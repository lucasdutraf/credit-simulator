from flask import request
from flask_restx import Namespace, Resource
from datetime import datetime
import time
import statistics
from marshmallow import ValidationError
from .schemas import BatchLoanSimulationSchema
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
        Process batch loan simulations with age-based interest rates

        This endpoint processes multiple loan simulations in a single request.
        It supports batch processing of up to 10,000 loan simulations for efficiency.

        Features:
        - Batch processing: 1 to 10,000 simulations per request
        - Performance optimized: Efficient processing for large batches
        - Summary statistics: Aggregate metrics across all simulations
        - Age-based interest rates: Different rates for different age groups

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
            start_time = time.time()

            payload = request.get_json()

            if payload is None:
                api.abort(400, "JSON payload is required")

            schema = BatchLoanSimulationSchema()
            try:
                validated_data = schema.load(payload)
            except ValidationError as err:
                api.abort(400, "Validation failed", details=err.messages)

            simulations = validated_data["simulations"]

            # Process batch simulations
            results = []
            loan_values = []
            monthly_payments = []

            for simulation in simulations:
                value = simulation["value"]
                date_of_birth = simulation["date_of_birth"]
                payment_deadline = simulation["payment_deadline"]

                birth_date = datetime.strptime(date_of_birth, "%d-%m-%Y")

                simulation_data = LoanSimulator.simulate_loan(
                    loan_value=value,
                    birth_date=birth_date,
                    payment_deadline_months=payment_deadline,
                )

                result = {
                    "total_value_to_pay": simulation_data["total_value_to_pay"],
                    "monthly_payment_amount": simulation_data["monthly_payment"],
                    "total_interest": simulation_data["total_interest"],
                }

                results.append(result)
                loan_values.append(value)
                monthly_payments.append(simulation_data["monthly_payment"])

            processing_time = (
                time.time() - start_time
            ) * 1000  # Convert to milliseconds

            summary = {
                "total_simulations": len(results),
                "processing_time_ms": round(processing_time, 2),
                "average_loan_value": (
                    round(statistics.mean(loan_values), 2) if loan_values else 0
                ),
                "average_monthly_payment": (
                    round(statistics.mean(monthly_payments), 2)
                    if monthly_payments
                    else 0
                ),
            }

            response = {"results": results, "summary": summary}

            return response, 200

        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


# Keep the Blueprint for backwards compatibility if needed
from flask import Blueprint

loan_blueprint = Blueprint("loans", __name__)
