#!/usr/bin/env python3
"""
Test runner script for the credit simulator application.
"""
import sys
import subprocess


def run_tests():
    """Run all tests using pytest."""
    try:
        # Run pytest with coverage if available
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], check=False
        )

        return result.returncode
    except FileNotFoundError:
        print("pytest not found. Please install pytest:")
        print("pip install pytest pytest-flask")
        return 1


def run_specific_test(test_file):
    """Run a specific test file."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", f"tests/{test_file}", "-v"], check=False
        )

        return result.returncode
    except FileNotFoundError:
        print("pytest not found. Please install pytest:")
        print("pip install pytest pytest-flask")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        if not test_file.startswith("test_"):
            test_file = f"test_{test_file}"
        if not test_file.endswith(".py"):
            test_file = f"{test_file}.py"

        print(f"Running tests in {test_file}...")
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        print("Running all tests...")
        exit_code = run_tests()

    sys.exit(exit_code)
