# Customization Guide

Welcome to the AI Impl Kit! This guide will help you customize prompt packs and create your own.

## 1. Directory Structure

- `src/ai_impl_kit/prompts/templates`: Store your `.system.md` and `.user.md` files here.
- `src/ai_impl_kit/prompts/registry.py`: Register the metadata (inputs and expected outputs) for your new prompts.
- `fixtures/cases`: Store JSON files representing inputs to your prompts.
- `fixtures/golden`: Store the expected outputs (JSON or Markdown) for regression testing.

## 2. Creating a New Prompt Pack

1. **Write Templates:** Create `my_prompt.system.md` and `my_prompt.user.md`. Use `{{ variable_name }}` for placeholders.
2. **Register Metadata:** Edit `registry.py` and add a new `PromptMetadata` entry. Ensure you define an `OutputContract` (e.g., `json_schema` or `markdown_headers`).
3. **Create Fixtures:** Create a basic input case in `fixtures/cases/my_prompt/basic.json` and its expected output in `fixtures/golden/my_prompt/basic.json` (or `.md`).
4. **Evaluate:** Run the evaluation script locally to ensure it works with the Mock adapter.
   ```bash
   python scripts/run_eval.py my_prompt fixtures/cases/my_prompt/basic.json
   ```

## 3. Running with Real Providers

Once you have customized your prompts, test them against real LLMs.

1. Copy `.env.example` to `.env`.
2. Add your API keys (e.g., `OPENAI_API_KEY`).
3. Run the evaluation specifying the provider:
   ```bash
   python scripts/run_eval.py my_prompt fixtures/cases/my_prompt/basic.json --provider openai
   ```
