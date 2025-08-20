#!/bin/bash

# Docker Test Runner Script for Credit Simulator
# This script provides various ways to run tests using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  test                    Run all tests"
    echo "  test-coverage          Run tests with coverage report"
    echo "  test-specific [FILE]   Run specific test file"
    echo "  test-watch             Run tests in watch mode (continuous)"
    echo "  test-build             Build test image"
    echo "  test-shell             Open interactive shell in test container"
    echo "  clean                  Clean up test containers and images"
    echo ""
    echo "Examples:"
    echo "  $0 test                                    # Run all tests"
    echo "  $0 test-coverage                          # Run tests with coverage"
    echo "  $0 test-specific tests/test_schemas.py    # Run specific test file"
    echo "  $0 test-watch                             # Run tests in watch mode"
    echo ""
}

# Function to build test image
build_test_image() {
    print_status "Building test image..."
    docker-compose -f docker-compose.test.yml build test
    print_success "Test image built successfully"
}

# Function to run all tests
run_tests() {
    print_status "Running all tests..."
    docker-compose -f docker-compose.test.yml run --rm test
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed!"
        exit 1
    fi
}

# Function to run tests with coverage
run_tests_coverage() {
    print_status "Running tests with coverage..."
    docker-compose -f docker-compose.test.yml run --rm test-coverage
    if [ $? -eq 0 ]; then
        print_success "Tests completed with coverage report!"
        print_status "Coverage report saved to htmlcov/ directory"
    else
        print_error "Tests failed!"
        exit 1
    fi
}

# Function to run specific test file
run_specific_test() {
    local test_file=$1
    if [ -z "$test_file" ]; then
        print_error "Please specify a test file"
        echo "Example: $0 test-specific tests/test_schemas.py"
        exit 1
    fi
    
    print_status "Running specific test: $test_file"
    docker-compose -f docker-compose.test.yml run --rm test pytest "$test_file" -v
    if [ $? -eq 0 ]; then
        print_success "Test completed successfully!"
    else
        print_error "Test failed!"
        exit 1
    fi
}

# Function to run tests in watch mode
run_tests_watch() {
    print_status "Running tests in watch mode..."
    print_warning "Press Ctrl+C to stop watching"
    docker-compose -f docker-compose.test.yml run --rm test-watch
}

# Function to open interactive shell
open_test_shell() {
    print_status "Opening interactive shell in test container..."
    docker-compose -f docker-compose.test.yml run --rm test /bin/sh
}

# Function to clean up
cleanup() {
    print_status "Cleaning up test containers and images..."
    docker-compose -f docker-compose.test.yml down --rmi all --volumes --remove-orphans
    print_success "Cleanup completed"
}

# Main script logic
case "${1:-}" in
    "test")
        run_tests
        ;;
    "test-coverage")
        run_tests_coverage
        ;;
    "test-specific")
        run_specific_test "$2"
        ;;
    "test-watch")
        run_tests_watch
        ;;
    "test-build")
        build_test_image
        ;;
    "test-shell")
        open_test_shell
        ;;
    "clean")
        cleanup
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    "")
        print_error "No command specified"
        show_usage
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
