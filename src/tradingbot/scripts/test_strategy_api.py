#!/usr/bin/env python3
"""
Strategy API Demo Script.
Demonstrates the strategy API endpoints and functionality.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import requests

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "strategy_test@example.com",
    "username": "strategy_tester",
    "password": "TestPassword123!",
    "full_name": "Strategy Tester",
}


class StrategyAPIDemo:
    """Demo class for testing strategy API endpoints."""

    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None

    def register_and_login(self):
        """Register a test user and login."""
        print("🔐 Setting up authentication...")

        # Register user
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/register", json=TEST_USER
            )
            if response.status_code == 409 or "already" in response.text.lower():
                print("✅ User already exists")
            elif response.status_code == 201:
                print("✅ User registered successfully")
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False

        # Login
        try:
            login_data = {
                "username": TEST_USER["email"],  # Using email as username
                "password": TEST_USER["password"],
            }
            response = self.session.post(
                f"{API_BASE_URL}/auth/login", data=login_data  # Form data for OAuth2
            )

            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def test_available_strategies(self):
        """Test getting available strategies."""
        print("\n📋 Testing available strategies endpoint...")

        try:
            response = self.session.get(f"{API_BASE_URL}/strategies/available")

            if response.status_code == 200:
                strategies = response.json()
                print("✅ Available strategies retrieved:")
                for name, info in strategies.items():
                    print(
                        f"  - {name}: {info.get('metadata', {}).get('description', 'No description')}"
                    )
                return strategies
            else:
                print(f"❌ Failed to get available strategies: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting available strategies: {e}")
            return None

    def test_create_strategy(self):
        """Test creating a new strategy."""
        print("\n🚀 Testing strategy creation...")

        strategy_data = {
            "name": "Test Moving Average Strategy",
            "description": "Test strategy for demo purposes",
            "strategy_type": "moving_average_crossover",
            "parameters": {
                "fast_period": 10,
                "slow_period": 20,
                "stop_loss": 0.02,
                "take_profit": 0.05,
            },
            "asset_class": "crypto",
            "is_public": False,
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}/strategies/", json=strategy_data
            )

            if response.status_code == 200:
                strategy = response.json()["data"]
                print("✅ Strategy created successfully:")
                print(f"  ID: {strategy['id']}")
                print(f"  Name: {strategy['name']}")
                print(f"  Type: {strategy['strategy_type']}")
                return strategy
            else:
                print(f"❌ Failed to create strategy: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating strategy: {e}")
            return None

    def test_validate_parameters(self):
        """Test parameter validation."""
        print("\n✅ Testing parameter validation...")

        # Test valid parameters
        valid_params = {
            "fast_period": 10,
            "slow_period": 20,
            "stop_loss": 0.02,
            "take_profit": 0.05,
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}/strategies/validate",
                params={"strategy_type": "moving_average_crossover"},
                json=valid_params,
            )

            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ Valid parameters correctly validated")
                else:
                    print(
                        f"❌ Valid parameters incorrectly rejected: {result['message']}"
                    )
            else:
                print(f"❌ Parameter validation request failed: {response.text}")
        except Exception as e:
            print(f"❌ Error validating parameters: {e}")

        # Test invalid parameters
        invalid_params = {
            "fast_period": 30,  # Fast > Slow (invalid)
            "slow_period": 20,
            "stop_loss": 0.02,
            "take_profit": 0.05,
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}/strategies/validate",
                params={"strategy_type": "moving_average_crossover"},
                json=invalid_params,
            )

            if response.status_code == 200:
                result = response.json()
                if not result["success"]:
                    print("✅ Invalid parameters correctly rejected")
                    print(f"  Reason: {result['message']}")
                else:
                    print("❌ Invalid parameters incorrectly accepted")
            else:
                print(f"❌ Parameter validation request failed: {response.text}")
        except Exception as e:
            print(f"❌ Error validating invalid parameters: {e}")

    def test_get_strategies(self):
        """Test getting user strategies."""
        print("\n📋 Testing get user strategies...")

        try:
            response = self.session.get(f"{API_BASE_URL}/strategies/")

            if response.status_code == 200:
                result = response.json()
                strategies = result["data"]
                print(f"✅ Retrieved {len(strategies)} strategies")
                for strategy in strategies:
                    print(f"  - {strategy['name']} ({strategy['strategy_type']})")
                return strategies
            else:
                print(f"❌ Failed to get strategies: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting strategies: {e}")
            return None

    def test_deploy_strategy(self, strategy_id):
        """Test deploying a strategy."""
        print("\n🚀 Testing strategy deployment...")

        # symbols list : ["LTCUSDT", "ETHUSDT", "BTCUSDT", "XRPUSDT", "BNBUSDT"]
        deployment_data = {
            "strategy_id": strategy_id,
            "exchange": "binance",
            "symbol": "BNBUSDT",  # Use BNBUSDT instead to avoid conflicts
            "timeframe": "1h",
            "amount": 100.0,
            "parameters": {"fast_period": 12, "slow_period": 26},  # Override default
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}/strategies/{strategy_id}/deploy", json=deployment_data
            )

            if response.status_code == 200:
                deployment = response.json()["data"]
                print("✅ Strategy deployed successfully:")
                print(f"  Deployment ID: {deployment['id']}")
                print(f"  Symbol: {deployment['symbol']}")
                print(f"  Status: {deployment['status']}")
                return deployment
            else:
                print(f"❌ Failed to deploy strategy: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error deploying strategy: {e}")
            return None

    def test_get_individual_strategy(self, strategy_id):
        """Test getting a specific strategy by ID."""
        print("\n📖 Testing get individual strategy...")

        try:
            response = self.session.get(f"{API_BASE_URL}/strategies/{strategy_id}")

            if response.status_code == 200:
                strategy = response.json()["data"]
                print("✅ Individual strategy retrieved successfully:")
                print(f"  ID: {strategy['id']}")
                print(f"  Name: {strategy['name']}")
                print(f"  Type: {strategy['strategy_type']}")
                print(f"  Parameters: {strategy['parameters']}")
                return strategy
            else:
                print(f"❌ Failed to get individual strategy: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting individual strategy: {e}")
            return None

    def test_update_strategy(self, strategy_id):
        """Test updating a strategy."""
        print("\n✏️ Testing strategy update...")

        update_data = {
            "description": "Updated test strategy description",
            "parameters": {
                "fast_period": 8,  # Changed from 10
                "slow_period": 21,  # Changed from 20
                "stop_loss": 0.015,  # Changed from 0.02
                "take_profit": 0.06,  # Changed from 0.05
            },
        }

        try:
            response = self.session.put(
                f"{API_BASE_URL}/strategies/{strategy_id}", json=update_data
            )

            if response.status_code == 200:
                strategy = response.json()["data"]
                print("✅ Strategy updated successfully:")
                print(f"  Description: {strategy['description']}")
                print(f"  New Parameters: {strategy['parameters']}")
                return strategy
            else:
                print(f"❌ Failed to update strategy: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error updating strategy: {e}")
            return None

    def test_get_deployments(self):
        """Test getting user deployments."""
        print("\n📋 Testing get deployments...")

        try:
            response = self.session.get(f"{API_BASE_URL}/strategies/deployments/")

            if response.status_code == 200:
                result = response.json()
                deployments = result[
                    "data"
                ]  # Extract deployments from DataResponse wrapper
                print(f"✅ Retrieved {len(deployments)} deployments")
                for deployment in deployments:
                    print(
                        f"  - {deployment.get('symbol', 'Unknown')} on {deployment.get('exchange', 'Unknown')} (Status: {deployment.get('status', 'Unknown')})"
                    )
                return deployments
            else:
                print(f"❌ Failed to get deployments: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting deployments: {e}")
            return None

    def test_stop_deployment(self, deployment_id):
        """Test stopping a deployment."""
        print("\n🛑 Testing deployment stop...")

        try:
            response = self.session.post(
                f"{API_BASE_URL}/strategies/deployments/{deployment_id}/stop",
                params={"reason": "Testing deployment stop functionality"},
            )

            if response.status_code == 200:
                deployment = response.json()["data"]
                print("✅ Deployment stopped successfully:")
                print(f"  Status: {deployment['status']}")
                return deployment
            else:
                print(f"❌ Failed to stop deployment: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error stopping deployment: {e}")
            return None

    def test_delete_strategy(self, strategy_id):
        """Test deleting a strategy (soft delete)."""
        print("\n🗑️ Testing strategy deletion...")

        try:
            response = self.session.delete(f"{API_BASE_URL}/strategies/{strategy_id}")

            if response.status_code == 200:
                result = response.json()
                print("✅ Strategy deleted successfully:")
                print(f"  Message: {result['message']}")
                return True
            else:
                print(f"❌ Failed to delete strategy: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error deleting strategy: {e}")
            return False

    def test_update_strategy_with_active_deployment(self, strategy_id):
        """Test updating a strategy that has active deployments (should fail)."""
        print("\n⚠️ Testing strategy update with active deployment (should fail)...")

        update_data = {
            "parameters": {
                "fast_period": 15,
                "slow_period": 30,
            }
        }

        try:
            response = self.session.put(
                f"{API_BASE_URL}/strategies/{strategy_id}", json=update_data
            )

            if response.status_code == 400:
                print("✅ Strategy update correctly blocked due to active deployment")
                print(f"  Reason: {response.json().get('detail', 'Unknown')}")
                return True
            elif response.status_code == 200:
                print("❌ Strategy update should have been blocked but was allowed")
                return False
            else:
                print(f"❌ Unexpected response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error testing protected update: {e}")
            return False

    def test_delete_strategy_with_active_deployment(self, strategy_id):
        """Test deleting a strategy that has active deployments (should fail)."""
        print("\n⚠️ Testing strategy deletion with active deployment (should fail)...")

        try:
            response = self.session.delete(f"{API_BASE_URL}/strategies/{strategy_id}")

            if response.status_code == 400:
                print("✅ Strategy deletion correctly blocked due to active deployment")
                print(f"  Reason: {response.json().get('detail', 'Unknown')}")
                return True
            elif response.status_code == 200:
                print("❌ Strategy deletion should have been blocked but was allowed")
                return False
            else:
                print(f"❌ Unexpected response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error testing protected deletion: {e}")
            return False

    def run_demo(self):
        """Run the complete demo."""
        print("🎯 Starting Strategy API Demo")
        print("=" * 50)

        # Setup authentication
        if not self.register_and_login():
            print("❌ Authentication setup failed")
            return False

        # Test available strategies
        available_strategies = self.test_available_strategies()
        if not available_strategies:
            print("❌ Could not get available strategies")
            return False

        # Test parameter validation
        self.test_validate_parameters()

        # Test creating a strategy
        strategy = self.test_create_strategy()
        if not strategy:
            print("❌ Could not create strategy")
            return False

        # Test getting strategies
        strategies = self.test_get_strategies()
        if not strategies:
            print("❌ Could not get strategies")
            return False

        # Test getting individual strategy
        individual_strategy = self.test_get_individual_strategy(strategy["id"])
        if not individual_strategy:
            print("❌ Could not get individual strategy")
            return False

        # Test strategy update (without active deployment)
        updated_strategy = self.test_update_strategy(strategy["id"])
        if not updated_strategy:
            print("❌ Could not update strategy")
            return False

        # Test deploying strategy
        deployment = self.test_deploy_strategy(strategy["id"])
        if not deployment:
            print("❌ Could not deploy strategy")
            return False

        # Test getting deployments
        deployments = self.test_get_deployments()
        if deployments is None:
            print("❌ Could not get deployments")
            return False

        # Test protected operations (should fail with active deployment)
        print("\n🔒 Testing protected operations with active deployment...")
        self.test_update_strategy_with_active_deployment(strategy["id"])
        self.test_delete_strategy_with_active_deployment(strategy["id"])

        # Test stopping deployment
        stopped_deployment = self.test_stop_deployment(deployment["id"])
        if not stopped_deployment:
            print("❌ Could not stop deployment")
            return False

        # Test deleting strategy
        if not self.test_delete_strategy(strategy["id"]):
            print("❌ Could not delete strategy")
            return False

        print("\n🎉 Strategy API Demo completed successfully!")
        print("=" * 50)
        return True


def main():
    """Main function."""
    print("🚀 Starting Strategy API Demo")

    # Check if server is running
    try:
        response = requests.get(
            "http://localhost:8000/health"
        )  # Health endpoint is at root
        if response.status_code != 200:
            print("❌ API server is not running or not healthy")
            print("Please start the server with: python src/backend/main.py")
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("Please start the server with: python src/backend/main.py")
        return 1

    # Run demo
    demo = StrategyAPIDemo()
    success = demo.run_demo()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
