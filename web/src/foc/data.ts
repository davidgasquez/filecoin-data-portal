import { readFileSync, readdirSync } from 'node:fs'
import { resolve, join } from 'node:path'

// Generated locally by scripts/foc.py; never query the database from the browser.
const root = resolve('.foc/data')
export const readFoc = (file: string): any => JSON.parse(readFileSync(join(root, file), 'utf8'))
export const labels = readFoc('labels.json')
export const overview = readFoc('overview.json')
export const coverage = readFoc('coverage.json')
export interface FocRoute { route: string | undefined; kind: string; key?: string; file: string }
export const routes: FocRoute[] = [
  ...['overview', 'providers', 'datasets', 'rails', 'clients', 'operators', 'solstice'].map(kind => ({
    route: kind === 'overview' ? undefined : kind, kind, file: `${kind}.json`,
  })),
  ...Object.entries({ p: 'provider', ds: 'dataset', r: 'rail', a: 'address' }).flatMap(([folder, kind]) =>
    readdirSync(join(root, folder)).filter(file => file.endsWith('.json')).sort().map(file => {
      const key = file.slice(0, -5)
      return { route: `${kind}/${key}`, kind, key, file: `${folder}/${file}` }
    })),
]
