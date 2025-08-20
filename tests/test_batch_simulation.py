"""
Tests for batch loan simulation functionality.
"""

import pytest
import os
from project import create_app


class TestBatchLoanSimulation:
    """Test cases for batch loan simulation."""

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_single_simulation_in_batch(self, client):
        """Test single simulation using batch format."""
        payload = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 1
        assert data["summary"]["total_simulations"] == 1

        result = data["results"][0]
        assert "total_value_to_pay" in result
        assert "monthly_payment_amount" in result
        assert "total_interest" in result

    def test_multiple_simulations_batch(self, client):
        """Test multiple simulations in a batch."""
        payload = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                },
                {
                    "value": 30000.0,
                    "date_of_birth": "20-03-1985",
                    "payment_deadline": 36,
                },
                {
                    "value": 75000.0,
                    "date_of_birth": "10-12-1975",
                    "payment_deadline": 18,
                },
            ]
        }

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 3
        assert data["summary"]["total_simulations"] == 3

        # Check that all results have required fields
        for result in data["results"]:
            assert "total_value_to_pay" in result
            assert "monthly_payment_amount" in result
            assert "total_interest" in result
            assert result["total_value_to_pay"] > 0
            assert result["monthly_payment_amount"] > 0

    def test_batch_summary_statistics(self, client):
        """Test that batch summary contains correct statistics."""
        payload = {
            "simulations": [
                {
                    "value": 10000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 12,
                },
                {
                    "value": 20000.0,
                    "date_of_birth": "20-03-1985",
                    "payment_deadline": 24,
                },
            ]
        }

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        summary = data["summary"]
        assert summary["total_simulations"] == 2
        assert "processing_time_ms" in summary
        assert "average_loan_value" in summary
        assert "average_monthly_payment" in summary
        assert summary["average_loan_value"] == 15000.0  # (10000 + 20000) / 2

    def test_large_batch_processing(self, client):
        """Test processing a larger batch of simulations."""
        simulations = []
        for i in range(100):
            simulations.append(
                {
                    "value": 50000.0 + (i * 1000),
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            )

        payload = {"simulations": simulations}

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert len(data["results"]) == 100
        assert data["summary"]["total_simulations"] == 100
        assert "processing_time_ms" in data["summary"]

    def test_empty_simulations_list(self, client):
        """Test validation for empty simulations list."""
        payload = {"simulations": []}

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        # Flask-RESTX validation returns 'errors' or 'message'
        assert "errors" in data or "message" in data

    def test_missing_simulations_field(self, client):
        """Test validation for missing simulations field."""
        payload = {}

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        # Flask-RESTX validation returns 'errors' or 'message'
        assert "errors" in data or "message" in data

    def test_invalid_simulation_data(self, client):
        """Test validation for invalid simulation data."""
        payload = {
            "simulations": [
                {
                    "value": -1000.0,  # Invalid negative value
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            ]
        }

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        # Flask-RESTX validation returns 'errors' or 'message'
        assert "errors" in data or "message" in data

    def test_mixed_age_groups_batch(self, client):
        """Test batch with customers from different age groups."""
        payload = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "01-01-2000",  # Young (5% rate)
                    "payment_deadline": 24,
                },
                {
                    "value": 50000.0,
                    "date_of_birth": "01-01-1985",  # Middle-aged (3% rate)
                    "payment_deadline": 24,
                },
                {
                    "value": 50000.0,
                    "date_of_birth": "01-01-1975",  # Low interest (2% rate)
                    "payment_deadline": 24,
                },
                {
                    "value": 50000.0,
                    "date_of_birth": "01-01-1955",  # Senior (4% rate)
                    "payment_deadline": 24,
                },
            ]
        }

        response = client.post(
            "/loans/simulate", json=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert len(data["results"]) == 4
        results = data["results"]

        # Different age groups should have different total amounts due to different rates
        # Young customer should pay more than middle-aged due to higher interest
        assert results[0]["total_value_to_pay"] > results[1]["total_value_to_pay"]

        # Low interest customer should pay least
        assert results[2]["total_value_to_pay"] < results[1]["total_value_to_pay"]
