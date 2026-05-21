import os
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Support direct script execution without install
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.runtime.pipeline import Pipeline
from ai_impl_kit.adapters.factory import get_adapter
from ai_impl_kit.evals.runner import EvalRunner
from ai_impl_kit.prompts.registry import registry

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Impl Kit - Evaluation Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: rgba(22, 29, 49, 0.65);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --accent-primary: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --success-color: #10b981;
            --success-gradient: linear-gradient(135deg, #059669 0%, #10b981 100%);
            --error-color: #ef4444;
            --error-gradient: linear-gradient(135deg, #dc2626 0%, #f87171 100%);
            --warning-color: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2.5rem;
            line-height: 1.5;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.15) 0%, transparent 40%);
            background-attachment: fixed;
        }

        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
        }

        header {
            max-width: 1200px;
            margin: 0 auto 3rem auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }

        header h1 {
            font-size: 2.25rem;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.025em;
        }

        .header-meta {
            text-align: right;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.3);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-gradient);
        }

        .stat-card.success::before {
            background: var(--success-gradient);
        }

        .stat-card.error::before {
            background: var(--error-gradient);
        }

        .stat-title {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2.5rem;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }

        .stat-sub {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        /* Main Section */
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .section-title span {
            background: var(--accent-gradient);
            width: 8px;
            height: 24px;
            display: inline-block;
            border-radius: 4px;
        }

        /* Prompt Groups */
        .prompt-group {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            margin-bottom: 2.5rem;
            overflow: hidden;
            backdrop-filter: blur(12px);
        }

        .prompt-header {
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .prompt-info h2 {
            font-size: 1.25rem;
            color: var(--text-main);
            margin-bottom: 0.25rem;
        }

        .prompt-info p {
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .prompt-meta {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            text-transform: uppercase;
        }

        .badge-version {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-main);
        }

        .badge-results {
            background: rgba(99, 102, 241, 0.15);
            color: var(--accent-primary);
        }

        /* Test Cases Table */
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            padding: 1rem 1.5rem;
            background: rgba(0, 0, 0, 0.15);
            font-weight: 600;
        }

        td {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--card-border);
            font-size: 0.875rem;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .case-name {
            font-weight: 500;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
        }

        .status-pill.pass {
            background: rgba(16, 185, 129, 0.12);
            color: var(--success-color);
        }

        .status-pill.fail {
            background: rgba(239, 68, 68, 0.12);
            color: var(--error-color);
        }

        .details-btn {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: var(--text-main);
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .details-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.3);
        }

        /* Accordion Panel */
        .details-row {
            display: none;
            background: rgba(0, 0, 0, 0.2);
        }

        .details-content {
            padding: 1.5rem;
            font-family: monospace;
            font-size: 0.8125rem;
            color: #d1d5db;
            overflow-x: auto;
            border-top: 1px dashed var(--card-border);
        }

        .details-box {
            background: #0d1117;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--card-border);
            margin-top: 0.5rem;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        .diff-added {
            color: #4ade80;
        }

        .diff-removed {
            color: #f87171;
        }

        .diff-header {
            color: #60a5fa;
        }
    </style>
</head>
<body>

    <header>
        <div>
            <h1>AI Impl Kit</h1>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem;">Evaluation Run Summary Dashboard</p>
        </div>
        <div class="header-meta">
            <p><strong>Provider:</strong> __PROVIDER__</p>
            <p><strong>Date:</strong> __DATE__</p>
        </div>
    </header>

    <div class="container">
        
        <!-- Stats Section -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Total Prompts</div>
                <div class="stat-value">__TOTAL_PROMPTS__</div>
                <div class="stat-sub">Registered packs</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Total Test Cases</div>
                <div class="stat-value">__TOTAL_CASES__</div>
                <div class="stat-sub">JSON configurations</div>
            </div>
            <div class="stat-card success">
                <div class="stat-title">Pass Rate</div>
                <div class="stat-value">__PASS_RATE__%</div>
                <div class="stat-sub">__PASSED_CASES__/__TOTAL_CASES__ checks succeeded</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Avg Latency</div>
                <div class="stat-value">__AVG_LATENCY__ ms</div>
                <div class="stat-sub">Across all executions</div>
            </div>
        </div>

        <h2 class="section-title"><span></span>Prompt Evaluations</h2>

        <!-- Prompt Groups -->
        __PROMPT_GROUPS_HTML__

    </div>

    <script>
        function toggleDetails(rowId) {
            const row = document.getElementById(rowId);
            if (row.style.display === "table-row") {
                row.style.display = "none";
            } else {
                row.style.display = "table-row";
            }
        }
    </script>
</body>
</html>
"""

async def run_all_evals(provider: str) -> Dict[str, Any]:
    cases_dir = ROOT / "fixtures" / "cases"
    golden_dir = ROOT / "fixtures" / "golden"
    templates_dir = ROOT / "src" / "ai_impl_kit" / "prompts" / "templates"
    
    # Initialize adapter
    adapter = get_adapter(provider)
    pipeline = Pipeline(str(templates_dir), adapter)
    runner = EvalRunner(pipeline, str(cases_dir), str(golden_dir))
    
    summary = {
        "provider": provider,
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompts": []
    }
    
    # Scan registered prompts
    prompt_ids = list(registry._prompts.keys())
    
    for prompt_id in prompt_ids:
        metadata = registry.get(prompt_id)
        if not metadata:
            continue
            
        results = await runner.run_prompt_evals(prompt_id)
        if not results:
            continue
            
        summary_results = []
        for r in results:
            # Colorize diff for HTML
            colored_diff = ""
            if r.diff:
                lines = r.diff.splitlines()
                processed = []
                for line in lines:
                    if line.startswith("+"):
                        processed.append(f'<span class="diff-added">{line}</span>')
                    elif line.startswith("-"):
                        processed.append(f'<span class="diff-removed">{line}</span>')
                    elif line.startswith("@@"):
                        processed.append(f'<span class="diff-header">{line}</span>')
                    else:
                        processed.append(line)
                colored_diff = "\\n".join(processed)
            
            summary_results.append({
                "case_name": r.case_name,
                "passed": r.passed,
                "contract_passed": r.contract_passed,
                "golden_passed": r.golden_passed,
                "duration_ms": r.duration_ms,
                "error_message": r.error_message,
                "diff": colored_diff,
                "raw_output": r.raw_output
            })
            
        summary["prompts"].append({
            "prompt_id": prompt_id,
            "purpose": metadata.purpose,
            "version": metadata.version,
            "results": summary_results
        })
        
    return summary

def generate_html(summary: Dict[str, Any]) -> str:
    total_prompts = len(summary["prompts"])
    total_cases = 0
    passed_cases = 0
    total_latency = 0.0
    
    prompt_groups_html = ""
    global_index = 0
    
    for prompt in summary["prompts"]:
        prompt_id = prompt["prompt_id"]
        purpose = prompt["purpose"]
        version = prompt["version"]
        results = prompt["results"]
        
        prompt_cases = len(results)
        prompt_passed = sum(1 for r in results if r["passed"])
        
        total_cases += prompt_cases
        passed_cases += prompt_passed
        
        table_rows_html = ""
        for r in results:
            global_index += 1
            case_name = r["case_name"]
            passed = r["passed"]
            latency = r["duration_ms"]
            total_latency += latency
            
            status_class = "pass" if passed else "fail"
            status_text = "PASS" if passed else "FAIL"
            
            # Show details button only if failed/has diff
            details_btn_html = ""
            details_row_html = ""
            
            if not passed:
                details_btn_html = f'<button class="details-btn" onclick="toggleDetails(\'row-det-{global_index}\')">Details</button>'
                
                error_msg = r["error_message"] or "Unknown Failure"
                diff_sec = ""
                if r["diff"]:
                    diff_sec = f'<h4>Unified Diff:</h4><div class="details-box">{r["diff"]}</div>'
                
                raw_out_sec = ""
                if r["raw_output"]:
                    raw_out_sec = f'<h4>Raw Output:</h4><div class="details-box">{r["raw_output"]}</div>'
                
                details_row_html = f"""
                <tr class="details-row" id="row-det-{global_index}">
                    <td colspan="4">
                        <div class="details-content">
                            <p style="color: var(--error-color); font-weight: 500; margin-bottom: 0.5rem;">Error: {error_msg}</p>
                            {diff_sec}
                            {raw_out_sec}
                        </div>
                    </td>
                </tr>
                """
                
            table_rows_html += f"""
            <tr>
                <td class="case-name">{case_name}</td>
                <td><span class="status-pill {status_class}">{status_text}</span></td>
                <td>{latency:.2f} ms</td>
                <td style="text-align: right;">{details_btn_html}</td>
            </tr>
            {details_row_html}
            """
            
        prompt_groups_html += f"""
        <div class="prompt-group">
            <div class="prompt-header">
                <div class="prompt-info">
                    <h2>{prompt_id}</h2>
                    <p>{purpose}</p>
                </div>
                <div class="prompt-meta">
                    <span class="badge badge-version">v{version}</span>
                    <span class="badge badge-results">{prompt_passed}/{prompt_cases} Passed</span>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Test Case</th>
                        <th>Status</th>
                        <th>Latency</th>
                        <th style="text-align: right;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>
        </div>
        """
        
    pass_rate = int((passed_cases / total_cases * 100)) if total_cases > 0 else 0
    avg_latency = int(total_latency / total_cases) if total_cases > 0 else 0
    
    html = HTML_TEMPLATE.replace("__PROVIDER__", summary["provider"].upper()) \
                         .replace("__DATE__", summary["date"]) \
                         .replace("__TOTAL_PROMPTS__", str(total_prompts)) \
                         .replace("__TOTAL_CASES__", str(total_cases)) \
                         .replace("__PASSED_CASES__", str(passed_cases)) \
                         .replace("__PASS_RATE__", str(pass_rate)) \
                         .replace("__AVG_LATENCY__", str(avg_latency)) \
                         .replace("__PROMPT_GROUPS_HTML__", prompt_groups_html)
    
    return html

async def main():
    parser = argparse.ArgumentParser(description="Generate Eval Dashboard HTML")
    parser.add_argument("--provider", choices=["mock", "openai", "anthropic", "gemini"], default="mock", help="Provider to run evaluations (default: mock)")
    args = parser.parse_args()
    
    print(f"Running evaluation dashboard compiler using provider: '{args.provider}'...")
    summary = await run_all_evals(args.provider)
    
    # Save JSON summary to outputs/reports/eval_results.json
    reports_dir = ROOT / "outputs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_path = reports_dir / "eval_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved evaluation JSON report to: {json_path}")
    
    # Generate HTML
    html_content = generate_html(summary)
    
    # Save HTML to public/dashboard.html
    public_dir = ROOT / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    html_path = public_dir / "dashboard.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated dashboard HTML in: {html_path}")

if __name__ == "__main__":
    asyncio.run(main())
