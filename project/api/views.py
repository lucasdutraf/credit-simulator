from flask import Blueprint, request, jsonify
from datetime import datetime
from marshmallow import ValidationError
from .schemas import LoanSimulationSchema
from .utils.loan_simulator import LoanSimulator

loan_blueprint = Blueprint("loans", __name__)


@loan_blueprint.post("/simulate")
def simulate_loan():
    try:
        payload = request.get_json()

        if payload is None:
            return {"error": "JSON payload is required"}, 400

        schema = LoanSimulationSchema()
        try:
            validated_data = schema.load(payload)
        except ValidationError as err:
            return {"error": "Validation failed", "details": err.messages}, 400

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

        return jsonify(simulation_result), 200

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500
