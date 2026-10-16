#!/bin/bash
# Run pattern skill tests
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh -k test_name # Run specific test
#   ./run_tests.sh --cov        # Run with coverage

set -e

# Change to tests directory
cd "$(dirname "$0")"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing test dependencies..."
    pip install -r requirements-test.txt
fi

# Run pytest with any additional arguments
pytest "$@"
