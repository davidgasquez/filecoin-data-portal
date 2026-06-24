import { readFile } from "node:fs/promises";
import { Chat, type Message, type Thread } from "chat";
import { createMemoryState } from "@chat-adapter/state-memory";
import { createTelegramAdapter } from "@chat-adapter/telegram";
import { ensureGuestAssets, hasGuestAssets } from "@earendil-works/gondolin";
import { AuthStorage, ModelRegistry } from "@earendil-works/pi-coding-agent";
import { loadSystemPrompt, userPaths } from "./fs.js";
import { logEvent } from "./log.js";
import { UserRuntime } from "./runtime.js";

const botToken = await readBotToken();
const systemPrompt = await loadSystemPrompt();

if (!hasGuestAssets()) await ensureGuestAssets();

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);
if ((await modelRegistry.getAvailable()).length === 0) {
	throw new Error("No configured Pi model credentials found. Configure a provider API key before starting the bot.");
}

const runtimes = new Map<string, UserRuntime>();
const telegram = createTelegramAdapter({ mode: "polling", botToken });
const bot = new Chat({
	userName: process.env.TELEGRAM_BOT_USERNAME || "pi",
	adapters: { telegram },
	state: createMemoryState(),
	logger: "info",
});

bot.onNewMention(async (thread, message) => {
	if (!thread.isDM) {
		await thread.post("This bot is DM-only.");
		return;
	}
	await thread.subscribe();
	await routeMessage(thread, message);
});

bot.onSubscribedMessage(routeMessage);

await bot.initialize();
logEvent("bot.ready", { botUserName: telegram.userName });

process.on("SIGINT", () => void shutdown("SIGINT"));
process.on("SIGTERM", () => void shutdown("SIGTERM"));

async function routeMessage(thread: Thread, message: Message): Promise<void> {
	if (!thread.isDM) return;
	logEvent("telegram.message", {
		userId: message.author.userId,
		userName: message.author.userName,
		messageId: message.id,
		text: message.text,
		attachments: message.attachments?.length ?? 0,
	});
	try {
		await getRuntime(message.author.userId).handleMessage(thread, message);
	} catch (error) {
		const text = error instanceof Error ? error.message : String(error);
		logEvent("route.error", { userId: message.author.userId, error: text });
		await thread.post(`Error: ${text}`);
	}
}

function getRuntime(userId: string): UserRuntime {
	const existing = runtimes.get(userId);
	if (existing) return existing;
	const runtime = new UserRuntime(userId, userPaths(userId), { authStorage, modelRegistry, systemPrompt });
	runtimes.set(userId, runtime);
	logEvent("runtime.created", { userId });
	return runtime;
}

async function shutdown(signal: string): Promise<void> {
	logEvent("bot.shutdown", { signal });
	await Promise.all([...runtimes.values()].map((r) => r.shutdown()));
	await bot.shutdown();
	process.exit(0);
}

async function readBotToken(): Promise<string> {
	const raw = await readFile("telegram.token.json", "utf8");
	const data = JSON.parse(raw) as { botToken?: unknown };
	const token = typeof data.botToken === "string" ? data.botToken.trim() : "";
	if (!token) throw new Error('telegram.token.json must contain { "botToken": "..." }');
	return token;
}
