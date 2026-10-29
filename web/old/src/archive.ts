import { query } from "./db"

// Frozen archive parameters. ARCHIVE_DATE is the UTC day the archived snapshot was published (the last daily run).
// It replaces "today" everywhere, so rebuilding from the same snapshot reproduces the same pages.
export const currentSiteUrl = "https://filecoindataportal.xyz"
export const archivedOn = process.env.ARCHIVE_DATE ?? "2026-10-28"
if (!/^\d{4}-\d{2}-\d{2}$/.test(archivedOn)) throw new Error(`ARCHIVE_DATE must be YYYY-MM-DD, got ${archivedOn}`)

// Latest observed day, separate from the archive date.
export const [{ observedThrough }] = await query(`
  SELECT strftime(max(date), '%Y-%m-%d') AS observedThrough FROM main.daily_network_metrics WHERE date < DATE '${archivedOn}'
`) as { observedThrough: string }[]

export const archiveNote = `Archived copy of the previous Filecoin Data Portal, frozen on ${archivedOn} with observations through ${observedThrough} and no longer updated. Pages, numbers, schemas, and samples are frozen; dataset download URLs point to the live data host and may be newer. Current site: ${currentSiteUrl}`
