export function logEvent(event: string, fields: Record<string, unknown> = {}): void {
	console.log(JSON.stringify({ at: new Date().toISOString(), event, ...fields }));
}
