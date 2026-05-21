import os
import json
import difflib
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.runtime.validator import ContractViolationError

@dataclass
class EvalResult:
    case_name: str
    passed: bool
    contract_passed: bool
    golden_passed: bool
    error_message: Optional[str] = None
    diff: Optional[str] = None
    raw_output: Optional[str] = None
    duration_ms: float = 0.0

class EvalRunner:
    def __init__(self, pipeline: Pipeline, cases_dir: str, golden_dir: str):
        self.pipeline = pipeline
        self.cases_dir = cases_dir
        self.golden_dir = golden_dir

    async def run_prompt_evals(self, prompt_id: str) -> List[EvalResult]:
        """Runs all test cases for a given prompt_id."""
        prompt_cases_dir = os.path.join(self.cases_dir, prompt_id)
        prompt_golden_dir = os.path.join(self.golden_dir, prompt_id)
        
        if not os.path.exists(prompt_cases_dir):
            return []

        results = []
        for filename in os.listdir(prompt_cases_dir):
            if not filename.endswith(".json"):
                continue
                
            case_name = filename[:-5]
            case_path = os.path.join(prompt_cases_dir, filename)
            
            with open(case_path, 'r', encoding='utf-8-sig') as f:
                inputs = json.load(f)
                
            results.append(await self._run_single_case(prompt_id, case_name, inputs, prompt_golden_dir))
            
        return results

    async def _run_single_case(self, prompt_id: str, case_name: str, inputs: Dict[str, Any], golden_dir: str) -> EvalResult:
        try:
            # 1. Execute Pipeline (which validates the Output Contract implicitly due to Fail-Fast)
            result = await self.pipeline.execute(prompt_id, inputs)
            
            # 2. Contract passed if we reached here
            contract_passed = True
            
            # 3. Check against Golden Output
            golden_passed = True
            diff_text = None
            error_msg = None
            
            # Expected golden file can be .md or .json. We compare exact string content.
            golden_path_md = os.path.join(golden_dir, f"{case_name}.md")
            golden_path_json = os.path.join(golden_dir, f"{case_name}.json")
            
            golden_content = None
            if os.path.exists(golden_path_md):
                with open(golden_path_md, 'r', encoding='utf-8') as f:
                    golden_content = f.read()
            elif os.path.exists(golden_path_json):
                with open(golden_path_json, 'r', encoding='utf-8') as f:
                    golden_content = f.read()
            
            if golden_content is not None:
                # Compare exact string (normalize newlines)
                actual_normalized = result.raw_output.replace('\r\n', '\n').strip()
                golden_normalized = golden_content.replace('\r\n', '\n').strip()
                
                if actual_normalized != golden_normalized:
                    golden_passed = False
                    error_msg = "Golden Output Differs"
                    
                    # Generate Diff
                    actual_lines = actual_normalized.splitlines(keepends=True)
                    golden_lines = golden_normalized.splitlines(keepends=True)
                    diff = difflib.unified_diff(golden_lines, actual_lines, fromfile='golden', tofile='actual')
                    diff_text = ''.join(diff)
            else:
                # No golden exists yet. Treat as failure requiring sync.
                golden_passed = False
                error_msg = "No Golden Output Found"

            return EvalResult(
                case_name=case_name,
                passed=contract_passed and golden_passed,
                contract_passed=contract_passed,
                golden_passed=golden_passed,
                error_message=error_msg,
                diff=diff_text,
                raw_output=result.raw_output,
                duration_ms=result.duration_ms
            )
            
        except ContractViolationError as e:
            return EvalResult(
                case_name=case_name,
                passed=False,
                contract_passed=False,
                golden_passed=False,
                error_message=f"Contract Violation: {e}"
            )
        except Exception as e:
            return EvalResult(
                case_name=case_name,
                passed=False,
                contract_passed=False,
                golden_passed=False,
                error_message=f"Execution Error: {e}"
            )
