from flask import Blueprint, request, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta
from marshmallow import ValidationError
from .schemas import LoanSimulationSchema

loan_blueprint = Blueprint("loans", __name__)


@loan_blueprint.post("/simulate")
def simulate_loan():
    try:
        payload = request.get_json()

        if not payload:
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

        age = (datetime.now() - birth_date).days // 365

        deadline_date = datetime.now() + relativedelta(months=payment_deadline)
        days_to_deadline = (deadline_date - datetime.now()).days

        interest_rate = 0.15
        total_interest = value * interest_rate * (payment_deadline / 12)
        total_value_to_pay = value + total_interest
        monthly_fee = total_value_to_pay / payment_deadline

        simulation_result = {
            "total_value_to_pay": round(total_value_to_pay, 2),
            "monthly_fee": round(monthly_fee, 2),
            "interest_rate": interest_rate,
        }

        return jsonify(simulation_result), 200

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500
