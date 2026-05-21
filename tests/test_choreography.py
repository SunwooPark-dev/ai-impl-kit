import pytest
import sys
import os
import asyncio
import tempfile
import json
from pathlib import Path

# Add src to sys.path so we can import packages without installing them.
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.adapters.mock_adapter import MockAdapter
from ai_impl_kit.runtime.choreography import Choreography, ChoreographyNode
from ai_impl_kit.runtime.visualizer import ChoreographyVisualizer
from ai_impl_kit.evals.replay import ReplayHarness

def test_choreography_cycle_detection():
    # node_1 -> node_2 -> node_1 순환 생성
    adapter = MockAdapter()
    choreography = Choreography(templates_dir="src/ai_impl_kit/prompts/templates", default_adapter=adapter)
    
    node_1 = ChoreographyNode("node_1", "classification", dependencies=["node_2"])
    node_2 = ChoreographyNode("node_2", "summarization", dependencies=["node_1"])
    
    choreography.add_node(node_1).add_node(node_2)
    
    with pytest.raises(ValueError, match="Cycle detected"):
        choreography._topological_sort()

def test_choreography_missing_dependency():
    adapter = MockAdapter()
    choreography = Choreography(templates_dir="src/ai_impl_kit/prompts/templates", default_adapter=adapter)
    
    node_1 = ChoreographyNode("node_1", "classification", dependencies=["non_existent_node"])
    choreography.add_node(node_1)
    
    with pytest.raises(ValueError, match="does not exist"):
        choreography._topological_sort()

def test_choreography_topological_sort_success():
    adapter = MockAdapter()
    choreography = Choreography(templates_dir="src/ai_impl_kit/prompts/templates", default_adapter=adapter)
    
    node_1 = ChoreographyNode("node_1", "classification")
    node_2 = ChoreographyNode("node_2", "summarization", dependencies=["node_1"])
    node_3 = ChoreographyNode("node_3", "drafting", dependencies=["node_1", "node_2"])
    
    choreography.add_node(node_1).add_node(node_2).add_node(node_3)
    
    order = choreography._topological_sort()
    assert order == ["node_1", "node_2", "node_3"]

def test_choreography_async_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = os.path.join(tmpdir, "ledger.jsonl")
        
        # 1. Mock 어댑터 준비 (노드 성격에 맞게 적절한 JSON 및 마크다운 리턴되도록 구성)
        # classification -> json, summarization -> markdown
        mock_classification = MockAdapter('{"category": "test-category"}')
        mock_summarization = MockAdapter('# Summary\nThis is mock summary\n# Key Points\n- Point A')
        
        choreography = Choreography(
            templates_dir="src/ai_impl_kit/prompts/templates",
            default_adapter=mock_classification,
            ledger_path=ledger_path
        )
        
        node_1 = ChoreographyNode("node_1", "classification")
        node_2 = ChoreographyNode(
            "node_2", 
            "summarization", 
            adapter=mock_summarization,
            dependencies=["node_1"],
            input_mapper=lambda global_inputs, prev_outputs: {
                "text": f"Context: {prev_outputs['node_1'].get('category', 'unknown')}. Content: {global_inputs['text']}",
                "max_length": "100"
            }
        )
        
        choreography.add_node(node_1).add_node(node_2)
        
        # 비동기 실행 루프 구동
        states = {}
        def callback(node_id, state):
            states[node_id] = state
            
        result = asyncio.run(choreography.execute(
            global_inputs={"text": "Hello world", "categories": ["test-category"]},
            status_callback=callback
        ))
        
        # 검증
        assert len(result.node_results) == 2
        assert result.node_results["node_1"].parsed_output["category"] == "test-category"
        assert "This is mock summary" in result.node_results["node_2"].raw_output
        assert result.total_cost_usd == 0.0 # Mock 어댑터 비용은 0.0
        
        # 콜백 상태 전이 최종 검증
        assert states["node_1"] == "COMPLETED"
        assert states["node_2"] == "COMPLETED"
        
        # ASCII 비주얼라이저 검증
        ascii_graph = ChoreographyVisualizer.render_ascii_graph(choreography, states)
        assert "Choreography Execution Pipeline Graph" in ascii_graph
        assert "✅ [COMPLETED] Node: node_1" in ascii_graph
        assert "✅ [COMPLETED] Node: node_2" in ascii_graph
        
        # Ledger 파일 내용 검증
        assert os.path.exists(ledger_path)
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        assert len(lines) == 2
        assert lines[0]["node_id"] == "node_1"
        assert lines[1]["node_id"] == "node_2"
        assert lines[0]["parsed_output"]["category"] == "test-category"

        # 2. Replay Harness 검증
        harness = ReplayHarness(ledger_path)
        replay_adapter = harness.get_adapter()
        
        replay_choreography = Choreography(
            templates_dir="src/ai_impl_kit/prompts/templates",
            default_adapter=replay_adapter,
            ledger_path=os.path.join(tmpdir, "replay_ledger.jsonl")
        )
        
        # 동일한 노드 구성
        node_1_rep = ChoreographyNode("node_1", "classification")
        node_2_rep = ChoreographyNode(
            "node_2", 
            "summarization", 
            dependencies=["node_1"], 
            input_mapper=lambda global_inputs, prev_outputs: {
                "text": f"Context: {prev_outputs['node_1'].get('category', 'unknown')}. Content: {global_inputs['text']}",
                "max_length": "100"
            }
        )
        replay_choreography.add_node(node_1_rep).add_node(node_2_rep)
        
        replay_result = asyncio.run(replay_choreography.execute(
            global_inputs={"text": "Hello world", "categories": ["test-category"]}
        ))
        
        assert len(replay_result.node_results) == 2
        assert replay_result.node_results["node_1"].parsed_output["category"] == "test-category"
