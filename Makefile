# Credit Simulator - Makefile
# Convenient commands for development and testing

.PHONY: help test test-local test-docker test-coverage test-watch test-specific clean build run

# Default target
help:
	@echo "Credit Simulator - Available Commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make test-local          Run tests locally (requires venv)"
	@echo "  make test-coverage-local Run tests with coverage locally"
	@echo ""
	@echo "Docker Testing:"
	@echo "  make test-docker         Run all tests in Docker"
	@echo "  make test-coverage       Run tests with coverage in Docker"
	@echo "  make test-watch          Run tests in watch mode (Docker)"
	@echo "  make test-specific FILE=tests/test_schemas.py  Run specific test file (Docker)"
	@echo "  make test-shell          Open interactive shell in test container"
	@echo ""
	@echo "Application:"
	@echo "  make build               Build Docker images"
	@echo "  make run                 Run application with Docker Compose"
	@echo "  make clean               Clean up Docker containers and images"
	@echo ""
	@echo "Examples:"
	@echo "  make test-docker"
	@echo "  make test-specific FILE=tests/test_loan_simulator.py"
	@echo "  make test-coverage"

# Local testing (requires virtual environment)
test-local:
	@echo "Running tests locally..."
	@source venv/bin/activate && python run_tests.py

test-coverage-local:
	@echo "Running tests with coverage locally..."
	@source venv/bin/activate && pytest tests/ --cov=project --cov-report=html --cov-report=term-missing -v

# Docker testing
test-docker:
	@echo "Running tests in Docker..."
	@./run_tests_docker.sh test

test-coverage:
	@echo "Running tests with coverage in Docker..."
	@./run_tests_docker.sh test-coverage

test-watch:
	@echo "Running tests in watch mode..."
	@./run_tests_docker.sh test-watch

test-specific:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify FILE parameter"; \
		echo "Example: make test-specific FILE=tests/test_schemas.py"; \
		exit 1; \
	fi
	@echo "Running specific test: $(FILE)"
	@./run_tests_docker.sh test-specific $(FILE)

test-shell:
	@echo "Opening test shell..."
	@./run_tests_docker.sh test-shell

# Application commands
build:
	@echo "Building Docker images..."
	@docker-compose build

run:
	@echo "Starting application..."
	@docker-compose up

run-detached:
	@echo "Starting application in background..."
	@docker-compose up -d

stop:
	@echo "Stopping application..."
	@docker-compose down

# Cleanup
clean:
	@echo "Cleaning up..."
	@./run_tests_docker.sh clean
	@docker-compose down --rmi all --volumes --remove-orphans

# Quick test - defaults to Docker
test: test-docker

# Development helpers
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

format:
	@echo "Formatting code..."
	@black project/ tests/

lint:
	@echo "Linting code..."
	@flake8 project/ tests/ --max-line-length=88 --extend-ignore=E203,W503

# CI/CD helpers
ci-test:
	@echo "Running CI tests..."
	@docker-compose -f docker-compose.test.yml run --rm test pytest tests/ -v --junitxml=test-results.xml

ci-coverage:
	@echo "Running CI tests with coverage..."
	@docker-compose -f docker-compose.test.yml run --rm test-coverage pytest tests/ --cov=project --cov-report=xml --cov-report=term -v
