#!/bin/bash

set -e

echo "🚀 Starting E2E test..."
echo ""

# Show config
LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2 || echo "mock")
echo "📋 Config: LLM_PROVIDER=$LLM_PROVIDER"
echo ""

# Build and start container
echo "📦 Building Docker image..."
docker build -t rewriteforge-test . -q

echo "🐳 Starting container..."
CONTAINER_ID=$(docker run -d -p 8001:8000 --env-file .env rewriteforge-test)

cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    docker stop $CONTAINER_ID > /dev/null 2>&1 || true
    docker rm $CONTAINER_ID > /dev/null 2>&1 || true
}
trap cleanup EXIT

# Wait for service
echo "⏳ Waiting for service..."
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null; then
        echo "   Service is up!"
        break
    fi
    sleep 1
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TEST 1: Health check"
echo "═══════════════════════════════════════════════════════════════"
echo "→ GET /health"
HEALTH=$(curl -s http://localhost:8001/health)
echo "← $HEALTH"
if [ "$HEALTH" = '{"status":"healthy"}' ]; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TEST 2: Rewrite with pirate style"
echo "═══════════════════════════════════════════════════════════════"
echo '→ POST /v1/rewrite {"text": "Hello world", "style": "pirate"}'
RESPONSE=$(curl -s -X POST http://localhost:8001/v1/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello world", "style": "pirate"}')
echo "← $RESPONSE"
if echo "$RESPONSE" | grep -q '"style":"pirate"'; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TEST 3: Default style (formal)"
echo "═══════════════════════════════════════════════════════════════"
echo '→ POST /v1/rewrite {"text": "Hello world"}'
RESPONSE=$(curl -s -X POST http://localhost:8001/v1/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello world"}')
echo "← $RESPONSE"
if echo "$RESPONSE" | grep -q '"style":"formal"'; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TEST 4: Invalid style rejection"
echo "═══════════════════════════════════════════════════════════════"
echo '→ POST /v1/rewrite {"text": "Hello", "style": "invalid"}'
RESPONSE=$(curl -s -X POST http://localhost:8001/v1/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello", "style": "invalid"}')
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8001/v1/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello", "style": "invalid"}')
echo "← HTTP $HTTP_CODE: $RESPONSE"
if [ "$HTTP_CODE" = "422" ]; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TEST 5: Cache hit"
echo "═══════════════════════════════════════════════════════════════"
echo '→ POST /v1/rewrite {"text": "Cache test", "style": "pirate"} (first request)'
RESPONSE1=$(curl -s -X POST http://localhost:8001/v1/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "Cache test", "style": "pirate"}')
echo "← $RESPONSE1"
echo ""
echo '→ POST /v1/rewrite {"text": "Cache test", "style": "pirate"} (second request)'
RESPONSE2=$(curl -s -X POST http://localhost:8001/v1/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "Cache test", "style": "pirate"}')
echo "← $RESPONSE2"
if echo "$RESPONSE2" | grep -q '"cached":true'; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 All E2E tests passed!"
echo "═══════════════════════════════════════════════════════════════"