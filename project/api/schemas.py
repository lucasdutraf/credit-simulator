from marshmallow import Schema, fields, validates, ValidationError
from datetime import datetime


class LoanSimulationSchema(Schema):
    value = fields.Float(
        required=True,
        validate=lambda x: x > 0,
        error_messages={"invalid": "Value must be a positive number"},
    )
    date_of_birth = fields.Str(required=True)
    payment_deadline = fields.Integer(
        required=True,
        validate=lambda x: x > 0,
        error_messages={"invalid": "Payment deadline must be a positive integer"},
    )

    @validates("date_of_birth")
    def validate_date_of_birth(self, value):
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise ValidationError("Date of birth must be in DD-MM-YYYY format")
