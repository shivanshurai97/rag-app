import pytest
import sys
import os

def main():
    """Run the test suite with coverage reporting."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the app directory to the Python path
    sys.path.insert(0, script_dir)
    
    # Set up test arguments
    args = [
        "tests",  # Test directory
        "-v",  # Verbose output
        "--cov=app",  # Coverage reporting for app directory
        "--cov-report=term-missing",  # Show missing lines in coverage
        "--cov-report=html",  # Generate HTML coverage report
        "-p", "no:warnings",  # Suppress warnings
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run the tests
    exit_code = pytest.main(args)
    
    # Exit with the same code as pytest
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 