#!/usr/bin/env python3
"""
Test script to demonstrate both single and batch loan simulation endpoints.
"""
import os
import json
import time
from project import create_app


def test_single_endpoint():
    """Test the single loan simulation endpoint."""
    print("🔹 Testing Single Loan Simulation Endpoint")
    print("=" * 50)

    # Set testing configuration
    os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
    app = create_app()

    # Test data for single simulation
    single_data = {
        "value": 50000.0,
        "date_of_birth": "15-06-1990",
        "payment_deadline": 24,
    }

    with app.test_client() as client:
        start_time = time.time()

        response = client.post(
            "/loans/simulate-single",
            data=json.dumps(single_data),
            content_type="application/json",
        )

        end_time = time.time()
        processing_time = (end_time - start_time) * 1000

        print(f"📊 Single Simulation Request:")
        print(f"   Endpoint: /loans/simulate-single")
        print(f"   Status Code: {response.status_code}")
        print(f"   Processing Time: {processing_time:.2f}ms")

        if response.status_code == 200:
            result = response.get_json()
            print(f"✅ Single Simulation Result:")
            print(f"   💰 Total to Pay: ${result['total_value_to_pay']:,.2f}")
            print(f"   📅 Monthly Payment: ${result['monthly_payment_amount']:,.2f}")
            print(f"   💸 Total Interest: ${result['total_interest']:,.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.get_json()
                print(f"   Details: {error_data}")
            except:
                print(f"   Response: {response.data}")


def test_batch_endpoint():
    """Test the batch loan simulation endpoint."""
    print("\n🔹 Testing Batch Loan Simulation Endpoint")
    print("=" * 50)

    # Set testing configuration
    os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
    app = create_app()

    # Test data for batch simulation (3 simulations)
    batch_data = {
        "simulations": [
            {"value": 50000.0, "date_of_birth": "15-06-1990", "payment_deadline": 24},
            {"value": 30000.0, "date_of_birth": "20-03-1985", "payment_deadline": 36},
            {"value": 75000.0, "date_of_birth": "10-12-1975", "payment_deadline": 18},
        ]
    }

    with app.test_client() as client:
        start_time = time.time()

        response = client.post(
            "/loans/simulate",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        end_time = time.time()
        processing_time = (end_time - start_time) * 1000

        print(f"📊 Batch Simulation Request:")
        print(f"   Endpoint: /loans/simulate")
        print(f"   Status Code: {response.status_code}")
        print(f"   Processing Time: {processing_time:.2f}ms")

        if response.status_code == 200:
            result = response.get_json()
            print(f"✅ Batch Simulation Results:")
            print(f"   📈 Total Simulations: {result['summary']['total_simulations']}")
            print(
                f"   ⚡ Server Processing: {result['summary']['processing_time_ms']:.2f}ms"
            )
            print(
                f"   💰 Average Loan Value: ${result['summary']['average_loan_value']:,.2f}"
            )
            print(
                f"   📅 Average Monthly Payment: ${result['summary']['average_monthly_payment']:,.2f}"
            )

            print(f"\n   📋 Individual Results:")
            for i, sim_result in enumerate(result["results"], 1):
                print(
                    f"   {i}. Total: ${sim_result['total_value_to_pay']:,.2f}, "
                    f"Monthly: ${sim_result['monthly_payment_amount']:,.2f}, "
                    f"Interest: ${sim_result['total_interest']:,.2f}"
                )
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.get_json()
                print(f"   Details: {error_data}")
            except:
                print(f"   Response: {response.data}")


def test_consistency():
    """Test that both endpoints give consistent results for the same data."""
    print("\n🔹 Testing Consistency Between Endpoints")
    print("=" * 50)

    # Set testing configuration
    os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
    app = create_app()

    # Same simulation data for both endpoints
    simulation_data = {
        "value": 50000.0,
        "date_of_birth": "15-06-1990",
        "payment_deadline": 24,
    }

    with app.test_client() as client:
        # Single endpoint
        single_response = client.post(
            "/loans/simulate-single",
            data=json.dumps(simulation_data),
            content_type="application/json",
        )

        # Batch endpoint with one simulation
        batch_data = {"simulations": [simulation_data]}
        batch_response = client.post(
            "/loans/simulate",
            data=json.dumps(batch_data),
            content_type="application/json",
        )

        if single_response.status_code == 200 and batch_response.status_code == 200:
            single_result = single_response.get_json()
            batch_result = batch_response.get_json()["results"][0]

            # Compare results
            total_diff = abs(
                single_result["total_value_to_pay"] - batch_result["total_value_to_pay"]
            )
            monthly_diff = abs(
                single_result["monthly_payment_amount"]
                - batch_result["monthly_payment_amount"]
            )
            interest_diff = abs(
                single_result["total_interest"] - batch_result["total_interest"]
            )

            print(f"🔍 Consistency Check:")
            print(f"   Total Value Difference: ${total_diff:.2f}")
            print(f"   Monthly Payment Difference: ${monthly_diff:.2f}")
            print(f"   Total Interest Difference: ${interest_diff:.2f}")

            if total_diff < 0.01 and monthly_diff < 0.01 and interest_diff < 0.01:
                print(f"   ✅ Results are consistent!")
            else:
                print(f"   ❌ Results differ significantly!")
        else:
            print(f"   ❌ One or both endpoints failed")
            print(f"   Single endpoint: {single_response.status_code}")
            print(f"   Batch endpoint: {batch_response.status_code}")


def main():
    """Main test function."""
    print("🚀 Credit Simulator - Dual Endpoint Test")
    print("=" * 60)

    # Test single endpoint
    test_single_endpoint()

    # Test batch endpoint
    test_batch_endpoint()

    # Test consistency
    test_consistency()

    print("\n✨ Dual endpoint tests completed!")
    print("\n📖 API Endpoints Summary:")
    print("   🔹 Single Simulation: POST /loans/simulate-single")
    print("     - Optimized for individual loan calculations")
    print("     - Direct response format")
    print("     - Minimal processing overhead")
    print()
    print("   🔹 Batch Simulation: POST /loans/simulate")
    print("     - Handles 1 to 10,000 simulations")
    print("     - Parallel processing for large batches")
    print("     - Includes summary statistics")
    print("     - Response includes processing metrics")
    print()
    print("   🌐 Swagger Documentation: http://localhost:5001/docs/")


if __name__ == "__main__":
    main()
