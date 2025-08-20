"""
Loan simulation module for calculating loan terms based on customer age and
loan parameters.
"""

from datetime import datetime


class LoanSimulator:
    """
    A class to handle loan simulation calculations including age-based interest rates
    and monthly payment calculations.
    """

    # Age-based interest rate tiers
    INTEREST_RATE_TIERS = {
        (0, 25): 0.05,  # Until 25 years: 5% annual
        (26, 40): 0.03,  # From 26 to 40: 3% annual
        (41, 60): 0.02,  # From 41 to 60: 2% annual
        (61, 999): 0.04,  # From 60+: 4% annual
    }

    @classmethod
    def calculate_age(cls, birth_date: datetime) -> int:
        """
        Calculate age from birth date.

        Args:
            birth_date (datetime): The birth date

        Returns:
            int: Age in years
        """
        today = datetime.now()
        age = today.year - birth_date.year

        # Adjust if birthday hasn't occurred this year
        if today.month < birth_date.month or (
            today.month == birth_date.month and today.day < birth_date.day
        ):
            age -= 1

        return age

    @classmethod
    def get_interest_rate_by_age(cls, age: int) -> float:
        """
        Get annual interest rate based on customer's age.

        Args:
            age (int): Customer's age in years

        Returns:
            float: Annual interest rate as decimal (e.g., 0.05 for 5%)
        """
        for (min_age, max_age), rate in cls.INTEREST_RATE_TIERS.items():
            if min_age <= age <= max_age:
                return rate

        return 0.04

    @classmethod
    def calculate_monthly_fee(
        cls,
        loan_value: float,
        annual_interest_rate: float,
        payment_deadline_months: int,
    ) -> float:
        """
        Calculate monthly payment using the compound interest formula.

        Formula: monthly_fee = (loan_value * (yearly_rate / 12)) /
                              (1 - (1 + (yearly_rate / 12))^(-payment_deadline))

        Args:
            loan_value (float): The principal loan amount
            annual_interest_rate (float): Annual interest rate as decimal
            payment_deadline_months (int): Number of months to repay

        Returns:
            float: Monthly payment amount
        """

        monthly_rate = annual_interest_rate / 12

        if monthly_rate == 0:
            return loan_value / payment_deadline_months

        denominator = 1 - ((1 + monthly_rate) ** (-payment_deadline_months))
        monthly_payment = (loan_value * monthly_rate) / denominator

        return monthly_payment

    @classmethod
    def calculate_total_value_to_pay(
        cls, monthly_payment: float, payment_deadline_months: int
    ) -> float:
        """
        Calculate total amount to be paid over the loan term.

        Args:
            monthly_payment (float): Monthly payment amount
            payment_deadline_months (int): Number of months to repay

        Returns:
            float: Total amount to be paid
        """
        return monthly_payment * payment_deadline_months

    @classmethod
    def simulate_loan(
        cls, loan_value: float, birth_date: datetime, payment_deadline_months: int
    ) -> dict:
        """
        Perform complete loan simulation with all calculations.

        Args:
            loan_value (float): The principal loan amount
            birth_date (datetime): Customer's birth date
            payment_deadline_months (int): Number of months to repay

        Returns:
            dict: Complete loan simulation results
        """
        age = cls.calculate_age(birth_date)

        annual_interest_rate = cls.get_interest_rate_by_age(age)

        monthly_payment = cls.calculate_monthly_fee(
            loan_value, annual_interest_rate, payment_deadline_months
        )

        total_value_to_pay = cls.calculate_total_value_to_pay(
            monthly_payment, payment_deadline_months
        )

        total_interest = total_value_to_pay - loan_value

        return {
            "loan_value": loan_value,
            "customer_age": age,
            "annual_interest_rate": annual_interest_rate,
            "monthly_payment": round(monthly_payment, 2),
            "total_value_to_pay": round(total_value_to_pay, 2),
            "total_interest": round(total_interest, 2),
            "payment_deadline_months": payment_deadline_months,
        }
