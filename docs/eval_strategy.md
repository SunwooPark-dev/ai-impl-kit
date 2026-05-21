# Evaluation & Golden Sync Strategy

To ensure reliability and prevent regressions, `ai-impl-kit` treats input/output fixtures as first-class citizens. We enforce a **Manual Golden Sync Protocol** (ADR 0004).

## The Evaluation Loop

1. **Define a Case**: Create a JSON file in `fixtures/cases/<prompt_id>/<case_name>.json`.
2. **Run Evaluations**: Execute the CLI runner.
   ```bash
   uv run python scripts/run_eval.py --provider mock
   ```
3. **Handle Diffs**: If the output diverges from the baseline (or if no baseline exists), the evaluation fails. The raw output is saved in `outputs/local/<prompt_id>/<case_name>.(md|json)`.
4. **Manual Sync**: Review the local output. If the change is expected or an improvement, promote it to a Golden Output.
   ```bash
   uv run python scripts/sync_golden.py --prompt <prompt_id> --case <case_name>
   ```
5. **Commit**: Commit the updated `fixtures/golden/...` files to version control.

## CI/CD Enforcement

In the CI pipeline, the `run_eval.py` script is executed. If *any* golden output differs from the current execution, the pipeline fails. Automatic updating of golden files in CI is strictly forbidden.
