"""Tests for the market coverage audit script."""

import sys
from datetime import date
from io import StringIO

from scripts.check_market_coverage import check_coverage, print_coverage_report


def test_print_coverage_report_empty():
    captured = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        print_coverage_report([], "turmeric", "Erode")
    finally:
        sys.stdout = old_stdout

    output = captured.getvalue()
    assert "FPOLink TN — Market Price Coverage Audit" in output
    assert "No records found" in output


def test_print_coverage_report_with_data():
    sample_results = [
        (date(2024, 1, 1), "Erode Mandi", 24),
        (date(2024, 1, 1), "Perundurai Mandi", 18),
        (date(2024, 2, 1), "Erode Mandi", 3),  # sparse month (<5)
    ]

    captured = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        print_coverage_report(sample_results, "turmeric", "Erode")
    finally:
        sys.stdout = old_stdout

    output = captured.getvalue()
    assert "Total records:      45" in output
    assert "Distinct markets:   2" in output
    assert "Erode Mandi" in output
    assert "Perundurai Mandi" in output
    assert "sparse" in output.lower() or "advisory" in output.lower()


def test_check_coverage_query(db):
    # Runs against the test database session
    results = check_coverage(crop="turmeric", district="Erode", db=db)
    assert isinstance(results, list)
