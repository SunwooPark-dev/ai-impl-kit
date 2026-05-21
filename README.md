# AI Impl Kit

Ship AI features faster with implementation-ready prompt packs, provider adapters, and validation fixtures.

![Status](https://img.shields.io/badge/status-MVP%20Ready-brightgreen)

## Included Use Cases

1.  **Structured Extraction:** Extract strictly formatted JSON from unstructured text.
2.  **Classification / Routing:** Classify intents or categories from user inputs.
3.  **Summarization:** Summarize large documents with constraints.
4.  **Drafting / Rewrite:** Adjust tone and polish rough drafts.

## Quickstart
\`\`\`bash
pip install -e .[dev]
python scripts/run_eval.py structured_extraction fixtures/cases/structured_extraction/basic.json
\`\`\`

## Guides

-   [Customization Guide](docs/customization_guide.md): Learn how to add your own prompt templates, update the registry, and run evaluations.
-   **TypeScript Starter:** See `examples/typescript-starter` for an example of how to consume this package in a Node.js environment.
