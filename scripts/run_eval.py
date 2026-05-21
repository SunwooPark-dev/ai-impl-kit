import argparse
import json
import os
import sys
from pathlib import Path
import asyncio

# Support direct script execution without install.
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.runtime.pipeline import Pipeline  # type: ignore
from ai_impl_kit.adapters.mock_adapter import MockAdapter  # type: ignore
from ai_impl_kit.adapters.openai_adapter import OpenAIAdapter  # type: ignore
from ai_impl_kit.adapters.anthropic_adapter import AnthropicAdapter  # type: ignore
from ai_impl_kit.adapters.gemini_adapter import GeminiAdapter  # type: ignore


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def resolve_golden_path(golden_dir: Path, prompt_id: str, case_stem: str) -> Path | None:
    md_path = golden_dir / prompt_id / f"{case_stem}.md"
    json_path = golden_dir / prompt_id / f"{case_stem}.json"
    if md_path.exists():
        return md_path
    if json_path.exists():
        return json_path
    return None


async def run_prompt_eval(prompt_id: str, case_path: Path, provider: str = "mock") -> int:
    cases_root = ROOT / "fixtures" / "cases"
    golden_root = ROOT / "fixtures" / "golden"

    resolved_case_path = case_path
    if not case_path.is_absolute():
        resolved_case_path = ROOT / case_path

    if not resolved_case_path.exists():
        print(f"ERROR: case file not found: {resolved_case_path}")
        return 1

    try:
        inputs = load_json(resolved_case_path)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in case file '{resolved_case_path}': {e}")
        return 1

    case_stem = resolved_case_path.stem
    golden_path = resolve_golden_path(golden_root, prompt_id, case_stem)
    if golden_path is None:
        print(f"ERROR: golden file for case '{case_stem}' not found under {golden_root}/{prompt_id}")
        return 1

    expected = load_text(golden_path)

    # Adapter setup
    if provider == "openai":
        try:
            adapter = OpenAIAdapter()
        except ValueError as e:
            print(f"ERROR: Cannot initialize OpenAIAdapter: {e}")
            return 1
    elif provider == "anthropic":
        try:
            adapter = AnthropicAdapter()
        except ValueError as e:
            print(f"ERROR: Cannot initialize AnthropicAdapter: {e}")
            return 1
    elif provider == "gemini":
        try:
            adapter = GeminiAdapter()
        except ValueError as e:
            print(f"ERROR: Cannot initialize GeminiAdapter: {e}")
            return 1
    else:
        # Mock adapter must return deterministic output for this run.
        adapter = MockAdapter(response_text=expected)
        
    templates_dir = ROOT / "src" / "ai_impl_kit" / "prompts" / "templates"
    pipeline = Pipeline(str(templates_dir), adapter)

    try:
        result = await pipeline.execute(prompt_id, inputs)
    except Exception as e:
        print(f"ERROR: execution failed: {e}")
        return 1

    actual = result.raw_output.strip().replace("\r\n", "\n")
    expected_norm = expected.replace("\r\n", "\n")

    if actual == expected_norm:
        print(f"PASS: {prompt_id}/{case_stem} (provider: {provider}) [Latency: {result.latency_sec:.2f}s | Cost: ${result.cost_usd:.5f}]")
        return 0

    print(f"FAIL: {prompt_id}/{case_stem} (provider: {provider}) [Latency: {result.latency_sec:.2f}s | Cost: ${result.cost_usd:.5f}]")
    print("expected:")
    print(expected_norm)
    print("actual:")
    print(actual)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ai-impl-kit eval for a prompt case")
    parser.add_argument("prompt_id", nargs="?", default="structured_extraction", help="Prompt ID in registry (default: structured_extraction)")
    parser.add_argument(
        "case_file",
        nargs="?",
        default="fixtures/cases/structured_extraction/basic.json",
        help="Case file path relative to repository root or absolute path"
    )
    parser.add_argument("--provider", choices=["mock", "openai", "anthropic", "gemini"], default="mock", help="Adapter provider to use (default: mock)")
    args = parser.parse_args()

    return asyncio.run(run_prompt_eval(args.prompt_id, Path(args.case_file), args.provider))


if __name__ == "__main__":
    raise SystemExit(main())
