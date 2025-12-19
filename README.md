# RewriteForge

Text rewriting service with pluggable LLM and cache adapters.

## Quick Start

```bash
# Pull and run
docker run -p 8000:8000 ghcr.io/vasilgerginski/rewriteforge:latest

# Or with custom config
docker run -p 8000:8000 --env-file .env ghcr.io/vasilgerginski/rewriteforge:latest

# Test
curl -X POST http://localhost:8000/v1/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "style": "pirate"}'
```

## Local Development

```bash
# Install uv
pip install uv

# Create venv and install
uv venv
uv sync --group dev

# Run
uv run uvicorn rewriteforge.bootstrap:app --reload

# Test
uv run pytest

# E2E test (requires running container)
./scripts/e2e.sh

# Lint
uv run ruff check .
uv run ruff format .
```

**VS Code:** Select interpreter `.venv/bin/python` for Pylance to resolve imports.

## Configuration

All adapters are swappable via environment variables — just use the name:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `mock` | LLM provider name |
| `CACHE_BACKEND` | `memory` | Cache backend name |
| `LLM_API_KEY` | - | API key for LLM provider |

### Swap to Anthropic
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
```

### Swap to Redis
```bash
CACHE_BACKEND=redis
CACHE_REDIS_URL=redis://localhost:6379
```

### List Available Adapters
```python
from llm_adapters import LLMInterface
from cache_adapters import CacheInterface

print(LLMInterface.available())   # ['anthropic', 'openai', 'mock']
print(CacheInterface.available()) # ['memory', 'redis']
```

## API Endpoints

### POST /v1/rewrite
Rewrite text in a specified style.

**Request:**
```json
{
  "text": "Hello world",
  "style": "pirate"
}
```

**Response:**
```json
{
  "original": "Hello world",
  "rewritten": "[*pirate*] Hello world",
  "style": "pirate",
  "cached": false
}
```

### POST /v1/rewrite/stream
Streaming version with Server-Sent Events.

### GET /health
Health check endpoint.

## Design Decisions

1. **Auto-Registration via `__init_subclass__`**: Adapters register themselves by declaring `name = "provider"`. No factory updates, no entry points, no config files.

2. **Contract IS the Registry**: `LLMInterface.resolve("anthropic")` — the contract knows all its implementations.

3. **Laravel-inspired Structure**: Contracts, Providers, Service Container, App Factory pattern.

4. **Monorepo with Extractable Packages**: `llm-adapters` and `cache-adapters` are independently installable, ready for extraction to private PyPI.

5. **Streaming Support**: SSE endpoint for real-time token delivery.

## Adding a New Adapter

1. Create class with `name = "gemini"` extending `LLMInterface`
2. Set `LLM_PROVIDER=gemini`
3. Done. Zero code changes anywhere else.

```python
# Just add this file — it auto-registers
class GeminiAdapter(LLMInterface):
    name = "gemini"

    async def rewrite(self, text: str, style: str) -> str:
        ...
```