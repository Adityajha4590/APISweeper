import argparse
import json
import time
from datetime import datetime

import requests

from modules.passive.security_headers import SecurityHeadersScanner
from modules.passive.verbose_errors import VerboseErrorsScanner
from modules.active.jwt_checks import JWTScanner
from modules.active.rate_limiting import RateLimitScanner
from modules.logic.bola_idor import BOLAChecker
from core.reporting import ReportGenerator


# ============================================================
# SEND REQUEST
# ============================================================

def scan_target(url, token=None, method="GET", data=None):
    """
    Send the main HTTP request to the target API.
    """

    headers = {}

    if token:
        token = token.strip()

        if token.lower().startswith("bearer "):
            headers["Authorization"] = token
        else:
            headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=data if method.upper() in ["POST", "PUT", "PATCH"] else None,
            timeout=10
        )

        return response

    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the target."

    except requests.exceptions.Timeout:
        return None, "Request timed out."

    except requests.exceptions.RequestException as error:
        return None, f"Request failed: {error}"


# ============================================================
# NORMALIZE FINDING
# ============================================================

def normalize_finding(finding, default_endpoint, source):
    """
    Convert findings from different modules into one standard format.
    """

    if isinstance(finding, dict):

        severity = str(
            finding.get("severity", "INFO")
        ).upper()

        if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            severity = "INFO"

        return {
            "severity": severity,
            "endpoint": finding.get(
                "endpoint",
                default_endpoint
            ),
            "description": finding.get(
                "description",
                "No description available."
            ),
            "source": finding.get("source", source),
        }

    return {
        "severity": "INFO",
        "endpoint": default_endpoint,
        "description": str(finding),
        "source": source,
    }


# ============================================================
# GET MODULES
# ============================================================

def get_available_modules(
    url,
    token,
    enable_headers=True,
    enable_verbose_errors=True,
    enable_jwt=True,
    enable_rate_limit=False,
    rate_limit_method="GET",
    rate_limit_data=None,
    enable_bola=False,
    token_b=None,
    endpoints_with_ids=None,
):
    """
    Prepare all enabled scanning modules.

    Future modules can be added here easily.
    """

    modules = []

    if enable_headers:
        modules.append({
            "name": "Security Headers",
            "scanner": SecurityHeadersScanner(url, token)
        })

    if enable_verbose_errors:
        modules.append({
            "name": "Verbose Error Detection",
            "scanner": VerboseErrorsScanner(url, token)
        })

    if enable_jwt:
        modules.append({
            "name": "JWT Security Checks",
            "scanner": JWTScanner(url, token)
        })

    if enable_rate_limit:
        modules.append({
            "name": "Rate Limiting",
            "scanner": RateLimitScanner(
                url,
                token,
                method=rate_limit_method,
                data=rate_limit_data,
            ),
        })

    if enable_bola and token and token_b and endpoints_with_ids:
        modules.append({
        "name": "BOLA / IDOR",
        "scanner": BOLAChecker(
            target_url=url,
            token=token,
            token_b=token_b,
            endpoints_with_ids=endpoints_with_ids,
        )
    })

    return modules


# ============================================================
# RUN SECURITY MODULES
# ============================================================

