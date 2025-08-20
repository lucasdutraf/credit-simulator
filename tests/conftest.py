"""
Shared test configuration and fixtures.
"""

import pytest
from flask import Flask
from project.api.views import loan_blueprint


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing."""
    app = Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
            "DEBUG": False,
            "WTF_CSRF_ENABLED": False,
        }
    )

    # Register blueprints
    app.register_blueprint(loan_blueprint, url_prefix="/loans")

    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask app's CLI commands."""
    return app.test_cli_runner()


# Sample test data fixtures
@pytest.fixture
def valid_loan_data():
    """Sample valid loan simulation data."""
    return {"value": 50000.0, "date_of_birth": "15-06-1990", "payment_deadline": 24}


@pytest.fixture
def young_customer_data():
    """Sample data for young customer (5% interest rate)."""
    return {"value": 25000.0, "date_of_birth": "01-01-2000", "payment_deadline": 18}


@pytest.fixture
def middle_aged_customer_data():
    """Sample data for middle-aged customer (3% interest rate)."""
    return {"value": 40000.0, "date_of_birth": "15-06-1985", "payment_deadline": 30}


@pytest.fixture
def senior_customer_data():
    """Sample data for senior customer (4% interest rate)."""
    return {"value": 30000.0, "date_of_birth": "20-03-1955", "payment_deadline": 24}


@pytest.fixture
def low_interest_customer_data():
    """Sample data for low interest customer (2% interest rate)."""
    return {"value": 35000.0, "date_of_birth": "10-08-1975", "payment_deadline": 36}
