import pytest
import sys
from pathlib import Path

# Add src to sys.path so we can import packages without installing them.
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.evals.pricing import calculate_cost

def test_openai_pricing():
    # gpt-4o: Input $5.00/1M, Output $15.00/1M
    # Prompt: 10,000 tokens ($0.05), Completion: 5,000 tokens ($0.075) -> Total: $0.125
    assert calculate_cost("gpt-4o", 10000, 5000) == pytest.approx(0.125, rel=1e-5)

    # gpt-3.5-turbo: Input $0.50/1M, Output $1.50/1M
    # Prompt: 1,000,000 tokens ($0.5), Completion: 1,000,000 tokens ($1.5) -> Total: $2.00
    assert calculate_cost("gpt-3.5-turbo", 1000000, 1000000) == pytest.approx(2.00, rel=1e-5)

def test_anthropic_pricing():
    # claude-3-5-sonnet: Input $3.00/1M, Output $15.00/1M
    # Prompt: 50,000 tokens ($0.15), Completion: 10,000 tokens ($0.15) -> Total: $0.30
    assert calculate_cost("claude-3-5-sonnet", 50000, 10000) == pytest.approx(0.30, rel=1e-5)

def test_prefix_matching():
    # Matching with model version suffixes
    # gpt-4o-2024-05-13 should match gpt-4o rate
    assert calculate_cost("gpt-4o-2024-05-13", 10000, 5000) == pytest.approx(0.125, rel=1e-5)

    # claude-3-5-sonnet-20241022 should match claude-3-5-sonnet rate
    assert calculate_cost("claude-3-5-sonnet-20241022", 50000, 10000) == pytest.approx(0.30, rel=1e-5)

def test_unknown_models():
    # local or unknown models should compute to 0.0 USD
    assert calculate_cost("gemma", 10000, 5000) == 0.0
    assert calculate_cost("mock-model", 9999, 9999) == 0.0
    assert calculate_cost("", 1000, 1000) == 0.0
