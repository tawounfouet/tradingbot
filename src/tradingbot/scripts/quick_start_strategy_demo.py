#!/usr/bin/env python3
"""
Quick start script for the Crypto Trading Bot with Strategy Engine.
This script demonstrates the complete strategy system functionality.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🤖 {title}")
    print("=" * 60)


def print_step(step, description):
    """Print a step description."""
    print(f"\n{step}. {description}")
    print("-" * 40)


def run_strategy_engine_test():
    """Run the strategy engine test."""
    print_step("1", "Testing Strategy Engine")

    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_dir))

    script_path = Path("scripts/test_strategy_engine.py")
    if not script_path.exists():
        print("❌ Strategy engine test script not found")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ Strategy Engine test passed!")
            # Print some key output
            lines = result.stdout.split("\n")
            for line in lines:
                if (
                    "Available strategies:" in line
                    or "Test Summary" in line
                    or "🎉" in line
                ):
                    print(f"  {line}")
            return True
        else:
            print("❌ Strategy Engine test failed!")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Strategy Engine test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running strategy engine test: {e}")
        return False


def start_api_server():
    """Start the FastAPI server."""
    print_step("2", "Starting FastAPI Server")

    backend_path = Path("src/backend")
    if not backend_path.exists():
        print("❌ Backend directory not found")
        return None

    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait a bit for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)

        # Check if server is running
        import requests

        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI server started successfully!")
                print("📚 API Documentation: http://localhost:8000/api/v1/docs")
                return process
            else:
                print("❌ Server health check failed")
                process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ Cannot connect to server")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None


def test_strategy_api():
    """Test the strategy API."""
    print_step("3", "Testing Strategy API")

    script_path = Path("scripts/test_strategy_api.py")
    if not script_path.exists():
        print("❌ Strategy API test script not found")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            print("✅ Strategy API test passed!")
            # Print key output
            lines = result.stdout.split("\n")
            for line in lines:
                if ("✅" in line or "❌" in line or "🎉" in line) and "Testing" in line:
                    print(f"  {line}")
            return True
        else:
            print("❌ Strategy API test failed!")
            print("Output:", result.stdout)
            print("Error:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Strategy API test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running strategy API test: {e}")
        return False


def show_strategy_info():
    """Show information about available strategies."""
    print_step("4", "Strategy Information")

    try:
        # Import strategy system
        sys.path.insert(0, "src/backend")
        from strategies import get_strategy, registry

        strategies = registry.list_strategies()
        print(f"📊 Available Strategies ({len(strategies)}):")

        for strategy_name in strategies:
            info = registry.get_strategy_info(strategy_name)
            metadata = info.get("metadata", {})
            print(f"\n🔹 {strategy_name}")
            print(f"   Description: {metadata.get('description', 'No description')}")
            print(f"   Class: {info.get('class', 'Unknown')}")

            # Show parameters
            params = metadata.get("parameters", {})
            if params:
                print(f"   Parameters:")
                for param_name, param_info in params.items():
                    default = param_info.get("default", "N/A")
                    param_type = param_info.get("type", "unknown")
                    print(f"     - {param_name} ({param_type}): default={default}")

        return True
    except Exception as e:
        print(f"❌ Error showing strategy info: {e}")
        return False


def show_usage_examples():
    """Show usage examples."""
    print_step("5", "Usage Examples")

    examples = [
        {
            "title": "Create a Moving Average Strategy",
            "endpoint": "POST /api/v1/strategies/",
            "payload": {
                "name": "My MA Strategy",
                "strategy_type": "moving_average_crossover",
                "parameters": {"fast_period": 10, "slow_period": 20},
            },
        },
        {
            "title": "Deploy Strategy for Trading",
            "endpoint": "POST /api/v1/strategies/{id}/deploy",
            "payload": {
                "exchange": "binance",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "amount": 100.0,
            },
        },
        {
            "title": "Get Available Strategies",
            "endpoint": "GET /api/v1/strategies/available",
            "payload": "No payload required",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   Endpoint: {example['endpoint']}")
        if isinstance(example["payload"], dict):
            import json

            print(f"   Payload: {json.dumps(example['payload'], indent=2)}")
        else:
            print(f"   Payload: {example['payload']}")


def main():
    """Main function."""
    print_header("Crypto Trading Bot - Strategy Engine Demo")

    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    server_process = None

    try:
        # Step 1: Test strategy engine
        if not run_strategy_engine_test():
            print("❌ Strategy engine test failed, aborting")
            return 1

        # Step 2: Start API server
        server_process = start_api_server()
        if not server_process:
            print("❌ Failed to start API server, aborting")
            return 1

        # Step 3: Test strategy API
        if not test_strategy_api():
            print("⚠️  Strategy API test failed, but continuing...")

        # Step 4: Show strategy information
        show_strategy_info()

        # Step 5: Show usage examples
        show_usage_examples()

        print_header("Demo Completed Successfully! 🎉")
        print("\n🌐 Your Crypto Trading Bot is now running!")
        print("📊 Strategy Engine: ✅ Active")
        print("🔗 API Server: ✅ Running on http://localhost:8000")
        print("📚 Documentation: http://localhost:8000/api/v1/docs")
        print("\n💡 Tips:")
        print("  - Use the API documentation to explore endpoints")
        print("  - Create strategies via POST /api/v1/strategies/")
        print("  - Deploy strategies via POST /api/v1/strategies/{id}/deploy")
        print("  - Monitor deployments via GET /api/v1/strategies/deployments/")

        print("\n⏹️  Press Ctrl+C to stop the server")

        # Keep server running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1
    finally:
        # Clean up server process
        if server_process:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                server_process.kill()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
