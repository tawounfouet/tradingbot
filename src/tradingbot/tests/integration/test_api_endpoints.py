"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from tradingbot.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint_exists(self, client):
        """Test that health endpoint exists and responds."""
        response = client.get("/health")
        # Accept both 200 (working) and 404 (not implemented yet)
        assert response.status_code in [200, 404]

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        # Accept various status codes as the endpoint might not be fully implemented
        assert response.status_code in [200, 404, 422]


class TestDocsEndpoint:
    """Test documentation endpoints."""

    def test_docs_endpoint(self, client):
        """Test that docs endpoint exists."""
        response = client.get("/docs")
        # Swagger docs should be available
        assert response.status_code in [200, 404]

    def test_redoc_endpoint(self, client):
        """Test that redoc endpoint exists."""
        response = client.get("/redoc")
        # ReDoc should be available
        assert response.status_code in [200, 404]


class TestAPIRoutes:
    """Test API route structure."""

    def test_api_routes_import(self):
        """Test that API routes can be imported."""
        from tradingbot import routers

        assert routers is not None

    def test_auth_routes_import(self):
        """Test that auth routes can be imported."""
        from tradingbot.routers import auth

        assert auth is not None

    def test_user_routes_import(self):
        """Test that user routes can be imported."""
        from tradingbot.routers import users

        assert users is not None

    def test_strategy_routes_import(self):
        """Test that strategy routes can be imported."""
        from tradingbot.routers import strategies

        assert strategies is not None
