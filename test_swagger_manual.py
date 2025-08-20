#!/usr/bin/env python3
"""
Manual test script to demonstrate Swagger API functionality.
Run this script to start the application and test the Swagger documentation.
"""
import os
import json
import requests
import time
import threading
from project import create_app


def test_swagger_api():
    """Test the Swagger API endpoints."""

    # Set development configuration
    os.environ["APP_SETTINGS"] = "project.config.DevelopmentConfig"

    # Create the app
    app = create_app()

    # Start the app in a separate thread
    def run_app():
        app.run(host="0.0.0.0", port=5555, debug=False)

    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    print("🚀 Testing Credit Simulator Swagger API")
    print("=" * 50)

    # Test the API endpoint
    base_url = "http://localhost:5555"

    # Test data
    test_data = {
        "value": 50000.0,
        "date_of_birth": "15-06-1990",
        "payment_deadline": 24,
    }

    try:
        # Test the loan simulation endpoint
        print("📊 Testing POST /loans/simulate endpoint...")
        response = requests.post(
            f"{base_url}/loans/simulate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )

        print(f"   ✅ Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   💰 Total Value to Pay: ${result['total_value_to_pay']:,.2f}")
            print(f"   📅 Monthly Payment: ${result['monthly_payment_amount']:,.2f}")
            print(f"   📈 Total Interest: ${result['total_interest']:,.2f}")
        else:
            print(f"   ❌ Error: {response.text}")

        print()

        # Test Swagger JSON endpoint
        print("📝 Testing Swagger JSON endpoint...")
        swagger_response = requests.get(f"{base_url}/swagger.json", timeout=5)
        print(f"   ✅ Swagger JSON Status: {swagger_response.status_code}")

        if swagger_response.status_code == 200:
            swagger_data = swagger_response.json()
            print(
                f"   📄 API Title: {swagger_data.get('info', {}).get('title', 'N/A')}"
            )
            print(
                f"   🔢 API Version: {swagger_data.get('info', {}).get('version', 'N/A')}"
            )
            print(f"   🔗 Endpoints: {list(swagger_data.get('paths', {}).keys())}")

        print()
        print("🌐 Swagger UI Access Points:")
        print(f"   📚 Swagger UI: {base_url}/docs/")
        print(f"   🔧 API Root: {base_url}/")
        print(f"   📊 Loan Simulate: {base_url}/loans/simulate")
        print(f"   📄 Swagger JSON: {base_url}/swagger.json")

        print()
        print("🎯 Example curl command:")
        print(
            f"""
curl -X POST {base_url}/loans/simulate \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(test_data, indent=2)}'
        """
        )

        print("✨ Swagger documentation is working! ✨")
        print(f"   Visit {base_url}/docs/ to see the interactive API documentation")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing API: {e}")
        print("Make sure the application is running...")

    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")


if __name__ == "__main__":
    test_swagger_api()
