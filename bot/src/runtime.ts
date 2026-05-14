import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import type { AgentSession, AuthStorage, ModelRegistry, ResourceLoader } from "@earendil-works/pi-coding-agent";
import {
	createAgentSession,
	DefaultResourceLoader,
	SessionManager,
	SettingsManager,
} from "@earendil-works/pi-coding-agent";
import type { FileUpload, Message, Thread } from "chat";
import { BOT_HOME, ensureUserDirs, materializeAttachments, saveProfile, type UserPaths } from "./fs.js";
import { logEvent } from "./log.js";
import { UserSandbox } from "./sandbox.js";

const IDLE_VM_MS = Number(process.env.TELEGRAM_PI_IDLE_VM_MS ?? 10 * 60 * 1000);
const MAX_REPLY_FILE_BYTES = Number(process.env.TELEGRAM_PI_MAX_REPLY_FILE_BYTES ?? 20 * 1024 * 1024);
const TOOL_NAMES = ["read", "write", "edit", "bash"];

type QueuedTurn = { thread: Thread; message: Message };

type RuntimeDeps = {
	authStorage: AuthStorage;
	modelRegistry: ModelRegistry;
	systemPrompt: string;
};

export class UserRuntime {
	private session?: AgentSession;
	private readonly sandbox: UserSandbox;
	private readonly queue: QueuedTurn[] = [];
	private running = false;
	private idleTimer?: ReturnType<typeof setTimeout>;

	constructor(
		private readonly userId: string,
		private readonly paths: UserPaths,
		private readonly deps: RuntimeDeps,
	) {
		this.sandbox = new UserSandbox(paths.workspace);
	}

	async handleMessage(thread: Thread, message: Message): Promise<void> {
		await saveProfile(this.paths, message.author);
		const command = parseCommand(message.text);
		if (command) {
			await this.handleCommand(thread, command);
			return;
		}
		this.queue.push({ thread, message });
		logEvent("turn.queued", { userId: this.userId, messageId: message.id, queueLength: this.queue.length });
		void this.processQueue();
	}

	async shutdown(): Promise<void> {
		if (this.idleTimer) clearTimeout(this.idleTimer);
		this.session?.dispose();
		await this.sandbox.close();
	}

	private async handleCommand(thread: Thread, command: string): Promise<void> {
		logEvent("runtime.command", { userId: this.userId, command });
		const handler = this.commands()[command];
		if (!handler) {
			await thread.post("Unknown command. Send /help.");
			return;
		}
		await handler(thread);
	}

	private commands(): Record<string, (thread: Thread) => Promise<void>> {
		const help = async (thread: Thread) => {
			await thread.post(HELP_TEXT);
		};
		return {
			start: help,
			help,
			status: async (thread) => {
				await thread.post(this.statusText());
			},
			stop: async (thread) => {
				if (!this.running || !this.session) {
					await thread.post("No active turn.");
					return;
				}
				await this.session.abort();
				await thread.post("Aborted current turn.");
			},
			new: async (thread) => {
				await this.abortIfRunning();
				await this.openSession("new");
				await thread.post("Started a fresh Pi session for this workspace.");
			},
			compact: async (thread) => {
				await this.abortIfRunning();
				const session = await this.openSession("continue");
				await thread.startTyping();
				await session.compact();
				await thread.post("Compacted current session.");
			},
			"reset-vm": async (thread) => {
				await this.abortIfRunning();
				await this.sandbox.reset();
				this.scheduleIdleClose();
				await thread.post("Restarted your Gondolin VM.");
			},
		};
	}

	private async processQueue(): Promise<void> {
		if (this.running) return;
		const turn = this.queue.shift();
		if (!turn) {
			this.scheduleIdleClose();
			return;
		}
		this.running = true;
		if (this.idleTimer) clearTimeout(this.idleTimer);
		try {
			await this.runTurn(turn);
		} finally {
			this.running = false;
			void this.processQueue();
		}
	}

