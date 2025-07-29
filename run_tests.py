#!/usr/bin/env python3
"""
Test runner for YouTube Page Builder
"""

import os
import sys
import unittest
from pathlib import Path


def run_all_tests():
    """Run all tests."""
    # Add tests directory to path
    tests_dir = Path(__file__).parent / "tests"
    sys.path.insert(0, str(tests_dir))

    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = str(tests_dir)
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_test(test_module):
    """Run a specific test module."""
    # Add tests directory to path
    tests_dir = Path(__file__).parent / "tests"
    sys.path.insert(0, str(tests_dir))

    # Import and run specific test module
    try:
        module = __import__(test_module)
        suite = unittest.TestLoader().loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"❌ Error importing test module '{test_module}': {e}")
        return False


def run_quick_tests():
    """Run quick tests that don't require external dependencies."""
    print("🧪 Running quick tests...")

    # Add tests directory to path
    tests_dir = Path(__file__).parent / "tests"
    sys.path.insert(0, str(tests_dir))

    # Quick tests that don't require external dependencies
    quick_test_modules = [
        'test_utilities.TestConfigModule',
        'test_create_index.TestCreateIndex',
    ]

    success_count = 0
    total_count = len(quick_test_modules)

    for test_module in quick_test_modules:
        print(f"\n📋 Running {test_module}...")
        try:
            # Import the test class
            module_name, class_name = test_module.split('.')
            module = __import__(module_name)
            test_class = getattr(module, class_name)

            # Run the test class
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=1)
            result = runner.run(suite)

            if result.wasSuccessful():
                success_count += 1
                print(f"✅ {test_module} passed")
            else:
                print(f"❌ {test_module} failed")

        except Exception as e:
            print(f"❌ Error running {test_module}: {e}")

    print(f"\n📊 Quick test results: {success_count}/{total_count} passed")
    return success_count == total_count


def main():
    """Main test runner function."""
    print("🧪 YouTube Page Builder - Test Runner")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "all":
            print("Running all tests...")
            success = run_all_tests()
        elif command == "quick":
            success = run_quick_tests()
        elif command.startswith("test_"):
            print(f"Running specific test: {command}")
            success = run_specific_test(command)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: all, quick, or test_<module_name>")
            return False
    else:
        print("Running quick tests (use 'all' for full test suite)...")
    print(
        "Note: Full test suite requires external dependencies and may have some failures."
    )
    success = run_quick_tests()

    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
