# Dockerfile
FROM python:3.15-rc-alpine3.23 AS builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy workspace files
COPY pyproject.toml ./
COPY packages/ packages/
COPY services/ services/

# Install dependencies
RUN uv pip install --system -e packages/llm-adapters -e packages/cache-adapters -e services/rewriteforge-api

# Production stage
FROM python:3.15-rc-alpine3.23

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

# Copy source code
COPY packages/ packages/
COPY services/ services/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "rewriteforge.bootstrap:app", "--host", "0.0.0.0", "--port", "8000"]