	private async runTurn(turn: QueuedTurn): Promise<void> {
		const stopTyping = startTypingLoop(turn.thread);
		let text = "";
		let unsubscribe: (() => void) | undefined;
		try {
			logEvent("turn.start", {
				userId: this.userId,
				messageId: turn.message.id,
				userName: turn.message.author.userName,
				attachments: turn.message.attachments?.length ?? 0,
				queueLength: this.queue.length,
			});
			const session = await this.openSession("continue");
			unsubscribe = session.subscribe((event) => {
				if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
					text += event.assistantMessageEvent.delta;
				}
			});
			await session.prompt(await this.buildPrompt(turn.message));
			const reply = text.trim() || "Done.";
			const files = await replyFilesFromMarkdown(this.paths.workspace, reply);
			await postReply(turn.thread, reply, files);
			logEvent("turn.end", {
				userId: this.userId,
				messageId: turn.message.id,
				responseChars: reply.length,
				replyFiles: files.length,
			});
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			logEvent("turn.error", { userId: this.userId, messageId: turn.message.id, error: message });
			if (!message.toLowerCase().includes("aborted")) await turn.thread.post(`Error: ${message}`);
		} finally {
			unsubscribe?.();
			stopTyping();
		}
	}

	private async buildPrompt(message: Message): Promise<string> {
		const attachments = await materializeAttachments(this.paths, message.id, message.attachments ?? []);
		const lines = [
			`Telegram user ${message.author.userId} (${message.author.fullName}) says:`,
			"",
			message.text.trim(),
		];
		if (attachments.length > 0) {
			lines.push("", "Attachments:");
			for (const file of attachments) {
				lines.push(`- ${file.guestPath} (${file.name}${file.mimeType ? `, ${file.mimeType}` : ""})`);
			}
		}
		return lines.join("\n");
	}

	private async openSession(mode: "continue" | "new"): Promise<AgentSession> {
		if (mode === "continue" && this.session) return this.session;
		this.session?.dispose();
		await ensureUserDirs(this.paths);
		const settingsManager = SettingsManager.inMemory({});
		const resourceLoader = this.createResourceLoader(settingsManager);
		await resourceLoader.reload();
		const sessionManager =
			mode === "new"
				? SessionManager.create(this.paths.workspace, this.paths.sessions)
				: SessionManager.continueRecent(this.paths.workspace, this.paths.sessions);
		const { session } = await createAgentSession({
			cwd: this.paths.workspace,
			agentDir: BOT_HOME,
			authStorage: this.deps.authStorage,
			modelRegistry: this.deps.modelRegistry,
			settingsManager,
			resourceLoader,
			sessionManager,
			tools: TOOL_NAMES,
			customTools: this.sandbox.toolDefinitions(),
		});
		this.session = session;
		return session;
	}

	private createResourceLoader(settingsManager: SettingsManager): ResourceLoader {
		return new DefaultResourceLoader({
			cwd: this.paths.workspace,
			agentDir: BOT_HOME,
			settingsManager,
			noExtensions: true,
			noSkills: true,
			noPromptTemplates: true,
			noThemes: true,
			noContextFiles: true,
			systemPromptOverride: () => this.deps.systemPrompt,
			appendSystemPromptOverride: () => [],
		});
	}

	private async abortIfRunning(): Promise<void> {
		if (!this.running || !this.session) return;
		await this.session.abort();
		await this.session.agent.waitForIdle();
	}

	private statusText(): string {
		return [
			`User: ${this.userId}`,
			`Session: ${this.session?.sessionId ?? "not opened"}`,
			`Session file: ${this.session?.sessionFile ?? "not opened"}`,
			`VM: ${this.sandbox.isRunning() ? "running" : "stopped"}`,
			`Active turn: ${this.running ? "yes" : "no"}`,
			`Queued messages: ${this.queue.length}`,
		].join("\n");
	}

	private scheduleIdleClose(): void {
		if (this.running || this.queue.length > 0 || IDLE_VM_MS <= 0) return;
		if (this.idleTimer) clearTimeout(this.idleTimer);
		this.idleTimer = setTimeout(() => {
			void this.sandbox.close().catch(() => undefined);
		}, IDLE_VM_MS);
	}
}

