from flask import request
from flask_restx import Namespace, Resource
from datetime import datetime
from marshmallow import ValidationError
from .schemas import LoanSimulationSchema
from .utils.loan_simulator import LoanSimulator
from .swagger_models import create_api_models

# Create namespace for loan operations
api = Namespace(
    "loans",
    description="Loan simulation operations with age-based interest rates",
    path="/loans",
)

# Create and register API models
models = create_api_models(api)


@api.route("/simulate")
class LoanSimulation(Resource):
    @api.doc("simulate_loan")
    @api.expect(models["loan_simulation_request"], validate=True)
    @api.response(200, "Success", models["loan_simulation_response"])
    @api.response(400, "Validation Error", models["error_response"])
    @api.response(500, "Internal Server Error", models["error_response"])
    def post(self):
        """
        Simulate a loan with age-based interest rates

        This endpoint calculates loan simulation details including:
        - Monthly payment amount using compound interest formula
        - Total value to be paid over the loan term
        - Total interest amount

        Interest rates are determined by customer age:
        - Until 25 years: 5% annual
        - 26 to 40 years: 3% annual
        - 41 to 60 years: 2% annual
        - 60+ years: 4% annual

        The monthly payment is calculated using the compound interest formula:
        monthly_payment = (loan_value * (yearly_rate / 12)) /
                         (1 - (1 + (yearly_rate / 12))^(-payment_deadline))
        """
        try:
            payload = request.get_json()

            if payload is None:
                api.abort(400, "JSON payload is required")

            schema = LoanSimulationSchema()
            try:
                validated_data = schema.load(payload)
            except ValidationError as err:
                api.abort(400, "Validation failed", details=err.messages)

            value = validated_data["value"]
            date_of_birth = validated_data["date_of_birth"]
            payment_deadline = validated_data["payment_deadline"]

            birth_date = datetime.strptime(date_of_birth, "%d-%m-%Y")

            simulation_data = LoanSimulator.simulate_loan(
                loan_value=value,
                birth_date=birth_date,
                payment_deadline_months=payment_deadline,
            )

            simulation_result = {
                "total_value_to_pay": simulation_data["total_value_to_pay"],
                "monthly_payment_amount": simulation_data["monthly_payment"],
                "total_interest": simulation_data["total_interest"],
            }

            return simulation_result, 200

        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


# Keep the Blueprint for backwards compatibility if needed
from flask import Blueprint

loan_blueprint = Blueprint("loans", __name__)
