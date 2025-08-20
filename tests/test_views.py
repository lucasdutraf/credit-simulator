"""
Tests for the views module.
"""

import pytest
import json
from unittest.mock import patch
from flask import Flask
from project.api.views import loan_blueprint


class TestLoanViews:
    """Test cases for loan-related views."""

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.register_blueprint(loan_blueprint, url_prefix="/loans")
        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_simulate_loan_valid_request(self, client):
        """Test simulate loan endpoint with valid request."""
        valid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        with patch("project.api.views.LoanSimulator.simulate_loan") as mock_simulate:
            mock_simulate.return_value = {
                "monthly_payment": 2200.50,
                "total_value_to_pay": 52812.00,
                "total_interest": 2812.00,
            }

            response = client.post(
                "/loans/simulate",
                data=json.dumps(valid_data),
                content_type="application/json",
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert "total_value_to_pay" in response_data
        assert "monthly_payment_amount" in response_data
        assert "total_interest" in response_data
        assert response_data["total_value_to_pay"] == 52812.00
        assert response_data["monthly_payment_amount"] == 2200.50
        assert response_data["total_interest"] == 2812.00

    def test_simulate_loan_missing_json_payload(self, client):
        """Test simulate loan endpoint without JSON payload."""
        response = client.post("/loans/simulate")

        # Flask may return 500 when trying to parse non-existent JSON
        assert response.status_code in [400, 500]
        if response.status_code == 400:
            response_data = json.loads(response.data)
            assert "error" in response_data
            assert response_data["error"] == "JSON payload is required"

    def test_simulate_loan_empty_json_payload(self, client):
        """Test simulate loan endpoint with empty JSON payload."""
        response = client.post(
            "/loans/simulate", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert response_data["error"] == "Validation failed"
        assert "details" in response_data

    def test_simulate_loan_missing_required_fields(self, client):
        """Test simulate loan endpoint with missing required fields."""
        incomplete_data = {
            "value": 50000.0
            # Missing date_of_birth and payment_deadline
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Validation failed"
        assert "details" in response_data
        assert "date_of_birth" in response_data["details"]
        assert "payment_deadline" in response_data["details"]

    def test_simulate_loan_invalid_value(self, client):
        """Test simulate loan endpoint with invalid value."""
        invalid_data = {
            "value": -1000.0,  # Negative value
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Validation failed"
        assert "value" in response_data["details"]

    def test_simulate_loan_invalid_payment_deadline(self, client):
        """Test simulate loan endpoint with invalid payment deadline."""
        invalid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": -12,  # Negative value
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Validation failed"
        assert "payment_deadline" in response_data["details"]

    def test_simulate_loan_invalid_date_format(self, client):
        """Test simulate loan endpoint with invalid date format."""
        invalid_data = {
            "value": 50000.0,
            "date_of_birth": "1990-06-15",  # Wrong format (YYYY-MM-DD)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Validation failed"
        assert "date_of_birth" in response_data["details"]

    def test_simulate_loan_invalid_date_values(self, client):
        """Test simulate loan endpoint with invalid date values."""
        invalid_data = {
            "value": 50000.0,
            "date_of_birth": "32-01-1990",  # Invalid day
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["error"] == "Validation failed"
        assert "date_of_birth" in response_data["details"]

    def test_simulate_loan_wrong_content_type(self, client):
        """Test simulate loan endpoint with wrong content type."""
        valid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="text/plain",  # Wrong content type
        )

        # Flask returns 500 for wrong content type when trying to parse JSON
        assert response.status_code == 500

    def test_simulate_loan_malformed_json(self, client):
        """Test simulate loan endpoint with malformed JSON."""
        response = client.post(
            "/loans/simulate",
            data='{"value": 50000.0, "date_of_birth": "15-06-1990"',  # Missing brace
            content_type="application/json",
        )

        # Flask returns 500 for malformed JSON
        assert response.status_code == 500

    def test_simulate_loan_young_customer_integration(self, client):
        """Test simulate loan endpoint integration for young customer."""
        valid_data = {
            "value": 10000.0,
            "date_of_birth": "01-01-2000",  # Young customer (5% rate)
            "payment_deadline": 12,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        # Verify response structure
        assert "total_value_to_pay" in response_data
        assert "monthly_payment_amount" in response_data
        assert "total_interest" in response_data

        # Verify that values are reasonable for a young customer (5% rate)
        assert (
            response_data["total_value_to_pay"] > 10000.0
        )  # Should be more than loan value
        assert response_data["monthly_payment_amount"] > 0
        assert response_data["total_interest"] > 0

    def test_simulate_loan_middle_aged_customer_integration(self, client):
        """Test simulate loan endpoint integration for middle-aged customer."""
        valid_data = {
            "value": 25000.0,
            "date_of_birth": "15-06-1985",  # Middle-aged customer (3% rate)
            "payment_deadline": 24,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        # Verify response structure and reasonable values
        assert response_data["total_value_to_pay"] > 25000.0
        assert response_data["monthly_payment_amount"] > 0
        assert response_data["total_interest"] > 0

    def test_simulate_loan_senior_customer_integration(self, client):
        """Test simulate loan endpoint integration for senior customer."""
        valid_data = {
            "value": 15000.0,
            "date_of_birth": "20-03-1955",  # Senior customer (4% rate)
            "payment_deadline": 18,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        # Verify response structure and reasonable values
        assert response_data["total_value_to_pay"] > 15000.0
        assert response_data["monthly_payment_amount"] > 0
        assert response_data["total_interest"] > 0

    def test_simulate_loan_low_interest_customer_integration(self, client):
        """Test simulate loan endpoint integration for low interest customer."""
        valid_data = {
            "value": 30000.0,
            "date_of_birth": "10-08-1975",  # Low interest customer (2% rate)
            "payment_deadline": 30,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        # Verify response structure and reasonable values
        assert response_data["total_value_to_pay"] > 30000.0
        assert response_data["monthly_payment_amount"] > 0
        assert response_data["total_interest"] > 0

    def test_simulate_loan_edge_case_values(self, client):
        """Test simulate loan endpoint with edge case values."""
        # Very small loan
        small_loan_data = {
            "value": 100.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 6,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(small_loan_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["total_value_to_pay"] >= 100.0

        # Very large loan
        large_loan_data = {
            "value": 500000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 360,  # 30 years
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(large_loan_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["total_value_to_pay"] >= 500000.0

    def test_simulate_loan_internal_server_error(self, client):
        """Test simulate loan endpoint handling internal server errors."""
        valid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        with patch("project.api.views.LoanSimulator.simulate_loan") as mock_simulate:
            mock_simulate.side_effect = Exception("Database connection failed")

            response = client.post(
                "/loans/simulate",
                data=json.dumps(valid_data),
                content_type="application/json",
            )

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "Internal server error" in response_data["error"]

    def test_simulate_loan_response_format(self, client):
        """Test that simulate loan endpoint returns proper JSON format."""
        valid_data = {
            "value": 20000.0,
            "date_of_birth": "01-12-1980",
            "payment_deadline": 18,
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.content_type == "application/json"

        response_data = json.loads(response.data)

        # Verify exact response structure
        expected_keys = {
            "total_value_to_pay",
            "monthly_payment_amount",
            "total_interest",
        }
        assert set(response_data.keys()) == expected_keys

        # Verify data types
        assert isinstance(response_data["total_value_to_pay"], (int, float))
        assert isinstance(response_data["monthly_payment_amount"], (int, float))
        assert isinstance(response_data["total_interest"], (int, float))
