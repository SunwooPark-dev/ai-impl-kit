from typing import Dict
from ai_impl_kit.runtime.choreography import Choreography

class ChoreographyVisualizer:
    @staticmethod
    def render_ascii_graph(choreography: Choreography, current_states: Dict[str, str]) -> str:
        """
        Renders a beautifully structured, premium box-art representation
        of the Choreography pipeline DAG and current node statuses.
        """
        header = "┌──────────────────────────────────────────────┐"
        title  = "│    Choreography Execution Pipeline Graph    │"
        sep    = "├──────────────────────────────────────────────┤"
        footer = "└──────────────────────────────────────────────┘"
        
        status_symbols = {
            "PENDING": "⏳ [PENDING]  ",
            "RUNNING": "▶️ [RUNNING]  ",
            "COMPLETED": "✅ [COMPLETED]",
            "FAILED": "❌ [FAILED]   "
        }
        
        lines = []
        lines.append(header)
        lines.append(title)
        lines.append(sep)
        
        for node_id, node in choreography.nodes.items():
            state = current_states.get(node_id, "PENDING")
            symbol = status_symbols.get(state, "⏳ [PENDING]  ")
            
            dep_info = f" <- [{', '.join(node.dependencies)}]" if node.dependencies else " (Root)"
            node_str = f" {symbol} Node: {node_id} ({node.prompt_id}){dep_info}"
            
            # 박스 내부 여백을 위해 패딩 처리
            max_content_len = 44 # 박스 내부 가용 너비
            if len(node_str) > max_content_len:
                node_str = node_str[:max_content_len-3] + "..."
            
            padded_line = f"│ {node_str:<{max_content_len}} │"
            lines.append(padded_line)
            
        lines.append(footer)
        return "\n".join(lines)
