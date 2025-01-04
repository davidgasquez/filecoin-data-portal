<script>
    import "@evidence-dev/tailwind/fonts.css";
    import "../app.css";
    import { EvidenceDefaultLayout } from "@evidence-dev/core-components";
    export let data;
</script>

<EvidenceDefaultLayout
    {data}
    logo="/icon.svg"
    homePageName="Overview"
    builtWithEvidence={false}
    fullWidth={true}
    hideBreadcrumbs={true}
    hideTOC={true}
    githubRepo="https://github.com/davidgasquez/filecoin-data-portal/"
>
    <slot slot="content" />
</EvidenceDefaultLayout>
