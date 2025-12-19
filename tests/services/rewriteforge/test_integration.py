import pytest
from httpx import ASGITransport, AsyncClient
from rewriteforge.bootstrap import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


class TestRewriteEndpoint:
    async def test_rewrite_full_flow(self, client):
        """Integration test: full request -> response cycle"""
        response = await client.post(
            "/v1/rewrite", json={"text": "Hello world", "style": "pirate"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original"] == "Hello world"
        assert data["style"] == "pirate"
        assert "rewritten" in data
        assert "cached" in data

    async def test_rewrite_default_style(self, client):
        """Test style defaults to formal when missing"""
        response = await client.post("/v1/rewrite", json={"text": "Hello world"})

        assert response.status_code == 200
        assert response.json()["style"] == "formal"

    async def test_rewrite_invalid_style(self, client):
        """Test 422 for unknown style"""
        response = await client.post(
            "/v1/rewrite", json={"text": "Hello world", "style": "unknown"}
        )

        assert response.status_code == 422

    async def test_rewrite_text_too_long(self, client):
        """Test 422 for text exceeding limit"""
        response = await client.post(
            "/v1/rewrite", json={"text": "x" * 6000, "style": "pirate"}
        )

        assert response.status_code == 422

    async def test_rewrite_empty_text(self, client):
        """Test 422 for empty text"""
        response = await client.post("/v1/rewrite", json={"text": "", "style": "pirate"})

        assert response.status_code == 422

    async def test_health_check(self, client):
        """Test health endpoint"""
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    async def test_rewrite_caching(self, client):
        """Test that second request returns cached result"""
        # First request
        response1 = await client.post(
            "/v1/rewrite", json={"text": "Cache test", "style": "formal"}
        )
        assert response1.status_code == 200
        assert response1.json()["cached"] is False

        # Second request with same input
        response2 = await client.post(
            "/v1/rewrite", json={"text": "Cache test", "style": "formal"}
        )
        assert response2.status_code == 200
        assert response2.json()["cached"] is True


class TestStreamEndpoint:
    async def test_rewrite_stream(self, client):
        """Test streaming endpoint returns SSE format"""
        response = await client.post(
            "/v1/rewrite/stream", json={"text": "Hello world", "style": "pirate"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Check SSE format
        content = response.text
        assert "data:" in content
        assert "[DONE]" in content