def run_security_modules(
    url,
    token=None,
    enable_headers=True,
    enable_verbose_errors=True,
    enable_jwt=True,
    enable_rate_limit=False,
    rate_limit_method="GET",
    rate_limit_data=None,
    enable_bola=False,
    token_b=None,
    endpoints_with_ids=None,

):
    """
    Run all selected security modules safely.

    Returns:
        findings
        module_status
    """

    findings = []
    module_status = []

    modules = get_available_modules(
    url=url,
    token=token,
    enable_headers=enable_headers,
    enable_verbose_errors=enable_verbose_errors,
    enable_jwt=enable_jwt,
    enable_rate_limit=enable_rate_limit,
    rate_limit_method=rate_limit_method,
    rate_limit_data=rate_limit_data,
    enable_bola=enable_bola,
    token_b=token_b,
    endpoints_with_ids=endpoints_with_ids,
)

    for module in modules:

        module_name = module["name"]
        scanner = module["scanner"]

        start_time = time.perf_counter()

        try:

            scanner.scan()

            results = scanner.get_results()

            elapsed_time = (
                time.perf_counter() - start_time
            ) * 1000

            normalized_results = []

            if results:

                for finding in results:

                    normalized = normalize_finding(
                        finding,
                        url,
                        module_name,
                    )

                    normalized_results.append(normalized)

                    findings.append(normalized)

            module_status.append({
                "name": module_name,
                "status": "COMPLETED",
                "findings": len(normalized_results),
                "execution_time_ms": round(
                    elapsed_time,
                    2
                ),
                "error": None
            })

        except Exception as error:

            elapsed_time = (
                time.perf_counter() - start_time
            ) * 1000

            module_status.append({
                "name": module_name,
                "status": "FAILED",
                "findings": 0,
                "execution_time_ms": round(
                    elapsed_time,
                    2
                ),
                "error": str(error)
            })

    return findings, module_status


# ============================================================
# RISK SUMMARY
# ============================================================

def calculate_risk_summary(findings):

    summary = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "INFO": 0
    }

    for finding in findings:

        if not isinstance(finding, dict):
            continue

        severity = str(
            finding.get("severity", "INFO")
        ).upper()

        if severity in summary:
            summary[severity] += 1

    return summary


# ============================================================
# CALCULATE RISK SCORE
# ============================================================

def calculate_risk_score(risk_summary):

    critical = risk_summary.get("CRITICAL", 0)
    high = risk_summary.get("HIGH", 0)
    medium = risk_summary.get("MEDIUM", 0)
    low = risk_summary.get("LOW", 0)

    score = (
        critical * 15
        + high * 10
        + medium * 5
        + low * 2
    )

    if score == 0:
        level = "CLEAN"

    elif score <= 10:
        level = "LOW"

    elif score <= 25:
        level = "MEDIUM"

    elif score <= 50:
        level = "HIGH"

    else:
        level = "CRITICAL"

    return score, level


# ============================================================
# CREATE RESULT
# ============================================================

def create_scan_result(
    url,
    response,
    findings,
    module_status,
    scan_duration
):

    risk_summary = calculate_risk_summary(findings)

    risk_score, risk_level = calculate_risk_score(
        risk_summary
    )

    return {
        "scan_id": datetime.now().strftime(
            "SCAN-%Y%m%d-%H%M%S"
        ),

        "scan_timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "target": url,

        "method": response.request.method,

        "status_code": response.status_code,

        "headers": dict(response.headers),

        "response": response.text,

        "findings": findings,

        "module_status": module_status,

        "risk_summary": risk_summary,

        "risk_score": risk_score,

        "risk_level": risk_level,

        "total_findings": len(findings),

        "scan_duration_ms": round(
            scan_duration,
            2
        )
    }


# ============================================================
# MAIN SCAN FUNCTION
# ============================================================

def run_scan(
    url,
    token=None,
    method="GET",
    data=None,
    enable_headers=True,
    enable_verbose_errors=True,
    enable_jwt=True,
    enable_rate_limit=False,
    enable_bola=False,
    token_b=None,
    endpoints_with_ids=None,
):
    """
    Main APISweeper scan function.
    Used by both CLI and Streamlit UI.
    """

    total_start_time = time.perf_counter()

    request_result = scan_target(
        url=url,
        token=token,
        method=method,
        data=data
    )

    if isinstance(request_result, tuple):

        response, error_message = request_result

        if response is None:
            return {
                "success": False,
                "error": error_message
            }

    else:
        response = request_result

    findings, module_status = run_security_modules(
    url=url,
    token=token,
    enable_headers=enable_headers,
    enable_verbose_errors=enable_verbose_errors,
    enable_jwt=enable_jwt,
    enable_rate_limit=enable_rate_limit,
    rate_limit_method=method,
    rate_limit_data=data,
    enable_bola=enable_bola,
    token_b=token_b,
    endpoints_with_ids=endpoints_with_ids,
)

    total_duration = (
        time.perf_counter() - total_start_time
    ) * 1000

    result = create_scan_result(
        url=url,
        response=response,
        findings=findings,
        module_status=module_status,
        scan_duration=total_duration
    )

    result["success"] = True

    return result


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(scan_result, output_file):

    try:

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                scan_result,
                file,
                indent=4,
                default=str
            )

        print(f"Report saved: {output_file}")

    except OSError as error:

        print(f"Could not save report: {error}")


