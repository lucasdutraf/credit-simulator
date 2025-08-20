#!/usr/bin/env python3
"""
Test script for batch loan simulation functionality.
Demonstrates processing multiple loan simulations in a single request.
"""
import os
import json
import time
import random
from datetime import datetime, timedelta
from project import create_app


def generate_test_data(num_simulations=10):
    """Generate test data for batch simulations."""
    simulations = []

    # Generate realistic test data
    for i in range(num_simulations):
        # Random loan value between 10,000 and 500,000
        value = round(random.uniform(10000, 500000), 2)

        # Random age between 20 and 70
        age = random.randint(20, 70)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe day for all months
        date_of_birth = f"{birth_day:02d}-{birth_month:02d}-{birth_year}"

        # Random payment deadline between 12 and 360 months (1-30 years)
        payment_deadline = random.randint(12, 360)

        simulations.append(
            {
                "value": value,
                "date_of_birth": date_of_birth,
                "payment_deadline": payment_deadline,
            }
        )

    return {"simulations": simulations}


def test_batch_simulation(num_simulations):
    """Test batch simulation with specified number of simulations."""

    # Set testing configuration
    os.environ["APP_SETTINGS"] = "project.config.TestingConfig"

    # Create the app
    app = create_app()

    print(f"🧮 Testing Batch Loan Simulation ({num_simulations:,} simulations)")
    print("=" * 60)

    # Generate test data
    print("📊 Generating test data...")
    test_data = generate_test_data(num_simulations)

    # Test the API
    with app.test_client() as client:
        start_time = time.time()

        response = client.post(
            "/loans/simulate",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds

        print(f"📈 Request completed")
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.get_json()

            print(f"✅ Batch Processing Results:")
            print(
                f"   📊 Total Simulations: {result['summary']['total_simulations']:,}"
            )
            print(
                f"   ⏱️  Server Processing Time: {result['summary']['processing_time_ms']:.2f} ms"
            )
            print(f"   🌐 Total Request Time: {total_time:.2f} ms")
            print(
                f"   💰 Average Loan Value: ${result['summary']['average_loan_value']:,.2f}"
            )
            print(
                f"   📅 Average Monthly Payment: ${result['summary']['average_monthly_payment']:,.2f}"
            )

            # Calculate throughput
            simulations_per_second = num_simulations / (total_time / 1000)
            print(f"   🚀 Throughput: {simulations_per_second:,.1f} simulations/second")

            # Show sample results
            print(f"\n📋 Sample Results (first 3):")
            for i, sim_result in enumerate(result["results"][:3]):
                print(
                    f"   {i+1}. Total: ${sim_result['total_value_to_pay']:,.2f}, "
                    f"Monthly: ${sim_result['monthly_payment_amount']:,.2f}, "
                    f"Interest: ${sim_result['total_interest']:,.2f}"
                )

            if len(result["results"]) > 3:
                print(f"   ... and {len(result['results']) - 3:,} more results")

        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.get_json()
                print(f"   Details: {error_data}")
            except:
                print(f"   Response: {response.data}")


def test_performance_scaling():
    """Test performance with different batch sizes."""

    print("🎯 Performance Scaling Test")
    print("=" * 60)

    batch_sizes = [1, 10, 100, 1000, 5000]

    for size in batch_sizes:
        try:
            print(f"\n📊 Testing {size:,} simulations...")
            test_batch_simulation(size)
        except Exception as e:
            print(f"❌ Error with {size:,} simulations: {e}")

        # Small delay between tests
        time.sleep(0.5)


def main():
    """Main test function."""
    print("🚀 Credit Simulator - Batch Processing Test")
    print("=" * 60)

    # Test individual batch sizes
    print("\n1️⃣ Small Batch Test (10 simulations)")
    test_batch_simulation(10)

    print("\n\n2️⃣ Medium Batch Test (100 simulations)")
    test_batch_simulation(100)

    print("\n\n3️⃣ Large Batch Test (1,000 simulations)")
    test_batch_simulation(1000)

    print("\n\n4️⃣ Performance Scaling Analysis")
    test_performance_scaling()

    print("\n\n✨ Batch processing tests completed!")
    print("\n📖 API Usage Examples:")
    print(
        """
# Single simulation in batch format:
{
  "simulations": [
    {
      "value": 50000.0,
      "date_of_birth": "15-06-1990",
      "payment_deadline": 24
    }
  ]
}

# Multiple simulations:
{
  "simulations": [
    {
      "value": 50000.0,
      "date_of_birth": "15-06-1990", 
      "payment_deadline": 24
    },
    {
      "value": 30000.0,
      "date_of_birth": "20-03-1985",
      "payment_deadline": 36
    }
  ]
}
    """
    )


if __name__ == "__main__":
    main()
