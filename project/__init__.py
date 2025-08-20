import os

from flask import Flask
from flask_restx import Api

from project.api.views import api as loans_api


# instantiate the app
def create_app(script_info=None):
    # Instantiate the app
    app = Flask(__name__)

    # Set Configuration
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # Initialize Flask-RESTX API with Swagger documentation
    api = Api(
        app,
        version="1.0",
        title="Credit Simulator API",
        description="""
        A comprehensive loan simulation API with age-based interest rate calculations.
        
        ## Features
        - **Age-Based Interest Rates**: Different rates for different age groups
        - **Compound Interest Calculation**: Accurate monthly payment calculations
        - **Input Validation**: Robust validation using Marshmallow schemas
        - **Comprehensive Documentation**: Interactive Swagger documentation
        
        ## Interest Rate Tiers
        - **Until 25 years**: 5% annual interest rate
        - **26 to 40 years**: 3% annual interest rate
        - **41 to 60 years**: 2% annual interest rate
        - **60+ years**: 4% annual interest rate
        
        ## Monthly Payment Formula
        The monthly payment is calculated using the compound interest formula:
        ```
        monthly_payment = (loan_value * (yearly_rate / 12)) / 
                         (1 - (1 + (yearly_rate / 12))^(-payment_deadline))
        ```
        """,
        doc="/docs/",  # Swagger UI endpoint
        validate=True,
        ordered=True,
    )

    # Add namespaces
    api.add_namespace(loans_api)

    # shell context for flask cli
    @app.shell_context_processor
    def shell_context():
        return {"app": app, "api": api}

    return app
