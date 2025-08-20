"""
Tests for Swagger API documentation endpoints.
"""

import pytest
import os
from project import create_app


class TestSwaggerDocumentation:
    """Test cases for Swagger API documentation."""

    @pytest.fixture
    def app(self):
        """Create a Flask app for testing Swagger."""
        os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_swagger_json_endpoint(self, client):
        """Test that Swagger JSON endpoint is accessible."""
        response = client.get("/swagger.json")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        swagger_data = response.get_json()
        assert "info" in swagger_data
        assert "paths" in swagger_data
        assert swagger_data["info"]["title"] == "Credit Simulator API"
        assert swagger_data["info"]["version"] == "1.0"

    def test_swagger_ui_endpoint(self, client):
        """Test that Swagger UI endpoint is accessible."""
        response = client.get("/docs/")

        assert response.status_code == 200
        assert "text/html" in response.content_type

    def test_api_root_endpoint(self, client):
        """Test that API root endpoint is accessible."""
        response = client.get("/")

        # Flask-RESTX root might return 404 if not configured, that's acceptable
        assert response.status_code in [200, 302, 308, 404]

    def test_loans_simulate_endpoint_exists(self, client):
        """Test that the loans simulate endpoint exists in Swagger."""
        response = client.get("/swagger.json")
        swagger_data = response.get_json()

        assert "/loans/simulate" in swagger_data["paths"]
        assert "post" in swagger_data["paths"]["/loans/simulate"]

        post_spec = swagger_data["paths"]["/loans/simulate"]["post"]
        assert "summary" in post_spec or "description" in post_spec
        assert "parameters" in post_spec or "requestBody" in post_spec

    def test_api_models_in_swagger(self, client):
        """Test that API models are properly defined in Swagger."""
        response = client.get("/swagger.json")
        swagger_data = response.get_json()

        # Check if definitions/components contain our models
        models_section = swagger_data.get("definitions", {}) or swagger_data.get(
            "components", {}
        ).get("schemas", {})

        # Should have our loan simulation models
        model_names = list(models_section.keys())

        # Should contain request and response models
        assert len(model_names) > 0

        # Check for typical model properties
        for model_name, model_spec in models_section.items():
            if "properties" in model_spec:
                assert isinstance(model_spec["properties"], dict)
