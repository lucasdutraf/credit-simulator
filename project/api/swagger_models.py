"""
Swagger API models for documentation using Flask-RESTX.
"""

from flask_restx import fields


def create_api_models(api):
    """Create and register API models for Swagger documentation."""

    # Input model for loan simulation request
    loan_simulation_request = api.model(
        "LoanSimulationRequest",
        {
            "value": fields.Float(
                required=True,
                description="Loan amount in currency units",
                example=50000.0,
                min=0.01,
            ),
            "date_of_birth": fields.String(
                required=True,
                description="Customer date of birth in DD-MM-YYYY format",
                example="15-06-1990",
                pattern=r"^\d{2}-\d{2}-\d{4}$",
            ),
            "payment_deadline": fields.Integer(
                required=True,
                description="Number of months for loan repayment",
                example=24,
                min=1,
            ),
        },
    )

    # Output model for loan simulation response
    loan_simulation_response = api.model(
        "LoanSimulationResponse",
        {
            "total_value_to_pay": fields.Float(
                required=True,
                description="Total amount to be paid over the loan term",
                example=52631.58,
            ),
            "monthly_payment_amount": fields.Float(
                required=True,
                description="Fixed monthly payment amount",
                example=2192.98,
            ),
            "total_interest": fields.Float(
                required=True,
                description="Total interest amount to be paid",
                example=2631.58,
            ),
        },
    )

    # Error response model
    error_response = api.model(
        "ErrorResponse",
        {
            "error": fields.String(
                required=True,
                description="Error message describing what went wrong",
                example="Validation failed",
            ),
            "details": fields.Raw(
                required=False,
                description="Detailed error information (field-specific errors)",
                example={
                    "value": ["Value must be a positive number"],
                    "date_of_birth": ["Date of birth must be in DD-MM-YYYY format"],
                },
            ),
        },
    )

    return {
        "loan_simulation_request": loan_simulation_request,
        "loan_simulation_response": loan_simulation_response,
        "error_response": error_response,
    }
