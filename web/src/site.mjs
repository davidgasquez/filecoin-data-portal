// The portal (default) and Filecoin Onchain Cloud explorer (FDP_SITE=foc).
// The explorer links to the portal by origin; the portal does not advertise the explorer.
const site = process.env.FDP_SITE || 'portal'
if (site !== 'portal' && site !== 'foc') throw new Error(`FDP_SITE must be portal or foc, not ${site}`)
export const explorer = site === 'foc'
export const outDir = explorer ? 'dist-foc' : 'dist'

// Production origins by default; previews and local servers set both.
export const PORTAL = 'https://filecoindataportal.xyz'
export const EXPLORER = 'https://foc.filecoindataportal.xyz'
export const portalUrl = new URL(process.env.SITE_URL || PORTAL).origin
export const focUrl = new URL(process.env.FOC_URL || EXPLORER).origin
export const origin = explorer ? focUrl : portalUrl
export const production = origin === (explorer ? EXPLORER : PORTAL)
/** @param {string} path */
export const portalHref = (path) => explorer ? portalUrl + path : path

export const repoUrl = 'https://github.com/davidgasquez/filecoin-data-portal'
// Top-level sections: the portal header, and the explorer's portal menu.
export const portal = [[portalHref('/numbers'), 'Numbers'], ...(explorer ? [['/', 'Filecoin Onchain Cloud']] : []), [portalHref('/datasets'), 'Datasets'], [portalHref('/docs'), 'Docs']]
