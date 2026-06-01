# Security Policy

## Reporting a Vulnerability

Please report any security vulnerabilities responsibly. Do not use the public issue tracker to report a vulnerability. 

Instead, please send a message to the repository owner or use GitHub's private vulnerability reporting feature.

## Secret Handling

### API Keys and `.env` Files

- **Never commit your `.env` file or any API keys directly to the repository.**
- Ensure that `.env` and other secret files are properly included in the `.gitignore` file.
- When running prompts and using provider adapters locally, handle your API keys securely by relying on environment variables.
- If an API key or a secret is exposed, immediately revoke it from the provider (e.g., OpenAI, Anthropic, etc.).
