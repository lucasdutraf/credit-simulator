"""
Tests for the schemas module.
"""

import pytest
from marshmallow import ValidationError
from project.api.schemas import LoanSimulationSchema


class TestLoanSimulationSchema:
    """Test cases for the LoanSimulationSchema."""

    def setup_method(self):
        """Set up test fixtures."""
        self.schema = LoanSimulationSchema()

    def test_valid_data(self):
        """Test schema with valid data."""
        valid_data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        result = self.schema.load(valid_data)

        assert result["value"] == 50000.0
        assert result["date_of_birth"] == "15-06-1990"
        assert result["payment_deadline"] == 24

    def test_valid_data_integer_value(self):
        """Test schema with integer value (should be converted to float)."""
        valid_data = {
            "value": 50000,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
        }

        result = self.schema.load(valid_data)

        assert result["value"] == 50000.0
        assert isinstance(result["value"], float)

    def test_missing_required_fields(self):
        """Test schema with missing required fields."""
        # Missing all fields
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({})

        errors = exc_info.value.messages
        assert "value" in errors
        assert "date_of_birth" in errors
        assert "payment_deadline" in errors

    def test_missing_value_field(self):
        """Test schema with missing value field."""
        data = {"date_of_birth": "15-06-1990", "payment_deadline": 24}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "value" in errors
        assert "date_of_birth" not in errors
        assert "payment_deadline" not in errors

    def test_missing_date_of_birth_field(self):
        """Test schema with missing date_of_birth field."""
        data = {"value": 50000.0, "payment_deadline": 24}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "date_of_birth" in errors
        assert "value" not in errors
        assert "payment_deadline" not in errors

    def test_missing_payment_deadline_field(self):
        """Test schema with missing payment_deadline field."""
        data = {"value": 50000.0, "date_of_birth": "15-06-1990"}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "payment_deadline" in errors
        assert "value" not in errors
        assert "date_of_birth" not in errors

    def test_invalid_value_zero(self):
        """Test schema with zero value (should be invalid)."""
        data = {"value": 0.0, "date_of_birth": "15-06-1990", "payment_deadline": 24}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "value" in errors

    def test_invalid_value_negative(self):
        """Test schema with negative value (should be invalid)."""
        data = {"value": -1000.0, "date_of_birth": "15-06-1990", "payment_deadline": 24}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "value" in errors

    def test_invalid_value_string(self):
        """Test schema with string value (should be invalid)."""
        data = {"value": "50000", "date_of_birth": "15-06-1990", "payment_deadline": 24}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "value" in errors

    def test_invalid_payment_deadline_zero(self):
        """Test schema with zero payment_deadline (should be invalid)."""
        data = {"value": 50000.0, "date_of_birth": "15-06-1990", "payment_deadline": 0}

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "payment_deadline" in errors

    def test_invalid_payment_deadline_negative(self):
        """Test schema with negative payment_deadline (should be invalid)."""
        data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": -12,
        }

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "payment_deadline" in errors

    def test_invalid_payment_deadline_float(self):
        """Test schema with float payment_deadline (should be invalid)."""
        data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 12.5,
        }

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "payment_deadline" in errors

    def test_invalid_payment_deadline_string(self):
        """Test schema with string payment_deadline (should be invalid)."""
        data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": "24",
        }

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "payment_deadline" in errors

    def test_valid_date_formats(self):
        """Test schema with various valid date formats."""
        valid_dates = [
            "01-01-1990",
            "31-12-1985",
            "15-06-2000",
            "29-02-1996",  # Leap year
        ]

        for date_str in valid_dates:
            data = {"value": 50000.0, "date_of_birth": date_str, "payment_deadline": 24}

            result = self.schema.load(data)
            assert result["date_of_birth"] == date_str

    def test_invalid_date_format_wrong_separator(self):
        """Test schema with invalid date format (wrong separator)."""
        data = {
            "value": 50000.0,
            "date_of_birth": "15/06/1990",  # Wrong separator
            "payment_deadline": 24,
        }

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "date_of_birth" in errors
        assert "DD-MM-YYYY format" in str(errors["date_of_birth"])

    def test_invalid_date_format_wrong_order(self):
        """Test schema with invalid date format (wrong order)."""
        data = {
            "value": 50000.0,
            "date_of_birth": "1990-06-15",  # Wrong order (YYYY-MM-DD)
            "payment_deadline": 24,
        }

        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)

        errors = exc_info.value.messages
        assert "date_of_birth" in errors
        assert "DD-MM-YYYY format" in str(errors["date_of_birth"])

    def test_invalid_date_format_invalid_date(self):
        """Test schema with invalid date values."""
        invalid_dates = [
            "32-01-1990",  # Invalid day
            "15-13-1990",  # Invalid month
            "29-02-1990",  # Invalid leap year
            "00-01-1990",  # Invalid day (zero)
            "15-00-1990",  # Invalid month (zero)
        ]

        for date_str in invalid_dates:
            data = {"value": 50000.0, "date_of_birth": date_str, "payment_deadline": 24}

            with pytest.raises(ValidationError) as exc_info:
                self.schema.load(data)

            errors = exc_info.value.messages
            assert "date_of_birth" in errors

    def test_invalid_date_format_incomplete(self):
        """Test schema with incomplete date format."""
        incomplete_dates = [
            "15-06",  # Missing year
            "1990",  # Only year
            "15-1990",  # Missing month
            "",  # Empty string
        ]

        for date_str in incomplete_dates:
            data = {"value": 50000.0, "date_of_birth": date_str, "payment_deadline": 24}

            with pytest.raises(ValidationError) as exc_info:
                self.schema.load(data)

            errors = exc_info.value.messages
            assert "date_of_birth" in errors

    def test_edge_case_values(self):
        """Test schema with edge case values."""
        # Very small positive value
        data = {"value": 0.01, "date_of_birth": "15-06-1990", "payment_deadline": 1}
        result = self.schema.load(data)
        assert result["value"] == 0.01
        assert result["payment_deadline"] == 1

        # Very large values
        data = {
            "value": 1000000.0,
            "date_of_birth": "01-01-1900",
            "payment_deadline": 360,  # 30 years
        }
        result = self.schema.load(data)
        assert result["value"] == 1000000.0
        assert result["payment_deadline"] == 360

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored by the schema."""
        data = {
            "value": 50000.0,
            "date_of_birth": "15-06-1990",
            "payment_deadline": 24,
            "extra_field": "should be ignored",
            "another_extra": 123,
        }

        result = self.schema.load(data)

        assert "extra_field" not in result
        assert "another_extra" not in result
        assert len(result) == 3
