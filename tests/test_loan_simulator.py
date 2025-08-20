"""
Tests for the loan_simulator utility module.
"""

import pytest
from datetime import datetime
from project.api.utils.loan_simulator import LoanSimulator


class TestLoanSimulator:
    """Test cases for the LoanSimulator class."""

    def test_calculate_age_current_year_birthday_passed(self):
        """Test age calculation when birthday has passed this year."""
        # Birth date: January 1, 1990
        birth_date = datetime(1990, 1, 1)
        # Mock current date as December 31, 2023
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 12, 31)}),
            )
            age = LoanSimulator.calculate_age(birth_date)
            assert age == 33

    def test_calculate_age_current_year_birthday_not_passed(self):
        """Test age calculation when birthday hasn't passed this year."""
        # Birth date: December 31, 1990
        birth_date = datetime(1990, 12, 31)
        # Mock current date as June 15, 2023
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 6, 15)}),
            )
            age = LoanSimulator.calculate_age(birth_date)
            assert age == 32

    def test_get_interest_rate_by_age_under_25(self):
        """Test interest rate for customers under 25."""
        rate = LoanSimulator.get_interest_rate_by_age(20)
        assert rate == 0.05

        rate = LoanSimulator.get_interest_rate_by_age(25)
        assert rate == 0.05

    def test_get_interest_rate_by_age_26_to_40(self):
        """Test interest rate for customers aged 26-40."""
        rate = LoanSimulator.get_interest_rate_by_age(26)
        assert rate == 0.03

        rate = LoanSimulator.get_interest_rate_by_age(35)
        assert rate == 0.03

        rate = LoanSimulator.get_interest_rate_by_age(40)
        assert rate == 0.03

    def test_get_interest_rate_by_age_41_to_60(self):
        """Test interest rate for customers aged 41-60."""
        rate = LoanSimulator.get_interest_rate_by_age(41)
        assert rate == 0.02

        rate = LoanSimulator.get_interest_rate_by_age(50)
        assert rate == 0.02

        rate = LoanSimulator.get_interest_rate_by_age(60)
        assert rate == 0.02

    def test_get_interest_rate_by_age_over_60(self):
        """Test interest rate for customers over 60."""
        rate = LoanSimulator.get_interest_rate_by_age(61)
        assert rate == 0.04

        rate = LoanSimulator.get_interest_rate_by_age(75)
        assert rate == 0.04

    def test_get_interest_rate_by_age_edge_cases(self):
        """Test interest rate for edge cases (very young/old)."""
        rate = LoanSimulator.get_interest_rate_by_age(0)
        assert rate == 0.05

        rate = LoanSimulator.get_interest_rate_by_age(150)
        assert rate == 0.04

    def test_calculate_monthly_fee_with_interest(self):
        """Test monthly payment calculation with interest."""
        loan_value = 10000.0
        annual_interest_rate = 0.12  # 12% annual
        payment_deadline_months = 12

        monthly_payment = LoanSimulator.calculate_monthly_fee(
            loan_value, annual_interest_rate, payment_deadline_months
        )

        # Expected calculation:
        # monthly_rate = 0.12 / 12 = 0.01
        # denominator = 1 - (1.01)^(-12) = 0.11255
        # monthly_payment = (10000 * 0.01) / 0.11255 = 888.49
        assert abs(monthly_payment - 888.49) < 0.01

    def test_calculate_monthly_fee_zero_interest(self):
        """Test monthly payment calculation with zero interest."""
        loan_value = 12000.0
        annual_interest_rate = 0.0
        payment_deadline_months = 12

        monthly_payment = LoanSimulator.calculate_monthly_fee(
            loan_value, annual_interest_rate, payment_deadline_months
        )

        # With zero interest, monthly payment = loan_value / months
        expected_payment = 12000.0 / 12
        assert monthly_payment == expected_payment

    def test_calculate_total_value_to_pay(self):
        """Test total value calculation."""
        monthly_payment = 500.0
        payment_deadline_months = 24

        total_value = LoanSimulator.calculate_total_value_to_pay(
            monthly_payment, payment_deadline_months
        )

        assert total_value == 12000.0

    def test_simulate_loan_young_customer(self):
        """Test complete loan simulation for young customer (5% rate)."""
        loan_value = 50000.0
        birth_date = datetime(2000, 1, 1)  # 23-24 years old
        payment_deadline_months = 24

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 6, 15)}),
            )

            result = LoanSimulator.simulate_loan(
                loan_value, birth_date, payment_deadline_months
            )

        assert result["loan_value"] == loan_value
        assert result["customer_age"] == 23
        assert result["annual_interest_rate"] == 0.05
        assert result["payment_deadline_months"] == payment_deadline_months
        assert "monthly_payment" in result
        assert "total_value_to_pay" in result
        assert "total_interest" in result
        # Check that total interest calculation is correct (with rounding tolerance)
        expected_total_interest = result["total_value_to_pay"] - loan_value
        assert abs(result["total_interest"] - expected_total_interest) < 0.01

    def test_simulate_loan_middle_aged_customer(self):
        """Test complete loan simulation for middle-aged customer (3% rate)."""
        loan_value = 30000.0
        birth_date = datetime(1988, 6, 15)  # 35 years old
        payment_deadline_months = 36

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 6, 15)}),
            )

            result = LoanSimulator.simulate_loan(
                loan_value, birth_date, payment_deadline_months
            )

        assert result["loan_value"] == loan_value
        assert result["customer_age"] == 35
        assert result["annual_interest_rate"] == 0.03
        assert result["payment_deadline_months"] == payment_deadline_months

    def test_simulate_loan_senior_customer(self):
        """Test complete loan simulation for senior customer (4% rate)."""
        loan_value = 20000.0
        birth_date = datetime(1955, 3, 20)  # 68 years old
        payment_deadline_months = 18

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 6, 15)}),
            )

            result = LoanSimulator.simulate_loan(
                loan_value, birth_date, payment_deadline_months
            )

        assert result["loan_value"] == loan_value
        assert result["customer_age"] == 68
        assert result["annual_interest_rate"] == 0.04
        assert result["payment_deadline_months"] == payment_deadline_months

    def test_simulate_loan_low_interest_customer(self):
        """Test complete loan simulation for low interest customer (2% rate)."""
        loan_value = 40000.0
        birth_date = datetime(1975, 8, 10)  # 47-48 years old
        payment_deadline_months = 30

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 6, 15)}),
            )

            result = LoanSimulator.simulate_loan(
                loan_value, birth_date, payment_deadline_months
            )

        assert result["loan_value"] == loan_value
        assert result["customer_age"] == 47
        assert result["annual_interest_rate"] == 0.02
        assert result["payment_deadline_months"] == payment_deadline_months

    def test_simulate_loan_rounding(self):
        """Test that monetary values are properly rounded to 2 decimal places."""
        loan_value = 10000.0
        birth_date = datetime(1990, 1, 1)
        payment_deadline_months = 12

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "project.api.utils.loan_simulator.datetime",
                type("MockDatetime", (), {"now": lambda: datetime(2023, 6, 15)}),
            )

            result = LoanSimulator.simulate_loan(
                loan_value, birth_date, payment_deadline_months
            )

        # Check that monetary values have at most 2 decimal places
        monthly_payment_str = str(result["monthly_payment"])
        total_value_str = str(result["total_value_to_pay"])
        total_interest_str = str(result["total_interest"])

        if "." in monthly_payment_str:
            assert len(monthly_payment_str.split(".")[1]) <= 2
        if "." in total_value_str:
            assert len(total_value_str.split(".")[1]) <= 2
        if "." in total_interest_str:
            assert len(total_interest_str.split(".")[1]) <= 2
