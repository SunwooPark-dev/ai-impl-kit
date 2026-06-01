# Contributing

First off, thank you for considering contributing to this repository! 

## Adding a Prompt Pack

Prompt packs help developers quickly implement robust AI features. To add a new prompt pack:

1. Create a new directory/module for your use case.
2. Provide a clear system prompt and user prompt structure.
3. Include default parameters (e.g., `temperature`, `max_tokens`) that work best for the use case.
4. Ensure the prompt pack is documented with expected inputs and outputs.

## Writing Fixture / Eval

Every prompt pack should be tested against an evaluation fixture to ensure its reliability across models and updates.

1. **Create a Fixture**: Add a test case JSON in `fixtures/cases/<use-case>/`. Define the input and the expected output or validation rules.
2. **Run Evals**: Use the provided script to run your fixture against the prompt pack.
   ```bash
   python scripts/run_eval.py <use-case> fixtures/cases/<use-case>/<new-fixture>.json
   ```
3. Ensure that your new fixture passes the basic evaluation criteria before opening a Pull Request.

## Pull Request Process

1. Fork the repo and create your branch from `main`.
2. Add tests (fixtures) for your changes.
3. Update the documentation, if applicable.
4. Open a Pull Request!
