#!/usr/bin/env python3
"""Debug script to test importing the FastAPI app and creating TestClient."""

import traceback


def test_import():
    """Test importing the app."""
    try:
        print("Testing import of tradingbot.main...")
        from tradingbot.main import app

        print("✅ Successfully imported app")
        print(f"App type: {type(app)}")
        return app
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        traceback.print_exc()
        return None


def test_testclient(app):
    """Test creating TestClient."""
    if not app:
        print("❌ No app to test with")
        return None

    try:
        print("Testing TestClient creation...")
        from fastapi.testclient import TestClient

        # The app parameter should be positional, not keyword
        client = TestClient(app)
        print("✅ Successfully created TestClient")
        print(f"Client type: {type(client)}")
        return client
    except Exception as e:
        print(f"❌ Failed to create TestClient: {e}")

        # Let's try to understand what's happening
        try:
            import inspect

            sig = inspect.signature(TestClient.__init__)
            print(f"TestClient signature: {sig}")
        except Exception as e2:
            print(f"Couldn't get signature: {e2}")

        traceback.print_exc()
        return None


def test_basic_request(client):
    """Test a basic request."""
    if not client:
        print("❌ No client to test with")
        return

    try:
        print("Testing basic request...")
        response = client.get("/")
        print(f"✅ Request successful, status: {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ Request failed: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🔍 Debug FastAPI App Import and TestClient Creation")
    print("=" * 60)

    app = test_import()
    client = test_testclient(app)
    response = test_basic_request(client)

    print("=" * 60)
    if app and client:
        print("✅ All tests passed! Integration tests should work.")
    else:
        print("❌ Some tests failed. Integration tests may have issues.")