const HELP_TEXT = [
	"Telegram Pi Bot (DM only)",
	"",
	"Commands:",
	"/start - initialize and show help",
	"/help - show help",
	"/status - show session/runtime status",
	"/stop - abort current turn",
	"/new - start a fresh Pi session",
	"/compact - compact current session",
	"/reset-vm - restart your Gondolin VM",
].join("\n");

function parseCommand(text: string): string | undefined {
	const first = text.trim().split(/\s+/, 1)[0] ?? "";
	const match = first.match(/^\/([a-z-]+)(?:@\w+)?$/i);
	return match?.[1]?.toLowerCase();
}

async function postReply(thread: Thread, markdown: string, files: FileUpload[]): Promise<void> {
	if (files.length === 0) {
		await thread.post({ markdown });
		return;
	}
	const cleanMarkdown = stripLocalFileLinks(markdown);
	if (cleanMarkdown) await thread.post({ markdown: cleanMarkdown });
	for (const file of files) {
		await thread.post({ markdown: "", files: [file] });
	}
}

async function replyFilesFromMarkdown(workspace: string, markdown: string): Promise<FileUpload[]> {
	const files: FileUpload[] = [];
	const seen = new Set<string>();
	for (const guestPath of workspaceMarkdownLinks(markdown)) {
		const hostPath = hostPathForGuest(workspace, guestPath);
		if (!hostPath || seen.has(hostPath)) continue;
		seen.add(hostPath);
		const info = await stat(hostPath).catch(() => undefined);
		if (!info?.isFile() || info.size > MAX_REPLY_FILE_BYTES) continue;
		files.push({
			data: await readFile(hostPath),
			filename: path.basename(hostPath),
			mimeType: mimeTypeForPath(hostPath),
		});
	}
	return files;
}

function workspaceMarkdownLinks(markdown: string): string[] {
	const links: string[] = [];
	const regex = /!?\[[^\]]*\]\((\/workspace\/[^)\s]+)\)/g;
	for (const match of markdown.matchAll(regex)) {
		const value = match[1];
		if (!value) continue;
		links.push(decodeURI(value));
	}
	return links;
}

function stripLocalFileLinks(markdown: string): string {
	return markdown
		.replace(/!\[([^\]]*)\]\((\/workspace\/[^)\s]+)\)/g, (_match, alt: string, guestPath: string) => {
			const label = alt.trim() || path.posix.basename(guestPath);
			return `Attached: ${label}`;
		})
		.replace(/\[([^\]]+)\]\((\/workspace\/[^)\s]+)\)/g, "$1")
		.trim();
}

function hostPathForGuest(workspace: string, guestPath: string): string | undefined {
	if (!guestPath.startsWith("/workspace/")) return undefined;
	const root = path.resolve(workspace);
	const hostPath = path.resolve(root, guestPath.slice("/workspace/".length));
	if (hostPath !== root && hostPath.startsWith(`${root}${path.sep}`)) return hostPath;
	return undefined;
}

function mimeTypeForPath(filePath: string): string | undefined {
	switch (path.extname(filePath).toLowerCase()) {
		case ".png":
			return "image/png";
		case ".jpg":
		case ".jpeg":
			return "image/jpeg";
		case ".gif":
			return "image/gif";
		case ".webp":
			return "image/webp";
		case ".csv":
			return "text/csv";
		case ".json":
			return "application/json";
		case ".pdf":
			return "application/pdf";
		default:
			return undefined;
	}
}

function startTypingLoop(thread: Thread): () => void {
	void thread.startTyping();
	const timer = setInterval(() => void thread.startTyping(), 4000);
	return () => clearInterval(timer);
}
