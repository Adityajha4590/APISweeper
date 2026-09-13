import json
from datetime import datetime, timezone


class ReportGenerator:
    """
    Takes the aggregated list of finding dicts (as produced by
    BaseScanner.add_finding across all scanner instances) and
    renders them as JSON (for ui.py to consume) and HTML (human-readable).
    """

    SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    SEVERITY_COLORS = {
        "CRITICAL": "#c0392b",
        "HIGH": "#e67e22",
        "MEDIUM": "#f1c40f",
        "LOW": "#3498db",
    }

    def __init__(self, target_url: str):
        self.target_url = target_url

    def _sorted_findings(self, findings: list[dict]) -> list[dict]:
        return sorted(findings, key=lambda f: self.SEVERITY_ORDER.get(f.get("severity", "LOW"), 99))

    def _count_by_severity(self, findings: list[dict]) -> dict:
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in findings:
            sev = f.get("severity", "LOW")
            if sev in counts:
                counts[sev] += 1
        return counts

    def to_json(self, findings: list[dict], output_path: str = "report.json") -> str:
        report_data = {
            "target": self.target_url,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_findings": len(findings),
            "findings_by_severity": self._count_by_severity(findings),
            "findings": self._sorted_findings(findings),
        }
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
        return output_path

    def to_html(self, findings: list[dict], output_path: str = "report.html") -> str:
        sorted_findings = self._sorted_findings(findings)
        counts = self._count_by_severity(findings)

        rows = ""
        for f in sorted_findings:
            severity = f.get("severity", "LOW")
            color = self.SEVERITY_COLORS.get(severity, "#999999")
            source = f.get("source", "—")
            rows += f"""
            <tr>
                <td><span style="background:{color}; color:white; padding:3px 10px;
                     border-radius:4px; font-weight:bold; font-size:12px;">{severity}</span></td>
                <td>{source}</td>
                <td><code>{f.get('endpoint', '')}</code></td>
                <td>{f.get('description', '')}</td>
            </tr>"""

        summary_badges = "".join(
            f'<span style="background:{self.SEVERITY_COLORS[sev]}; color:white; '
            f'padding:6px 14px; border-radius:6px; margin-right:8px; font-weight:bold;">'
            f'{sev}: {count}</span>'
            for sev, count in counts.items()
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>APISweeper Report — {self.target_url}</title>
    <style>
        body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 40px; background: #f7f8fa; color: #1a1a1a; }}
        h1 {{ color: #1a2b4c; }}
        .meta {{ color: #666; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
        th {{ background: #1a2b4c; color: white; text-align: left; padding: 10px; font-size: 13px; }}
        td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; vertical-align: top; }}
        code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>APISweeper Security Report</h1>
    <div class="meta">
        Target: <b>{self.target_url}</b><br>
        Generated: {datetime.now(timezone.utc).isoformat()}<br>
        Total findings: <b>{len(findings)}</b>
    </div>
    <div style="margin-bottom: 20px;">{summary_badges}</div>
    <table>
        <tr><th>Severity</th><th>Source Module</th><th>Endpoint</th><th>Description</th></tr>
        {rows}
    </table>
</body>
</html>"""

        with open(output_path, "w") as f:
            f.write(html)
        return output_path


# ---------------------------------------------------------------
# manual test (will be removed later)
# ---------------------------------------------------------------
if __name__ == "__main__":
    sample_findings = [
        {
            "severity": "CRITICAL",
            "endpoint": "/api/orders/1042",
            "description": "User B accessed User A's order via own token.",
            "source": "BOLAChecker",
        },
        {
            "severity": "LOW",
            "endpoint": "/api/status",
            "description": "Strict-Transport-Security header absent.",
            "source": "SecurityHeadersScanner",
        },
    ]

    reporter = ReportGenerator(target_url="http://localhost:5000")
    reporter.to_json(sample_findings, "test_report.json")
    reporter.to_html(sample_findings, "test_report.html")
    print("Test reports generated: test_report.json, test_report.html")