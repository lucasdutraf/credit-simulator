from flask import request, Blueprint
from flask_restx import Namespace, Resource
from datetime import datetime
import time
import statistics
from marshmallow import ValidationError
from .schemas import BatchLoanSimulationSchema, SingleLoanSimulationSchema
from .utils.loan_simulator import LoanSimulator
from .swagger_models import create_api_models

# Create namespace for loan operations
api = Namespace(
    "loans",
    description=("Loan simulation operations with age-based interest rates"),
    path="/loans",
)

# Create and register API models
models = create_api_models(api)


@api.route("/simulate")
class BatchLoanSimulation(Resource):
    @api.doc("simulate_batch_loans")
    @api.expect(models["loan_simulation_request"], validate=True)
    @api.response(200, "Success", models["loan_simulation_response"])
    @api.response(400, "Validation Error", models["error_response"])
    @api.response(500, "Internal Server Error", models["error_response"])
    def post(self):
        """
        Process multiple loan simulations with intelligent parallel processing

        This endpoint processes multiple loan simulations in a single request
        using parallel processing strategies optimized for different batch sizes
        to maximize performance.

        Processing Strategies:
        - Small batches (1-20): Sequential processing (minimal overhead)
        - Medium batches (21-100): Parallel processing with optimized worker count
        - Large batches (101-500): Parallel processing with memory optimization
        - Very large batches (500+): Chunked parallel processing with memory management

        Features:
        - Parallel processing: Multi-core CPU utilization for faster computation
        - Intelligent batching: Automatic strategy selection based on batch size
        - High performance: Up to 4x faster for large batches on multi-core systems
        - Memory efficient: Chunked processing prevents memory overflow
        - Summary statistics: Aggregate metrics across all simulations
        - Age-based interest rates: Different rates for different age groups

        Performance Benefits:
        - CPU utilization: Leverages all available CPU cores
        - Scalability: Handles 1 to 10,000 simulations efficiently
        - Throughput: Significantly improved processing speed for batches

        Interest rates are determined by customer age:
        - Until 25 years: 5% annual
        - 26 to 40 years: 3% annual
        - 41 to 60 years: 2% annual
        - 60+ years: 4% annual

        The monthly payment is calculated using the compound interest formula:
        monthly_payment = (loan_value * (yearly_rate / 12)) /
                         (1 - (1 + (yearly_rate / 12))^(-payment_deadline))
        """
        # Check for JSON payload
        payload = request.get_json()
        if payload is None:
            api.abort(400, "JSON payload is required")

        # Validate input data
        schema = BatchLoanSimulationSchema()
        try:
            validated_data = schema.load(payload)
        except ValidationError as err:
            api.abort(400, "Validation failed", details=err.messages)

        try:
            start_time = time.time()

            simulations = validated_data["simulations"]
            batch_size = len(simulations)

            # Determine optimal processing strategy
            strategy = LoanSimulator.get_optimal_processing_strategy(batch_size)

            # Process simulations based on strategy
            if strategy == "sequential":
                # Small batches - use sequential processing
                # (avoids multiprocessing overhead)
                simulation_results = []
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
                    simulation_results.append(simulation_data)

            elif strategy == "parallel_small":
                # Medium batches - parallel processing with optimized worker count
                simulation_results = LoanSimulator.simulate_batch_parallel(
                    simulations, max_workers=4
                )

            elif strategy == "parallel_medium":
                # Large batches - parallel processing with more workers
                simulation_results = LoanSimulator.simulate_batch_parallel(
                    simulations, max_workers=6
                )

            else:  # parallel_chunked
                # Very large batches - chunked parallel processing
                simulation_results = LoanSimulator.simulate_batch_chunked_parallel(
                    simulations, chunk_size=100, max_workers=8
                )

            # Transform results for response
            results = []
            loan_values = []
            monthly_payments = []

            for simulation_data in simulation_results:
                result = {
                    "total_value_to_pay": simulation_data["total_value_to_pay"],
                    "monthly_payment_amount": simulation_data["monthly_payment"],
                    "total_interest": simulation_data["total_interest"],
                }
                results.append(result)
                loan_values.append(simulation_data["loan_value"])
                monthly_payments.append(simulation_data["monthly_payment"])

            processing_time = (time.time() - start_time) * 1000

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


@api.route("/simulate-single")
class SingleLoanSimulation(Resource):
    @api.doc("simulate_single_loan")
    @api.expect(models["single_loan_request"], validate=True)
    @api.response(200, "Success", models["single_loan_response"])
    @api.response(400, "Validation Error", models["error_response"])
    @api.response(500, "Internal Server Error", models["error_response"])
    def post(self):
        """
        Process a single loan simulation with age-based interest rates

        This endpoint processes a single loan simulation request with optimized
        performance for individual calculations.

        Features:
        - Single loan processing: Optimized for individual simulations
        - Fast response: No batching overhead for single calculations
        - Age-based interest rates: Different rates for different age groups
        - Input validation: Comprehensive validation using Marshmallow schemas

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

            schema = SingleLoanSimulationSchema()
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

            # Remove unused processing_time variable
            result = {
                "total_value_to_pay": simulation_data["total_value_to_pay"],
                "monthly_payment_amount": simulation_data["monthly_payment"],
                "total_interest": simulation_data["total_interest"],
            }

            return result, 200

        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


# Keep the Blueprint for backwards compatibility if needed
loan_blueprint = Blueprint("loans", __name__)
