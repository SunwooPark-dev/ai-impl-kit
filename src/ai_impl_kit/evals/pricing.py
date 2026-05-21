# pricing.py
from typing import Dict, Tuple

# Pricing database: Model identifier -> (Input cost per 1M tokens in USD, Output cost per 1M tokens in USD)
MODEL_PRICING: Dict[str, Tuple[float, float]] = {
    "gpt-4o": (5.00, 15.00),
    "gpt-4o-mini": (0.150, 0.600),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "claude-3-5-sonnet": (3.00, 15.00),
    "claude-3-opus": (15.00, 75.00),
    "claude-3-haiku": (0.25, 1.25),
}

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculates estimated API cost in USD based on model pricing rates.
    Supports prefix matching to accommodate model version tags (e.g. gpt-4o-2024-05-13).
    """
    if not model:
        return 0.0

    model_lower = model.lower()

    # Search for matching prefix/key in pricing database
    matched_rate = (0.0, 0.0)
    for key, rate in MODEL_PRICING.items():
        if model_lower.startswith(key):
            matched_rate = rate
            break

    input_cost = (prompt_tokens / 1_000_000.0) * matched_rate[0]
    output_cost = (completion_tokens / 1_000_000.0) * matched_rate[1]
    
    return round(input_cost + output_cost, 7)
