# ruff: noqa
import asyncio
import time
import json
import os
from typing import Dict, Any, List, Optional, Callable

from ai_impl_kit.adapters.base import AIAdapter, ExecuteOptions
from ai_impl_kit.runtime.pipeline import Pipeline, PipelineExecutionResult

class ChoreographyNode:
    def __init__(
        self,
        node_id: str,
        prompt_id: str,
        adapter: Optional[AIAdapter] = None,
        input_mapper: Optional[Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = None,
        dependencies: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None
    ):
        self.node_id = node_id
        self.prompt_id = prompt_id
        self.adapter = adapter
        self.dependencies = dependencies or []
        self.tools = tools or []
        
        # 기본 인풋 매퍼: 글로벌 인풋과 이전 노드들의 parsed_output 병합
        self.input_mapper = input_mapper or self._default_input_mapper

    def _default_input_mapper(self, global_inputs: Dict[str, Any], prev_outputs: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**global_inputs}
        for dep_id, output in prev_outputs.items():
            if isinstance(output, dict):
                merged = {**merged, **output}
            else:
                merged[dep_id] = output
        return merged

class ChoreographyExecutionResult:
    def __init__(
        self,
        node_results: Dict[str, PipelineExecutionResult],
        total_duration_ms: float,
        total_cost_usd: float,
        ledger_path: str
    ):
        self.node_results = node_results
        self.total_duration_ms = total_duration_ms
        self.total_cost_usd = total_cost_usd
        self.ledger_path = ledger_path

class Choreography:
    def __init__(
        self, 
        templates_dir: str, 
        default_adapter: AIAdapter, 
        ledger_path: str = "outputs/choreography_ledger.jsonl"
    ):
        self.templates_dir = templates_dir
        self.default_adapter = default_adapter
        self.ledger_path = ledger_path
        self.nodes: Dict[str, ChoreographyNode] = {}

    def add_node(self, node: ChoreographyNode) -> 'Choreography':
        self.nodes[node.node_id] = node
        return self

    def _topological_sort(self) -> List[str]:
        in_degree = {node_id: 0 for node_id in self.nodes}
        adj = {node_id: [] for node_id in self.nodes}

        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    raise ValueError(f"Dependency '{dep}' of node '{node_id}' does not exist.")
                adj[dep].append(node_id)
                in_degree[node_id] += 1

        queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError("Cycle detected in Choreography dependencies!")
        return order

    def _write_to_ledger(self, node: ChoreographyNode, inputs: Dict[str, Any], result: PipelineExecutionResult):
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        ledger_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "node_id": node.node_id,
            "prompt_id": node.prompt_id,
            "registered_tools": [t.name for t in node.tools],
            "inputs": inputs,
            "raw_output": result.raw_output,
            "parsed_output": result.parsed_output,
            "latency_sec": result.latency_sec,
            "cost_usd": result.cost_usd,
            "duration_ms": result.duration_ms,
            "usage": result.usage
        }
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")

    async def execute(
        self, 
        global_inputs: Dict[str, Any], 
        options: Optional[ExecuteOptions] = None,
        status_callback: Optional[Callable[[str, str], None]] = None
    ) -> ChoreographyExecutionResult:
        # 1. 의존성 사이클 체크 및 순서 획득
        order = self._topological_sort()
        
        completed_nodes: Dict[str, PipelineExecutionResult] = {}
        node_events: Dict[str, asyncio.Event] = {node_id: asyncio.Event() for node_id in self.nodes}
        
        start_time = time.time()
        
        # 모든 노드를 PENDING으로 상태 업데이트
        if status_callback:
            for node_id in self.nodes:
                status_callback(node_id, "PENDING")

        async def run_node(node_id: str):
            node = self.nodes[node_id]
            # 2. 선행 의존성 완료될 때까지 대기
            for dep in node.dependencies:
                await node_events[dep].wait()

            if status_callback:
                status_callback(node_id, "RUNNING")
                
            try:
                # 3. 데이터 Handoff 매핑
                prev_outputs = {dep: completed_nodes[dep].parsed_output for dep in node.dependencies}
                node_inputs = node.input_mapper(global_inputs, prev_outputs)
                
                # 4. 개별 노드 전용 Tools 옵션 설정
                if options:
                    node_options = options.model_copy(update={"tools": node.tools})
                else:
                    node_options = ExecuteOptions(tools=node.tools)
                
                # 5. 실행용 Pipeline 준비 및 수행
                adapter = node.adapter or self.default_adapter
                pipeline = Pipeline(self.templates_dir, adapter)
                
                result = await pipeline.execute(node.prompt_id, node_inputs, node_options)
                completed_nodes[node_id] = result
                
                # 6. Ledger 실시간 저장
                self._write_to_ledger(node, node_inputs, result)
                
                if status_callback:
                    status_callback(node_id, "COMPLETED")
            except Exception as e:
                if status_callback:
                    status_callback(node_id, "FAILED")
                raise e
            finally:
                # 다음 노드를 위해 완료 처리 (Fail-Fast 시에도 대기 해제)
                node_events[node_id].set()

        # 7. 모든 노드 병렬 실행 예약
        tasks = [asyncio.create_task(run_node(node_id)) for node_id in self.nodes]  # noqa: F841
        await asyncio.gather(*tasks)
        
        total_duration_ms = (time.time() - start_time) * 1000
        total_cost_usd = sum(res.cost_usd for res in completed_nodes.values())
        
        return ChoreographyExecutionResult(
            node_results=completed_nodes,
            total_duration_ms=total_duration_ms,
            total_cost_usd=total_cost_usd,
            ledger_path=self.ledger_path
        )

