"""
Tests for the views module.
"""

import pytest
import json
import os
from unittest.mock import patch
from project import create_app


class TestLoanViews:
    """Test cases for loan-related views."""

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_simulate_loan_valid_request(self, client):
        """Test simulate loan endpoint with valid request."""
        valid_data = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            ]
        }

        with patch(
            "project.api.utils.loan_simulator.LoanSimulator.simulate_loan"
        ) as mock_simulate:
            mock_simulate.return_value = {
                "loan_value": 50000.0,
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

        assert "results" in response_data
        assert "summary" in response_data
        assert len(response_data["results"]) == 1

        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result
        assert result["total_value_to_pay"] == 52812.00
        assert result["monthly_payment_amount"] == 2200.50
        assert result["total_interest"] == 2812.00

    def test_simulate_loan_missing_json_payload(self, client):
        """Test simulate loan endpoint without JSON payload."""
        response = client.post("/loans/simulate")

        # Flask-RESTX returns 415 for missing content type
        assert response.status_code in [400, 415, 500]

    def test_simulate_loan_empty_json_payload(self, client):
        """Test simulate loan endpoint with empty JSON payload."""
        response = client.post(
            "/loans/simulate", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        # Flask-RESTX returns validation errors in 'errors' field
        assert "errors" in response_data or "message" in response_data

    def test_simulate_loan_missing_required_fields(self, client):
        """Test simulate loan endpoint with missing required fields."""
        incomplete_data = {
            "simulations": [
                {
                    "value": 50000.0
                    # Missing date_of_birth and payment_deadline
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        # Flask-RESTX returns validation errors in 'errors' field
        assert "errors" in response_data or "message" in response_data

    def test_simulate_loan_invalid_value(self, client):
        """Test simulate loan endpoint with invalid value."""
        invalid_data = {
            "simulations": [
                {
                    "value": -1000.0,  # Negative value
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        # Flask-RESTX returns validation errors in 'errors' field
        assert "errors" in response_data or "message" in response_data

    def test_simulate_loan_invalid_payment_deadline(self, client):
        """Test simulate loan endpoint with invalid payment deadline."""
        invalid_data = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": -12,  # Negative value
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        # Flask-RESTX returns validation errors in 'errors' field
        assert "errors" in response_data or "message" in response_data

    def test_simulate_loan_invalid_date_format(self, client):
        """Test simulate loan endpoint with invalid date format."""
        invalid_data = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "1990-06-15",  # Wrong format (YYYY-MM-DD)
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        # Flask-RESTX returns validation errors in 'errors' field
        assert "errors" in response_data or "message" in response_data

    def test_simulate_loan_invalid_date_values(self, client):
        """Test simulate loan endpoint with invalid date values."""
        invalid_data = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "32-01-1990",  # Invalid day
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        # Flask-RESTX returns validation errors in 'errors' field
        assert "errors" in response_data or "message" in response_data

    def test_simulate_loan_wrong_content_type(self, client):
        """Test simulate loan endpoint with wrong content type."""
        valid_data = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="text/plain",  # Wrong content type
        )

        # Flask-RESTX returns 415 for wrong content type
        assert response.status_code in [400, 415, 500]

    def test_simulate_loan_malformed_json(self, client):
        """Test simulate loan endpoint with malformed JSON."""
        response = client.post(
            "/loans/simulate",
            data='{"simulations": [{"value": 50000.0, "date_of_birth": "15-06-1990"',  # Missing brace
            content_type="application/json",
        )

        # Flask returns 400 for malformed JSON
        assert response.status_code in [400, 500]

    def test_simulate_loan_young_customer_integration(self, client):
        """Test simulate loan endpoint integration for young customer."""
        valid_data = {
            "simulations": [
                {
                    "value": 10000.0,
                    "date_of_birth": "01-01-2000",  # Young customer (5% rate)
                    "payment_deadline": 12,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert "results" in response_data
        assert "summary" in response_data
        assert len(response_data["results"]) == 1

        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

        # Verify the calculation makes sense
        assert result["total_value_to_pay"] > 10000.0  # Should include interest
        assert result["monthly_payment_amount"] > 0
        assert result["total_interest"] > 0

    def test_simulate_loan_middle_aged_customer_integration(self, client):
        """Test simulate loan endpoint integration for middle-aged customer."""
        valid_data = {
            "simulations": [
                {
                    "value": 25000.0,
                    "date_of_birth": "15-06-1985",  # Middle-aged customer (3% rate)
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert "results" in response_data
        assert "summary" in response_data
        assert len(response_data["results"]) == 1

        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

        # Verify the calculation makes sense
        assert result["total_value_to_pay"] > 25000.0  # Should include interest
        assert result["monthly_payment_amount"] > 0
        assert result["total_interest"] > 0

    def test_simulate_loan_senior_customer_integration(self, client):
        """Test simulate loan endpoint integration for senior customer."""
        valid_data = {
            "simulations": [
                {
                    "value": 15000.0,
                    "date_of_birth": "20-03-1955",  # Senior customer (4% rate)
                    "payment_deadline": 18,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert "results" in response_data
        assert "summary" in response_data
        assert len(response_data["results"]) == 1

        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

        # Verify the calculation makes sense
        assert result["total_value_to_pay"] > 15000.0  # Should include interest
        assert result["monthly_payment_amount"] > 0
        assert result["total_interest"] > 0

    def test_simulate_loan_low_interest_customer_integration(self, client):
        """Test simulate loan endpoint integration for low interest customer."""
        valid_data = {
            "simulations": [
                {
                    "value": 30000.0,
                    "date_of_birth": "10-08-1975",  # Low interest customer (2% rate)
                    "payment_deadline": 30,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert "results" in response_data
        assert "summary" in response_data
        assert len(response_data["results"]) == 1

        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

        # Verify the calculation makes sense
        assert result["total_value_to_pay"] > 30000.0  # Should include interest
        assert result["monthly_payment_amount"] > 0
        assert result["total_interest"] > 0

    def test_simulate_loan_edge_case_values(self, client):
        """Test simulate loan endpoint with edge case values."""
        # Very small loan
        small_loan_data = {
            "simulations": [
                {
                    "value": 100.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 6,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(small_loan_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        assert "results" in response_data
        assert "summary" in response_data
        assert len(response_data["results"]) == 1

        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

        # Verify the calculation makes sense
        assert result["total_value_to_pay"] > 100.0  # Should include interest
        assert result["monthly_payment_amount"] > 0
        assert result["total_interest"] > 0

    def test_simulate_loan_internal_server_error(self, client):
        """Test simulate loan endpoint handling internal server errors."""
        valid_data = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            ]
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
            assert "message" in response_data
            assert "Internal server error" in response_data["message"]

    def test_simulate_loan_response_format(self, client):
        """Test that simulate loan endpoint returns proper JSON format."""
        valid_data = {
            "simulations": [
                {
                    "value": 20000.0,
                    "date_of_birth": "01-12-1980",
                    "payment_deadline": 18,
                }
            ]
        }

        response = client.post(
            "/loans/simulate",
            data=json.dumps(valid_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)

        # Check response structure
        assert "results" in response_data
        assert "summary" in response_data
        assert isinstance(response_data["results"], list)
        assert isinstance(response_data["summary"], dict)

        # Check results structure
        assert len(response_data["results"]) == 1
        result = response_data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

        # Check summary structure
        summary = response_data["summary"]
        assert "total_simulations" in summary
        assert "processing_time_ms" in summary
        assert "average_loan_value" in summary
        assert "average_monthly_payment" in summary

        # Verify data types
        assert isinstance(result["total_value_to_pay"], (int, float))
        assert isinstance(result["monthly_payment_amount"], (int, float))
        assert isinstance(result["total_interest"], (int, float))
        assert isinstance(summary["total_simulations"], int)
        assert isinstance(summary["processing_time_ms"], (int, float))
        assert isinstance(summary["average_loan_value"], (int, float))
        assert isinstance(summary["average_monthly_payment"], (int, float))
