#!/usr/bin/env python3
"""Generate united coverage report from individual service coverage XML files."""

import os
import sys
import xml.etree.ElementTree as ET

services = [
    "auth_service",
    "checklists_service",
    "escalation_service",
    "knowledge_service",
    "meeting_service",
    "notification_service",
    "telegram_bot",
]
total_lines = 0
total_covered = 0

print(f"{'Service':<20} {'Lines':>10} {'Covered':>10} {'Percent':>10}")
print("-" * 52)

for svc in services:
    xml_path = f".coverage-reports/{svc}.xml"
    if not os.path.exists(xml_path):
        print(f"{svc:<20} No report found")
        continue
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        pkg = root.find(".//package")
        if pkg is not None:
            metrics = pkg.find("metrics")
            if metrics is not None:
                lines = int(metrics.get("statements", 0))
                covered = int(metrics.get("coveredstatements", 0))
                total_lines += lines
                total_covered += covered
                pct = (covered / lines * 100) if lines > 0 else 0
                print(f"{svc:<20} {lines:>10} {covered:>10} {pct:>9.1f}%")
            else:
                print(f"{svc:<20} No metrics found")
        else:
            # Try alternative format
            metrics = root.find(".//coverage")
            if metrics is not None:
                lines_val = metrics.get("statements") or metrics.get("lines-valid")
                covered_val = metrics.get("covered") or metrics.get("lines-covered")
                if lines_val and covered_val:
                    lines = int(lines_val)
                    covered = int(covered_val)
                    total_lines += lines
                    total_covered += covered
                    pct = (covered / lines * 100) if lines > 0 else 0
                    print(f"{svc:<20} {lines:>10} {covered:>10} {pct:>9.1f}%")
    except Exception as e:
        print(f"{svc:<20} Error: {e}")

print("-" * 52)
if total_lines > 0:
    total_pct = total_covered / total_lines * 100
    print(f"{'TOTAL':<20} {total_lines:>10} {total_covered:>10} {total_pct:>9.1f}%")
    sys.exit(0 if total_pct > 0 else 1)
else:
    print("No coverage data found")
    sys.exit(1)
