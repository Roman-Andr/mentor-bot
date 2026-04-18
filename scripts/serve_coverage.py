#!/usr/bin/env python3
"""Generate unified coverage dashboard and serve it via HTTP."""

import http.server
import os
import socketserver
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

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
PORT = 8765

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mentor Bot - Unified Coverage Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}
        .summary {{
            background: #fff;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .summary h2 {{
            font-size: 18px;
            color: #333;
        }}
        .total-badge {{
            background: {total_color};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 20px;
            font-weight: bold;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background: #f8f9fa;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            color: #555;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 14px 16px;
            border-top: 1px solid #eee;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .service-name {{
            font-weight: 500;
            color: #333;
        }}
        .coverage-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 6px;
        }}
        .coverage-fill {{
            height: 100%;
            background: {color};
            border-radius: 4px;
        }}
        .coverage-text {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }}
        .percentage {{
            font-weight: 600;
            color: {color};
        }}
        .btn {{
            display: inline-block;
            padding: 6px 14px;
            background: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 13px;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #0052a3;
        }}
        .btn-disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .btn-disabled:hover {{
            background: #ccc;
        }}
        .no-data {{
            color: #999;
            font-style: italic;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Mentor Bot - Coverage Report</h1>
        <p class="subtitle">United coverage report for all microservices</p>

        <div class="summary">
            <div class="summary-header">
                <h2>Overall Coverage</h2>
                <span class="total-badge">{total_pct:.1f}%</span>
            </div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_lines:,}</div>
                    <div class="stat-label">Total Lines</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_covered:,}</div>
                    <div class="stat-label">Covered Lines</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{service_count}</div>
                    <div class="stat-label">Services</div>
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Service</th>
                    <th style="width: 180px;">Coverage</th>
                    <th style="width: 100px;">Lines</th>
                    <th style="width: 80px;">Report</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <p class="footer">Generated on {timestamp} • Reports served at http://localhost:{port}</p>
    </div>
</body>
</html>
"""

ROW_TEMPLATE = """<tr>
    <td><span class="service-name">{service}</span></td>
    <td>
        <div class="coverage-text">
            <span>{covered:,} / {lines:,}</span>
            <span class="percentage">{pct:.1f}%</span>
        </div>
        <div class="coverage-bar">
            <div class="coverage-fill" style="width: {pct:.1f}%; background: {color};"></div>
        </div>
    </td>
    <td>{lines:,}</td>
    <td>{link}</td>
</tr>"""

NO_DATA_ROW = """<tr>
    <td><span class="service-name">{service}</span></td>
    <td colspan="3" class="no-data">No coverage data available</td>
</tr>"""


def get_color(pct: float) -> str:
    """Return color based on coverage percentage."""
    if pct >= 80:
        return "#28a745"
    if pct >= 60:
        return "#ffc107"
    return "#dc3545"


def parse_coverage_xml(xml_path: str) -> tuple[int, int] | None:
    """Parse coverage XML and return (lines, covered) or None if error."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        lines_valid = root.get("lines-valid")
        lines_covered = root.get("lines-covered")

        if lines_valid is not None and lines_covered is not None:
            return (int(lines_valid), int(lines_covered))

        line_rate = root.get("line-rate")
        if line_rate is not None and lines_valid is not None:
            lines = int(lines_valid)
            covered = int(lines * float(line_rate))
            return (lines, covered)
    except Exception:
        pass
    return None


def generate_dashboard() -> Path:
    """Generate the unified coverage dashboard HTML."""
    total_lines = 0
    total_covered = 0
    rows = []
    service_count = 0
    timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for svc in SERVICES:
        xml_path = os.path.join(REPORTS_DIR, f"{svc}.xml")
        html_path = f"{svc}-html/index.html"
        html_full_path = os.path.join(REPORTS_DIR, html_path)

        if not os.path.exists(xml_path):
            rows.append(NO_DATA_ROW.format(service=svc))
            continue

        result = parse_coverage_xml(xml_path)
        if result is None:
            rows.append(NO_DATA_ROW.format(service=svc))
            continue

        lines, covered = result
        total_lines += lines
        total_covered += covered
        service_count += 1
        pct = (covered / lines * 100) if lines > 0 else 0
        color = get_color(pct)

        if os.path.exists(html_full_path):
            link = f'<a href="{html_path}" class="btn">View →</a>'
        else:
            link = '<span class="btn btn-disabled">N/A</span>'

        rows.append(ROW_TEMPLATE.format(
            service=svc,
            lines=lines,
            covered=covered,
            pct=pct,
            color=color,
            link=link
        ))

    total_pct = (total_covered / total_lines * 100) if total_lines > 0 else 0
    total_color = get_color(total_pct)

    html = HTML_TEMPLATE.format(
        total_lines=total_lines,
        total_covered=total_covered,
        total_pct=total_pct,
        total_color=total_color,
        color=total_color,
        service_count=service_count,
        rows="\n".join(rows),
        timestamp=timestamp,
        port=PORT
    )

    index_path = Path(REPORTS_DIR) / "index.html"
    index_path.write_text(html)
    return index_path


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Suppress request logging."""

    def log_message(self, format, *args):
        pass


def main():
    reports_dir = Path(REPORTS_DIR)
    if not reports_dir.exists():
        print(f"Error: {REPORTS_DIR} directory not found. Run 'make coverage' first.")
        sys.exit(1)

    index_path = generate_dashboard()
    print(f"Generated: {index_path}")

    os.chdir(REPORTS_DIR)

    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\nServing coverage reports at {url}")
        print("Press Ctrl+C to stop")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
