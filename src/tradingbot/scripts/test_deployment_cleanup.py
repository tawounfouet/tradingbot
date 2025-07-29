#!/usr/bin/env python3
"""
Deployment cleanup script.
Helps clean up existing deployments and check deployment status.
"""

import json
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


class DeploymentManager:
    """Manager for deployment operations."""

    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None

    def register_and_login(self):
        """Register and login to get auth token."""
        print("🔐 Authenticating...")

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
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get_all_deployments(self):
        """Get all deployments for the user."""
        print("\n📋 Getting all deployments...")

        try:
            response = self.session.get(f"{API_BASE_URL}/strategies/deployments/")

            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    deployments = result["data"]
                    print(f"✅ Found {len(deployments)} deployments:")

                    for deployment in deployments:
                        print(f"  📌 ID: {deployment['id']}")
                        print(f"     Symbol: {deployment['symbol']}")
                        print(f"     Exchange: {deployment['exchange']}")
                        print(f"     Status: {deployment['status']}")
                        print(f"     Strategy ID: {deployment['strategy_id']}")
                        print()

                    return deployments
                else:
                    print(f"❌ Failed to get deployments: {result['message']}")
                    return []
            else:
                print(f"❌ Request failed: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error getting deployments: {e}")
            return []

    def stop_deployment(self, deployment_id):
        """Stop a specific deployment."""
        print(f"\n🛑 Stopping deployment {deployment_id}...")

        try:
            response = self.session.post(
                f"{API_BASE_URL}/strategies/deployments/{deployment_id}/stop"
            )

            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ Deployment stopped successfully")
                    return True
                else:
                    print(f"❌ Failed to stop deployment: {result['message']}")
                    return False
            else:
                print(f"❌ Request failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error stopping deployment: {e}")
            return False

    def stop_all_deployments(self):
        """Stop all active deployments."""
        deployments = self.get_all_deployments()

        active_deployments = [d for d in deployments if d["status"] == "active"]

        if not active_deployments:
            print("✅ No active deployments to stop")
            return True

        print(f"\n🧹 Stopping {len(active_deployments)} active deployments...")

        success_count = 0
        for deployment in active_deployments:
            if self.stop_deployment(deployment["id"]):
                success_count += 1

        print(f"\n📊 Stopped {success_count}/{len(active_deployments)} deployments")
        return success_count == len(active_deployments)

    def run_cleanup(self):
        """Run the complete cleanup process."""
        print("🧹 Starting deployment cleanup")
        print("=" * 50)

        if not self.register_and_login():
            return False

        self.stop_all_deployments()

        # Get final status
        print("\n📋 Final deployment status:")
        final_deployments = self.get_all_deployments()

        active_count = len([d for d in final_deployments if d["status"] == "active"])
        print(f"✅ Cleanup complete. {active_count} active deployments remaining.")

        return True


def main():
    """Main function."""
    manager = DeploymentManager()
    manager.run_cleanup()


if __name__ == "__main__":
    main()
