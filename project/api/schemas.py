from marshmallow import Schema, fields, validates, ValidationError, pre_load, EXCLUDE
from datetime import datetime


class LoanSimulationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

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

    @pre_load
    def validate_types(self, data, **kwargs):
        """Validate types before processing."""
        if "value" in data and isinstance(data["value"], str):
            raise ValidationError({"value": ["Value must be a number, not a string"]})
        if "payment_deadline" in data:
            if isinstance(data["payment_deadline"], str):
                raise ValidationError(
                    {
                        "payment_deadline": [
                            "Payment deadline must be an integer, not a string"
                        ]
                    }
                )
            elif isinstance(data["payment_deadline"], float):
                raise ValidationError(
                    {
                        "payment_deadline": [
                            "Payment deadline must be an integer, not a float"
                        ]
                    }
                )
        return data

    @validates("date_of_birth")
    def validate_date_of_birth(self, value):
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise ValidationError("Date of birth must be in DD-MM-YYYY format")
