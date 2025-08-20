"""
Swagger API models for documentation using Flask-RESTX.
"""

from flask_restx import fields


def create_api_models(api):
    """Create and register API models for Swagger documentation."""

    # Single loan simulation item
    loan_simulation_item = api.model(
        "LoanSimulationItem",
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

    # Input model for loan simulation request (supports both single and batch)
    loan_simulation_request = api.model(
        "LoanSimulationRequest",
        {
            "simulations": fields.List(
                fields.Nested(loan_simulation_item),
                required=True,
                description="List of loan simulations to process (1 to 10000 items)",
                example=[
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
                ],
                min_items=1,
                max_items=10000,
            )
        },
    )

    # Single simulation result
    loan_simulation_result = api.model(
        "LoanSimulationResult",
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

    # Batch simulation response
    loan_simulation_response = api.model(
        "LoanSimulationResponse",
        {
            "results": fields.List(
                fields.Nested(loan_simulation_result),
                required=True,
                description="List of loan simulation results",
                example=[
                    {
                        "total_value_to_pay": 51577.45,
                        "monthly_payment_amount": 2149.06,
                        "total_interest": 1577.45,
                    },
                    {
                        "total_value_to_pay": 31523.76,
                        "monthly_payment_amount": 875.66,
                        "total_interest": 1523.76,
                    },
                ],
            ),
            "summary": fields.Nested(
                api.model(
                    "BatchSummary",
                    {
                        "total_simulations": fields.Integer(
                            description="Total number of simulations processed",
                            example=2,
                        ),
                        "processing_time_ms": fields.Float(
                            description="Processing time in milliseconds",
                            example=45.2,
                        ),
                        "average_loan_value": fields.Float(
                            description="Average loan value across all simulations",
                            example=40000.0,
                        ),
                        "average_monthly_payment": fields.Float(
                            description="Average monthly payment across all simulations",
                            example=1512.36,
                        ),
                    },
                ),
                description="Summary statistics for the batch processing",
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
