#!/usr/bin/env python3
"""
Aerthos Test Runner

Runs all test suites and generates comprehensive report.
Use this before making changes to ensure nothing breaks.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --web              # Run only web UI tests
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --no-web           # Skip web tests (if Flask not installed)
"""

import sys
import unittest
import argparse
from pathlib import Path
from io import StringIO


class ColoredTextTestResult(unittest.TextTestResult):
    """Test result class with colored output"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_results.append(('PASS', str(test)))
        if self.showAll:
            self.stream.write('\033[92m✓ PASS\033[0m\n')

    def addError(self, test, err):
        super().addError(test, err)
        self.test_results.append(('ERROR', str(test)))
        if self.showAll:
            self.stream.write('\033[91m✗ ERROR\033[0m\n')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results.append(('FAIL', str(test)))
        if self.showAll:
            self.stream.write('\033[91m✗ FAIL\033[0m\n')

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.test_results.append(('SKIP', str(test)))
        if self.showAll:
            self.stream.write('\033[93m⊘ SKIP\033[0m\n')


class ColoredTextTestRunner(unittest.TextTestRunner):
    """Test runner with colored output"""
    resultclass = ColoredTextTestResult


def discover_tests(test_dir, pattern):
    """Discover tests in directory"""
    loader = unittest.TestLoader()
    return loader.discover(test_dir, pattern=pattern)


def run_test_suite(suite_name, test_suite, verbosity=1):
    """Run a test suite and return results"""
    print(f"\n{'='*70}")
    print(f"Running {suite_name}")
    print(f"{'='*70}")

    runner = ColoredTextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)

    return result


def print_summary(all_results):
    """Print comprehensive test summary"""
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}\n")

    total_run = sum(r.testsRun for r in all_results)
    total_failures = sum(len(r.failures) for r in all_results)
    total_errors = sum(len(r.errors) for r in all_results)
    total_skipped = sum(len(r.skipped) for r in all_results)
    total_passed = total_run - total_failures - total_errors - total_skipped

    print(f"Total Tests Run:    {total_run}")
    print(f"\033[92mPassed:            {total_passed}\033[0m")
    print(f"\033[91mFailed:            {total_failures}\033[0m")
    print(f"\033[91mErrors:            {total_errors}\033[0m")
    print(f"\033[93mSkipped:           {total_skipped}\033[0m")

    if total_failures > 0 or total_errors > 0:
        print(f"\n\033[91m{'='*70}")
        print("FAILURES AND ERRORS")
        print(f"{'='*70}\033[0m\n")

        for result in all_results:
            for test, traceback in result.failures:
                print(f"\033[91mFAILURE: {test}\033[0m")
                print(traceback)
                print()

            for test, traceback in result.errors:
                print(f"\033[91mERROR: {test}\033[0m")
                print(traceback)
                print()

    print(f"{'='*70}")
    if total_failures == 0 and total_errors == 0:
        print("\033[92m✓ ALL TESTS PASSED\033[0m")
    else:
        print(f"\033[91m✗ {total_failures + total_errors} TESTS FAILED\033[0m")
    print(f"{'='*70}\n")

    return total_failures + total_errors == 0


def main():
    parser = argparse.ArgumentParser(description='Run Aerthos test suites')
    parser.add_argument('--unit', action='store_true',
                        help='Run only unit tests')
    parser.add_argument('--integration', action='store_true',
                        help='Run only integration tests')
    parser.add_argument('--web', action='store_true',
                        help='Run only web UI tests')
    parser.add_argument('--no-web', action='store_true',
                        help='Skip web UI tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--list', action='store_true',
                        help='List all available tests')

    args = parser.parse_args()

    # Determine verbosity
    verbosity = 2 if args.verbose else 1

    # Get test directory
    test_dir = Path(__file__).parent / 'tests'

    if not test_dir.exists():
        print(f"Error: Test directory not found: {test_dir}")
        return 1

    # List tests if requested
    if args.list:
        print("Available test modules:")
        for test_file in sorted(test_dir.glob('test_*.py')):
            print(f"  - {test_file.name}")
        return 0

    # Determine which tests to run
    all_results = []

    # Unit tests
    if not args.integration and not args.web:
        print("\n" + "="*70)
        print("UNIT TESTS - Core Game Systems")
        print("="*70)

        unit_tests = [
            ('Parser Tests', 'test_parser.py'),
            ('Combat System Tests', 'test_combat.py'),
            ('Game State Tests', 'test_game_state.py'),
            ('Storage Tests', 'test_storage.py'),
            ('Ability Modifiers Tests', 'test_ability_modifiers.py'),
            ('Armor System Tests', 'test_armor_system.py')
        ]

        for suite_name, pattern in unit_tests:
            suite = discover_tests(str(test_dir), pattern=pattern)
            if suite.countTestCases() > 0:
                result = run_test_suite(suite_name, suite, verbosity)
                all_results.append(result)

    # Integration tests
    if args.integration or not (args.unit or args.web):
        print("\n" + "="*70)
        print("INTEGRATION TESTS - End-to-End Scenarios")
        print("="*70)

        suite = discover_tests(str(test_dir), pattern='test_integration.py')
        if suite.countTestCases() > 0:
            result = run_test_suite('Integration Tests', suite, verbosity)
            all_results.append(result)

    # Web UI tests
    if (args.web or not (args.unit or args.integration)) and not args.no_web:
        print("\n" + "="*70)
        print("WEB UI TESTS - Flask API Wrapper")
        print("="*70)

        try:
            import flask
            suite = discover_tests(str(test_dir), pattern='test_web_ui.py')
            if suite.countTestCases() > 0:
                result = run_test_suite('Web UI Tests', suite, verbosity)
                all_results.append(result)
        except ImportError:
            print("\n\033[93mSkipping Web UI tests - Flask not installed\033[0m")
            print("Install with: pip install flask")

    # Print summary
    if all_results:
        success = print_summary(all_results)
        return 0 if success else 1
    else:
        print("\nNo tests found!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
