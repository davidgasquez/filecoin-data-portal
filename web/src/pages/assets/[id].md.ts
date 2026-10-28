import type { GetStaticPaths } from "astro"
import { datasetMarkdown, datasets } from "../../datasets"

export const getStaticPaths = (() => datasets.map((dataset) => ({ params: { id: dataset.id }, props: { dataset } }))) satisfies GetStaticPaths

export const GET = ({ props }: { props: { dataset: (typeof datasets)[number] } }) => new Response(datasetMarkdown(props.dataset))