def save_html_report(scan_result, output_file):
    """Render the aggregated findings as a standalone HTML report."""
    try:
        ReportGenerator(scan_result["target"]).to_html(
            scan_result["findings"], output_file
        )
        print(f"HTML report saved: {output_file}")
    except OSError as error:
        print(f"Could not save HTML report: {error}")


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="APISweeper - REST API Security Scanner"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Target API URL"
    )

    parser.add_argument(
        "--token",
        help="Authentication token"
    )

    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST"],
        help="HTTP method"
    )

    parser.add_argument(
        "--data",
        help="JSON request body for POST"
    )

    parser.add_argument(
        "--output",
        help="Save results to JSON file"
    )

    parser.add_argument(
        "--html-output",
        help="Save findings as a standalone HTML report"
    )

    parser.add_argument(
        "--enable-rate-limit",
        action="store_true",
        help="Run the active rate-limiting check"
    )

    parser.add_argument(
        "--enable-bola",
        action="store_true",
        help="Run the BOLA/IDOR check"
    )

    parser.add_argument(
        "--token-b",
        help="Second user's token required for the BOLA/IDOR check"
    )

    parser.add_argument(
        "--bola-path",
        help="ID-based path template, for example /api/v1/orders/{id}"
    )

    parser.add_argument(
        "--bola-known-id",
        help="Object ID known to belong to the first user"
    )

    args = parser.parse_args()

    data = None

    if args.data:

        try:
            data = json.loads(args.data)

        except json.JSONDecodeError:
            print("Invalid JSON data.")
            return

    endpoints_with_ids = None
    if args.enable_bola:
        if not (args.token and args.token_b and args.bola_path and args.bola_known_id):
            parser.error(
                "--enable-bola requires --token, --token-b, --bola-path, and --bola-known-id"
            )
        endpoints_with_ids = [{
            "path_template": args.bola_path,
            "known_id_user_a": args.bola_known_id,
        }]

    result = run_scan(
        url=args.url,
        token=args.token,
        method=args.method,
        data=data,
        enable_rate_limit=args.enable_rate_limit,
        enable_bola=args.enable_bola,
        token_b=args.token_b,
        endpoints_with_ids=endpoints_with_ids,
    )

    if not result.get("success"):

        print("Scan failed.")
        print(result.get("error"))
        return

    print("\n" + "=" * 55)
    print("APISWEEPER SCAN COMPLETE")
    print("=" * 55)

    print(f"Scan ID: {result['scan_id']}")
    print(f"Target: {result['target']}")
    print(f"Method: {result['method']}")
    print(f"Status Code: {result['status_code']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}")

    print("\nModule Status:")

    for module in result["module_status"]:

        print(
            f"{module['name']}: "
            f"{module['status']}"
        )

    print("\nSecurity Findings:")

    if result["findings"]:

        for finding in result["findings"]:

            print(
                f"[{finding['severity']}] "
                f"{finding['description']}"
            )

    else:

        print("No findings detected.")

    if args.output:

        save_report(
            result,
            args.output
        )

    if args.html_output:
        save_html_report(result, args.html_output)


if __name__ == "__main__":
    main()
