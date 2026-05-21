import json
import os
from typing import Dict, Any, List, Optional
from ai_impl_kit.adapters.base import AIAdapter, AdapterResponse, PromptMessage, ExecuteOptions

class ReplayAdapter(AIAdapter):
    """
    An adapter that does not call any external APIs but instead plays back
    recorded responses from a choreography ledger matching execution orders.
    """
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.records: List[Dict[str, Any]] = []
        self._pointer = 0
        self._load_records()

    def _load_records(self):
        if not os.path.exists(self.ledger_path):
            return
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        self.records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    async def execute(
        self, 
        messages: List[PromptMessage], 
        model: Optional[str] = None,
        options: Optional[ExecuteOptions] = None
    ) -> AdapterResponse:
        """
        Retrieves the next record from the ledger for sequential replay mock response.
        """
        if self._pointer < len(self.records):
            rec = self.records[self._pointer]
            self._pointer += 1
            return AdapterResponse(
                content=rec["raw_output"],
                raw_response=rec.get("raw_output"),
                usage=rec.get("usage", {}),
                model=model or "replay-model",
                latency_sec=rec.get("latency_sec", 0.0),
                cost_usd=rec.get("cost_usd", 0.0)
            )
        
        # Fallback if no matching or remaining record is found
        return AdapterResponse(
            content='{"status": "replay_exhausted", "result": "no-more-records"}',
            raw_response=None,
            usage={},
            model="replay-model",
            latency_sec=0.0,
            cost_usd=0.0
        )

class ReplayHarness:
    """
    Replay Harness for offline evaluation and regression tests of Multi-Agent Choreography.
    """
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path

    def get_adapter(self) -> ReplayAdapter:
        return ReplayAdapter(self.ledger_path)
