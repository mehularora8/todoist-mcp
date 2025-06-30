#!/usr/bin/env python3
"""
Test runner script for todoist-mcp-server

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run tests with coverage
    python run_tests.py --verbose    # Run tests with verbose output
    python run_tests.py --help       # Show help
"""

import subprocess
import sys
import argparse


def run_tests(coverage=False, verbose=False, specific_test=None):
    """Run the test suite with various options"""
    cmd = ["python", "-m", "pytest"]
    
    if coverage:
        cmd.extend(["--cov=todoist_mcp_server", "--cov-report=html", "--cov-report=term-missing"])
    
    if verbose:
        cmd.append("-v")
    
    if specific_test:
        cmd.append(specific_test)
    else:
        cmd.append("tests/")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for todoist-mcp-server")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", "-t", help="Run specific test file or function")
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        coverage=args.coverage,
        verbose=args.verbose,
        specific_test=args.test
    )
    
    if args.coverage and exit_code == 0:
        print("\nCoverage report generated in htmlcov/index.html")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 