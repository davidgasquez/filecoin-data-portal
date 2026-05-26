import { mkdir, readFile, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import path from "node:path";
import type { Attachment, Author } from "chat";

export const BOT_HOME = path.join(homedir(), ".pi", "agent", "telegram-bot");
const SESSIONS_ROOT = path.resolve(".sessions");

export type UserPaths = {
	root: string;
	workspace: string;
	sessions: string;
	incoming: string;
	profile: string;
};

export type StoredAttachment = {
	guestPath: string;
	name: string;
	mimeType?: string;
};

export function userPaths(userId: string): UserPaths {
	if (!/^\d+$/.test(userId)) throw new Error(`Invalid Telegram user id: ${userId}`);
	const root = path.join(SESSIONS_ROOT, userId);
	const workspace = path.join(root, "workspace");
	return {
		root,
		workspace,
		sessions: path.join(root, "sessions"),
		incoming: path.join(workspace, "incoming"),
		profile: path.join(root, "profile.json"),
	};
}

export async function ensureUserDirs(paths: UserPaths): Promise<void> {
	await mkdir(paths.workspace, { recursive: true });
	await mkdir(paths.sessions, { recursive: true });
	await mkdir(paths.incoming, { recursive: true });
}

export async function saveProfile(paths: UserPaths, author: Author): Promise<void> {
	await ensureUserDirs(paths);
	await writeFile(
		paths.profile,
		`${JSON.stringify(
			{
				telegramUserId: author.userId,
				userName: author.userName,
				fullName: author.fullName,
				updatedAt: new Date().toISOString(),
			},
			null,
			2,
		)}\n`,
		"utf8",
	);
}

export async function materializeAttachments(
	paths: UserPaths,
	messageId: string,
	attachments: Attachment[],
): Promise<StoredAttachment[]> {
	if (attachments.length === 0) return [];
	await mkdir(paths.incoming, { recursive: true });
	const stored: StoredAttachment[] = [];
	for (const [index, attachment] of attachments.entries()) {
		const data = await attachmentData(attachment);
		if (!data) continue;
		const name = sanitize(attachment.name || `attachment-${index + 1}`);
		const file = `${Date.now()}-${messageId}-${index + 1}-${name}`;
		await writeFile(path.join(paths.incoming, file), data);
		stored.push({ guestPath: `/workspace/incoming/${file}`, name, mimeType: attachment.mimeType });
	}
	return stored;
}

export async function loadSystemPrompt(): Promise<string> {
	return readFile(path.resolve("prompts/system.md"), "utf8");
}

async function attachmentData(attachment: Attachment): Promise<Buffer | undefined> {
	if (attachment.fetchData) return attachment.fetchData();
	if (attachment.data instanceof Buffer) return attachment.data;
	if (attachment.data instanceof Blob) return Buffer.from(await attachment.data.arrayBuffer());
	return undefined;
}

function sanitize(value: string): string {
	return value.replace(/[^0-9A-Za-z._-]+/g, "_") || "attachment";
}
