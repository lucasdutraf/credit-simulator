from flask import Blueprint, request, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta

example_blueprint = Blueprint("example", __name__)

loan_blueprint = Blueprint("loans", __name__)


@example_blueprint.get("/ping")
def pong():
    return {"message": "works!"}, 200


@loan_blueprint.post("/simulate")
def simulate_loan():
    try:
        payload = request.get_json()

        if not payload:
            return {"error": "JSON payload is required"}, 400

        required_fields = ["value", "date_of_birth", "payment_deadline"]
        missing_fields = [field for field in required_fields if field not in payload]

        if missing_fields:
            return {
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        value = payload.get("value")
        date_of_birth = payload.get("date_of_birth")
        payment_deadline = payload.get("payment_deadline")

        if not isinstance(value, (float)) or value <= 0:
            return {"error": "Value must be a positive number or a float value"}, 400

        if not isinstance(payment_deadline, int) or payment_deadline <= 0:
            return {
                "error": "Payment deadline must be a positive integer (months)"
            }, 400

        try:
            birth_date = datetime.strptime(date_of_birth, "%d-%m-%Y")
        except ValueError:
            return {"error": "Date of birth must be in DD-MM-YYYY format"}, 400

        age = (datetime.now() - birth_date).days // 365

        deadline_date = datetime.now() + relativedelta(months=payment_deadline)
        days_to_deadline = (deadline_date - datetime.now()).days

        interest_rate = 0.15
        total_interest = value * interest_rate * (payment_deadline / 12)
        total_value_to_pay = value + total_interest
        monthly_fee = total_value_to_pay / payment_deadline

        # Simple simulation response
        simulation_result = {
            "total_value_to_pay": round(total_value_to_pay, 2),
            "monthly_fee": round(monthly_fee, 2),
            "interest_rate": interest_rate,
        }

        return jsonify(simulation_result), 200

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500
