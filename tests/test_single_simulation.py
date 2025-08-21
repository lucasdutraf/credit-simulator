"""
Tests for single loan simulation functionality.
"""

import pytest
import os
from project import create_app


class TestSingleLoanSimulation:
    """Test cases for single loan simulation endpoint."""

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_single_simulation_valid_request(self, client):
        """Test single simulation endpoint with valid request."""
        payload = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "total_value_to_pay" in data
        assert "monthly_payment_amount" in data
        assert "total_interest" in data
        assert data["total_value_to_pay"] > 0
        assert data["monthly_payment_amount"] > 0

    def test_single_simulation_young_customer(self, client):
        """Test single simulation for young customer (high interest rate)."""
        payload = {
            "value": 50000.0,
            "date_of_birth": "01-01-2000",  # Young customer (5% rate)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        # Young customers should have higher interest due to 5% rate
        assert data["total_interest"] > 0
        assert data["total_value_to_pay"] > 50000.0

    def test_single_simulation_middle_aged_customer(self, client):
        """Test single simulation for middle-aged customer (medium interest rate)."""
        payload = {
            "value": 50000.0,
            "date_of_birth": "01-01-1985",  # Middle-aged customer (3% rate)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["total_interest"] > 0
        assert data["total_value_to_pay"] > 50000.0

    def test_single_simulation_low_interest_customer(self, client):
        """Test single simulation for low interest customer."""
        payload = {
            "value": 50000.0,
            "date_of_birth": "01-01-1975",  # Low interest customer (2% rate)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["total_interest"] > 0
        assert data["total_value_to_pay"] > 50000.0

    def test_single_simulation_senior_customer(self, client):
        """Test single simulation for senior customer (higher interest rate)."""
        payload = {
            "value": 50000.0,
            "date_of_birth": "01-01-1955",  # Senior customer (4% rate)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["total_interest"] > 0
        assert data["total_value_to_pay"] > 50000.0

    def test_single_simulation_missing_json_payload(self, client):
        """Test single simulation endpoint without JSON payload."""
        response = client.post("/loans/simulate-single")

        assert response.status_code in [400, 415]  # 415 for unsupported media type
        if response.status_code == 415:
            # Flask-RESTX returns 415 for missing content type
            assert True
        else:
            data = response.get_json()
            assert "error" in data or "message" in data

    def test_single_simulation_empty_json_payload(self, client):
        """Test single simulation endpoint with empty JSON payload."""
        response = client.post(
            "/loans/simulate-single", json={}, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_missing_required_fields(self, client):
        """Test single simulation endpoint with missing required fields."""
        incomplete_data = {
            "value": 50000.0,
            # Missing date_of_birth and payment_deadline
        }

        response = client.post(
            "/loans/simulate-single",
            json=incomplete_data,
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_invalid_value(self, client):
        """Test single simulation endpoint with invalid loan value."""
        invalid_data = {
            "value": -1000.0,  # Invalid negative value
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=invalid_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_invalid_payment_deadline(self, client):
        """Test single simulation endpoint with invalid payment deadline."""
        invalid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 0,  # Invalid zero value
        }

        response = client.post(
            "/loans/simulate-single", json=invalid_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_invalid_date_format(self, client):
        """Test single simulation endpoint with invalid date format."""
        invalid_data = {
            "value": 50000.0,
            "date_of_birth": "1990-06-15",  # Invalid format (should be DD-MM-YYYY)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=invalid_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_string_value(self, client):
        """Test single simulation endpoint with string value instead of number."""
        invalid_data = {
            "value": "50000",  # Should be float, not string
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=invalid_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_float_payment_deadline(self, client):
        """Test single simulation endpoint with float payment deadline instead of integer."""
        invalid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24.5,  # Should be integer, not float
        }

        response = client.post(
            "/loans/simulate-single", json=invalid_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data or "message" in data

    def test_single_simulation_response_format(self, client):
        """Test that single simulation response has correct format."""
        payload = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate-single", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        # Verify response structure (single simulation format, not batch)
        assert "total_value_to_pay" in data
        assert "monthly_payment_amount" in data
        assert "total_interest" in data

        # Should NOT have batch-specific fields
        assert "results" not in data
        assert "summary" not in data

        # Verify data types
        assert isinstance(data["total_value_to_pay"], (int, float))
        assert isinstance(data["monthly_payment_amount"], (int, float))
        assert isinstance(data["total_interest"], (int, float))

    def test_single_vs_batch_comparison(self, client):
        """Test that single endpoint gives same result as batch with one item."""
        simulation_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        # Single simulation
        single_response = client.post(
            "/loans/simulate-single",
            json=simulation_data,
            content_type="application/json",
        )

        # Batch simulation with one item
        batch_data = {"simulations": [simulation_data]}
        batch_response = client.post(
            "/loans/simulate", json=batch_data, content_type="application/json"
        )

        assert single_response.status_code == 200
        assert batch_response.status_code == 200

        single_data = single_response.get_json()
        batch_data = batch_response.get_json()

        # Extract the single result from batch response
        batch_result = batch_data["results"][0]

        # Compare results (should be identical)
        assert (
            abs(single_data["total_value_to_pay"] - batch_result["total_value_to_pay"])
            < 0.01
        )
        assert (
            abs(
                single_data["monthly_payment_amount"]
                - batch_result["monthly_payment_amount"]
            )
            < 0.01
        )
        assert (
            abs(single_data["total_interest"] - batch_result["total_interest"]) < 0.01
        )
