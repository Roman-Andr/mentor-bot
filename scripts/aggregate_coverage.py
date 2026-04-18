#!/usr/bin/env python3
"""
Aggregate coverage reports from all services into a united summary.
"""

import os
import sys
import xml.etree.ElementTree as ET

SERVICES = [
    "auth_service",
    "checklists_service",
    "escalation_service",
    "feedback_service",
    "knowledge_service",
    "meeting_service",
    "notification_service",
    "telegram_bot",
]

REPORTS_DIR = ".coverage-reports"


def parse_coverage_xml(xml_path: str) -> tuple[int, int] | None:
    """Parse coverage XML and return (lines, covered) or None if error."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Coverage.py / pytest-cov Cobertura format: attributes on root <coverage> element
        lines_valid = root.get("lines-valid")
        lines_covered = root.get("lines-covered")

        if lines_valid is not None and lines_covered is not None:
            return (int(lines_valid), int(lines_covered))

        # Alternative: use line-rate and lines-valid to calculate
        line_rate = root.get("line-rate")
        if line_rate is not None and lines_valid is not None:
            lines = int(lines_valid)
            covered = int(lines * float(line_rate))
            return (lines, covered)

    except Exception as e:
        print(f"Error parsing {xml_path}: {e}", file=sys.stderr)
        return None

    return None


def main():
    total_lines = 0
    total_covered = 0

    print(f"{'Service':<20} {'Lines':>10} {'Covered':>10} {'Percent':>10}")
    print("-" * 52)

    for svc in SERVICES:
        xml_path = os.path.join(REPORTS_DIR, f"{svc}.xml")

        if not os.path.exists(xml_path):
            print(f"{svc:<20} No report found")
            continue

        result = parse_coverage_xml(xml_path)
        if result is None:
            print(f"{svc:<20} Failed to parse")
            continue

        lines, covered = result
        total_lines += lines
        total_covered += covered

        pct = (covered / lines * 100) if lines > 0 else 0
        print(f"{svc:<20} {lines:>10} {covered:>10} {pct:>9.1f}%")

    print("-" * 52)
    if total_lines > 0:
        total_pct = (total_covered / total_lines * 100)
        print(f'{"TOTAL":<20} {total_lines:>10} {total_covered:>10} {total_pct:>9.1f}%')

    return 0


if __name__ == "__main__":
    sys.exit(main())
