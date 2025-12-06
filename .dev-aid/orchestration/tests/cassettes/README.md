# VCR Cassettes

This directory contains recorded HTTP interactions for testing API clients without making real API calls.

## What are Cassettes?

Cassettes are YAML files containing recorded HTTP request/response pairs. When tests run:
- **First run (with API keys)**: VCR records real API interactions to cassettes
- **Subsequent runs**: VCR replays responses from cassettes (no API calls, no cost)

## Security

**API keys are automatically sanitized** before recording. The VCR configuration in `vcr_config.py` strips:
- `Authorization` headers
- `x-api-key` headers
- `anthropic-api-key` headers
- `openai-api-key` headers

## Recording New Cassettes

1. Set environment variables with **real** API keys:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   export GOOGLE_API_KEY=...
   export OPENAI_API_KEY=sk-...
   ```

2. Delete existing cassettes (optional):
   ```bash
   rm tests/cassettes/*.yaml
   ```

3. Run VCR tests:
   ```bash
   pytest tests/test_api_clients_vcr.py -v
   ```

4. Verify cassettes were created:
   ```bash
   ls tests/cassettes/
   ```

5. **Review cassettes** to ensure no secrets leaked:
   ```bash
   grep -i "sk-ant\|sk-\|api.*key" tests/cassettes/*.yaml
   ```
   Should return NO matches!

6. Commit cassettes to repository:
   ```bash
   git add tests/cassettes/*.yaml
   git commit -m "test: add VCR cassettes for API client tests"
   ```

## Using Cassettes in CI

Once cassettes are committed:
- CI runs tests **without API keys**
- VCR replays responses from cassettes
- Tests are **fast** (no network calls)
- Tests are **free** (no API costs)
- Tests are **deterministic** (same response every time)

## Updating Cassettes

When API responses change or new tests are added:

1. Delete outdated cassettes
2. Re-record with real API keys
3. Review and commit

## Files

- `anthropic_simple_request.yaml` - Basic Anthropic API call
- `anthropic_long_context.yaml` - Large context window test
- `google_simple_request.yaml` - Basic Google Gemini call
- `openai_simple_request.yaml` - Basic OpenAI GPT call
- `cross_provider_consistency.yaml` - Multi-provider test

## Troubleshooting

### "No cassette found"
- Cassette doesn't exist yet. Run tests with API keys to record.

### "Request didn't match cassette"
- Request parameters changed. Re-record cassette.

### Tests fail in CI but pass locally
- Ensure cassettes are committed to the repository.
- Check that VCR is installed in CI: `pip install vcrpy==6.0.2`
