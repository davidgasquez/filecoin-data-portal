import path from "node:path";
import {
	createBashToolDefinition,
	createEditToolDefinition,
	createReadToolDefinition,
	createWriteToolDefinition,
	type ToolDefinition,
} from "@earendil-works/pi-coding-agent";
import { RealFSProvider, VM } from "@earendil-works/gondolin";

const GUEST_WORKSPACE = "/workspace";
const IMAGE_MIME: Record<string, string> = {
	".png": "image/png",
	".jpg": "image/jpeg",
	".jpeg": "image/jpeg",
	".gif": "image/gif",
	".webp": "image/webp",
};

export class UserSandbox {
	private vm?: VM;
	private starting?: Promise<VM>;

	constructor(private readonly workspaceDir: string) {}

	isRunning(): boolean {
		return this.vm !== undefined;
	}

	async start(): Promise<VM> {
		if (this.vm) return this.vm;
		if (this.starting) return this.starting;
		this.starting = (async () => {
			let vm: VM | undefined;
			try {
				vm = await VM.create({
					sessionLabel: `telegram-pi ${this.workspaceDir}`,
					vfs: { mounts: { [GUEST_WORKSPACE]: new RealFSProvider(this.workspaceDir) } },
				});
				const uv = await vm.exec("command -v uv >/dev/null 2>&1");
				if (!uv.ok) throw new Error("Gondolin image is missing uv");
				this.vm = vm;
				return vm;
			} catch (error) {
				await vm?.close().catch(() => undefined);
				throw error;
			} finally {
				this.starting = undefined;
			}
		})();
		return this.starting;
	}

	async reset(): Promise<void> {
		await this.close();
		await this.start();
	}

	async close(): Promise<void> {
		const vm = this.vm;
		this.vm = undefined;
		this.starting = undefined;
		if (vm) await vm.close();
	}

	toolDefinitions(): Array<ToolDefinition<any, any, any>> {
		const fs = async () => (await this.start()).fs;
		const resolve = (input: string) => resolveGuestPath(input);
		return [
			createReadToolDefinition(GUEST_WORKSPACE, {
				operations: {
					readFile: async (p) => (await fs()).readFile(resolve(p)),
					access: async (p) => {
						await (await fs()).access(resolve(p));
					},
					detectImageMimeType: async (p) => IMAGE_MIME[path.posix.extname(resolve(p)).toLowerCase()] ?? null,
				},
			}),
			createWriteToolDefinition(GUEST_WORKSPACE, {
				operations: {
					writeFile: async (p, content) => {
						await (await fs()).writeFile(resolve(p), content);
					},
					mkdir: async (p) => {
						await (await fs()).mkdir(resolve(p), { recursive: true });
					},
				},
			}),
			createEditToolDefinition(GUEST_WORKSPACE, {
				operations: {
					readFile: async (p) => (await fs()).readFile(resolve(p)),
					writeFile: async (p, content) => {
						await (await fs()).writeFile(resolve(p), content);
					},
					access: async (p) => {
						await (await fs()).access(resolve(p));
					},
				},
			}),
			createBashToolDefinition(GUEST_WORKSPACE, {
				operations: {
					exec: async (command, cwd, options) => {
						const vm = await this.start();
						const timeoutMs = options.timeout ? options.timeout * 1000 : undefined;
						const signals = [options.signal, timeoutMs ? AbortSignal.timeout(timeoutMs) : undefined].filter(
							(s): s is AbortSignal => s !== undefined,
						);
						const signal = signals.length > 1 ? AbortSignal.any(signals) : signals[0];
						try {
							const proc = vm.exec(["/bin/bash", "-lc", command], {
								cwd: resolve(cwd),
								signal,
								stdout: "pipe",
								stderr: "pipe",
							});
							for await (const chunk of proc.output()) options.onData(chunk.data);
							const result = await proc;
							return { exitCode: result.exitCode };
						} catch (error) {
							if (options.signal?.aborted) throw new Error("aborted");
							if (signal?.aborted && timeoutMs) throw new Error(`timeout:${options.timeout}`);
							throw error;
						}
					},
				},
			}),
		];
	}
}

function resolveGuestPath(input: string): string {
	const value = input.trim();
	if (!value) throw new Error("Path must not be empty");
	const base = value.startsWith("/") ? "/" : GUEST_WORKSPACE;
	const resolved = path.posix.resolve(base, value);
	if (resolved !== GUEST_WORKSPACE && !resolved.startsWith(`${GUEST_WORKSPACE}/`)) {
		throw new Error(`Path is outside /workspace: ${input}`);
	}
	return resolved;
}
