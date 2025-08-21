"""
Loan simulation module for calculating loan terms based on customer age and
loan parameters.
"""

import multiprocessing as mp
from datetime import datetime
from typing import List, Dict, Any
import os


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

    @staticmethod
    def _process_single_simulation(simulation_data: Dict[str, Any]) -> dict:
        """
        Process a single simulation - static method for multiprocessing compatibility.

        Args:
            simulation_data (Dict): Dictionary containing simulation parameters

        Returns:
            dict: Simulation result
        """
        # Convert date string to datetime object
        birth_date = datetime.strptime(simulation_data["date_of_birth"], "%d-%m-%Y")

        return LoanSimulator.simulate_loan(
            loan_value=simulation_data["value"],
            birth_date=birth_date,
            payment_deadline_months=simulation_data["payment_deadline"],
        )

    @classmethod
    def simulate_batch_parallel(
        cls, simulations: List[Dict[str, Any]], max_workers: int = None
    ) -> List[dict]:
        """
        Process multiple loan simulations in parallel using multiprocessing.

        Args:
            simulations (List[Dict]): List of simulation parameters
            max_workers (int): Maximum number of worker processes (default: CPU count)

        Returns:
            List[dict]: List of simulation results
        """
        if max_workers is None:
            # Optimize worker count based on batch size and CPU count
            cpu_count = os.cpu_count() or 1
            max_workers = min(len(simulations), cpu_count, 8)  # Cap at 8 workers

        # For very small batches, use sequential processing to avoid overhead
        if len(simulations) <= 20:
            return [cls._process_single_simulation(sim) for sim in simulations]

        # Use multiprocessing for larger batches
        try:
            with mp.Pool(processes=max_workers) as pool:
                results = pool.map(cls._process_single_simulation, simulations)
            return results
        except Exception:
            # Fallback to sequential processing if multiprocessing fails
            return [cls._process_single_simulation(sim) for sim in simulations]

    @classmethod
    def simulate_batch_chunked_parallel(
        cls,
        simulations: List[Dict[str, Any]],
        chunk_size: int = 100,
        max_workers: int = None,
    ) -> List[dict]:
        """
        Process large batches of simulations in chunks using parallel processing.

        Args:
            simulations (List[Dict]): List of simulation parameters
            chunk_size (int): Size of each processing chunk
            max_workers (int): Maximum number of worker processes per chunk

        Returns:
            List[dict]: List of simulation results
        """
        if max_workers is None:
            max_workers = os.cpu_count() or 1

        all_results = []

        # Process simulations in chunks
        for i in range(0, len(simulations), chunk_size):
            chunk = simulations[i : i + chunk_size]
            chunk_results = cls.simulate_batch_parallel(chunk, max_workers)
            all_results.extend(chunk_results)

        return all_results

    @classmethod
    def get_optimal_processing_strategy(cls, batch_size: int) -> str:
        """
        Determine the optimal processing strategy based on batch size.

        Args:
            batch_size (int): Number of simulations to process

        Returns:
            str: Recommended processing strategy
        """
        # Based on benchmark results, parallel processing overhead is significant
        # for small batches, so we use higher thresholds
        if batch_size <= 20:
            return "sequential"
        elif batch_size <= 100:
            return "parallel_small"
        elif batch_size <= 500:
            return "parallel_medium"
        else:
            return "parallel_chunked"
