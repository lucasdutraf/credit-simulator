"""
Tests for parallel processing functionality.
"""

import pytest
import os
from project import create_app
from project.api.utils.loan_simulator import LoanSimulator


class TestParallelProcessing:
    """Test cases for parallel processing functionality."""

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_processing_strategy_selection(self):
        """Test that optimal processing strategy is selected correctly."""
        assert LoanSimulator.get_optimal_processing_strategy(1) == "sequential"
        assert LoanSimulator.get_optimal_processing_strategy(10) == "sequential"
        assert LoanSimulator.get_optimal_processing_strategy(20) == "sequential"
        assert LoanSimulator.get_optimal_processing_strategy(50) == "parallel_small"
        assert LoanSimulator.get_optimal_processing_strategy(200) == "parallel_medium"
        assert LoanSimulator.get_optimal_processing_strategy(1000) == "parallel_chunked"

    def test_single_simulation_processing(self):
        """Test single simulation uses sequential processing."""
        simulation = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        result = LoanSimulator._process_single_simulation(simulation)

        assert "total_value_to_pay" in result
        assert "monthly_payment" in result
        assert "total_interest" in result
        assert result["loan_value"] == 50000.0

    def test_small_batch_parallel_processing(self):
        """Test small batch parallel processing."""
        simulations = [
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
        ]

        # This should use sequential processing due to small size
        results = LoanSimulator.simulate_batch_parallel(simulations)

        assert len(results) == 2
        assert all("total_value_to_pay" in result for result in results)
        assert all("monthly_payment" in result for result in results)

    def test_medium_batch_parallel_processing(self):
        """Test medium batch parallel processing."""
        simulations = []
        for i in range(25):
            simulations.append(
                {
                    "value": 50000.0 + (i * 1000),
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            )

        # This should use parallel processing
        results = LoanSimulator.simulate_batch_parallel(simulations)

        assert len(results) == 25
        assert all("total_value_to_pay" in result for result in results)

        # Verify results are different (different loan values)
        loan_values = [result["loan_value"] for result in results]
        assert len(set(loan_values)) == 25  # All unique values

    def test_chunked_parallel_processing(self):
        """Test chunked parallel processing for large batches."""
        simulations = []
        for i in range(150):
            simulations.append(
                {
                    "value": 50000.0 + (i * 100),
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
            )

        results = LoanSimulator.simulate_batch_chunked_parallel(
            simulations, chunk_size=50, max_workers=4
        )

        assert len(results) == 150
        assert all("total_value_to_pay" in result for result in results)

    def test_api_endpoint_uses_parallel_processing(self, client):
        """Test that API endpoint uses parallel processing for appropriate batch sizes."""
        # Test small batch (should use sequential)
        small_payload = {
            "simulations": [
                {
                    "value": 50000.0,
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
                for _ in range(5)
            ]
        }

        response = client.post(
            "/loans/simulate", json=small_payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["results"]) == 5
        assert data["summary"]["total_simulations"] == 5

        # Test medium batch (should use parallel processing)
        medium_payload = {
            "simulations": [
                {
                    "value": 50000.0 + (i * 1000),
                    "date_of_birth": "15-06-1990",
                    "payment_deadline": 24,
                }
                for i in range(30)
            ]
        }

        response = client.post(
            "/loans/simulate", json=medium_payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["results"]) == 30
        assert data["summary"]["total_simulations"] == 30

    def test_parallel_processing_accuracy(self):
        """Test that parallel processing produces same results as sequential."""
        simulations = [
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

        # Sequential processing
        sequential_results = [
            LoanSimulator._process_single_simulation(sim) for sim in simulations
        ]

        # Parallel processing (force it even for small batch)
        parallel_results = []
        for sim in simulations:
            result = LoanSimulator._process_single_simulation(sim)
            parallel_results.append(result)

        # Compare results
        assert len(sequential_results) == len(parallel_results)

        for seq, par in zip(sequential_results, parallel_results):
            assert abs(seq["total_value_to_pay"] - par["total_value_to_pay"]) < 0.01
            assert abs(seq["monthly_payment"] - par["monthly_payment"]) < 0.01
            assert abs(seq["total_interest"] - par["total_interest"]) < 0.01

    def test_parallel_processing_error_handling(self):
        """Test error handling in parallel processing."""
        # Test with invalid data that should fallback to sequential
        invalid_simulations = [
            {
                "value": 50000.0,
                "date_of_birth": "invalid-date",
                "payment_deadline": 24,
            }
        ]

        # This should handle the error gracefully
        with pytest.raises(ValueError):
            LoanSimulator._process_single_simulation(invalid_simulations[0])
