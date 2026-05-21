import argparse
import json
import os
import sys
from pathlib import Path
import asyncio

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.adapters.openai_adapter import OpenAIAdapter
from ai_impl_kit.adapters.anthropic_adapter import AnthropicAdapter

async def run_prompt_cli(prompt_id: str, inputs_json: str, provider: str):
    try:
        inputs = json.loads(inputs_json)
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON provided for inputs.")
        sys.exit(1)

    if provider == "openai":
        adapter = OpenAIAdapter()
    elif provider == "anthropic":
        adapter = AnthropicAdapter()
    else:
        adapter = MockAdapter(response_text='{"result": "mocked output for CLI run"}')

    templates_dir = ROOT / "src" / "ai_impl_kit" / "prompts" / "templates"
    pipeline = Pipeline(str(templates_dir), adapter)

    print(f"Executing '{prompt_id}' using {provider.upper()} provider...")
    try:
        result = await pipeline.execute(prompt_id, inputs)
        print("\n--- RAW OUTPUT ---")
        print(result.raw_output)
        print("\n--- PARSED OUTPUT ---")
        print(json.dumps(result.parsed_output, indent=2))
        print(f"\n[Duration: {result.duration_ms:.2f}ms | Tokens: {result.usage['total_tokens']}]")
    except Exception as e:
        print(f"ERROR: Execution failed. {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CLI entrypoint for AI Impl Kit prompt packs")
    parser.add_argument("prompt_id", help="The ID of the prompt pack (e.g., 'classification', 'drafting')")
    parser.add_argument("--inputs", required=True, help="JSON string of variables to inject into the template")
    parser.add_argument("--provider", choices=["mock", "openai", "anthropic"], default="mock", help="Which LLM provider to use")
    
    args = parser.parse_args()
    asyncio.run(run_prompt_cli(args.prompt_id, args.inputs, args.provider))

if __name__ == "__main__":
    main()
