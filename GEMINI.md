# GEMINI.md - AI Impl Kit Project Rules

This project strictly follows the **Agentic Engineering Master Process v0.1** defined in the root `../GEMINI.md`.

## Core Mandates

1. **Prompt Isolation:** Prompts must remain in `src/ai_impl_kit/prompts/templates` and should never be hardcoded in logic.
2. **Adapter Neutrality:** Business logic must depend on the `AIAdapter` protocol, not specific provider SDKs.
3. **Fixture-Driven Development:** Any bug fix or feature must include a corresponding fixture in `fixtures/cases` and a verified output in `fixtures/golden`.
4. **Hardening:** Never commit `.env` or any file containing real API keys. Use `.env.example` for documentation.

## Verification Checklist

- [ ] `pytest` passes.
- [ ] `ruff check .` passes.
- [ ] `mypy src` passes.
- [ ] `python scripts/run_eval.py` shows 100% pass rate or explicitly approved diffs.

## Architecture Decisions (ADRs)

See `docs/adr/` for major architectural decisions.
