import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

import uvicorn

# Support direct script execution without install.
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.adapters.openai_adapter import OpenAIAdapter
from ai_impl_kit.adapters.anthropic_adapter import AnthropicAdapter

app = FastAPI(title="AI Impl Kit API", description="Production-ready serving layer for Prompt Packs")

class ExecuteRequest(BaseModel):
    prompt_id: str
    inputs: Dict[str, Any]
    provider: str = "mock"

class ExecuteResponse(BaseModel):
    parsed_output: Any
    raw_output: str
    duration_ms: float
    usage: Dict[str, int]
    latency_sec: float = 0.0
    cost_usd: float = 0.0

def get_adapter(provider: str):
    if provider == "openai":
        return OpenAIAdapter()
    elif provider == "anthropic":
        return AnthropicAdapter()
    elif provider == "mock":
        # Note: In real serving, mock needs pre-defined expected outputs. 
        # Here we just pass an empty JSON object for structural demonstration.
        return MockAdapter(response_text='{"status": "mocked response"}')
    else:
        raise ValueError(f"Unknown provider: {provider}")

@app.post("/execute", response_model=ExecuteResponse)
async def execute_prompt(request: ExecuteRequest):
    try:
        adapter = get_adapter(request.provider)
        templates_dir = ROOT / "src" / "ai_impl_kit" / "prompts" / "templates"
        pipeline = Pipeline(str(templates_dir), adapter)
        
        result = await pipeline.execute(request.prompt_id, request.inputs)
        
        return ExecuteResponse(
            parsed_output=result.parsed_output,
            raw_output=result.raw_output,
            duration_ms=result.duration_ms,
            usage=result.usage,
            latency_sec=result.latency_sec,
            cost_usd=result.cost_usd
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting AI Impl Kit API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
