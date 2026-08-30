import json
import time
from datetime import datetime

import streamlit as st

from scanner import run_scan


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="APISweeper",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1120;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #263244;
    }

    [data-testid="stSidebarContent"] {
        height: 100vh;
        overflow-y: auto;
    }

    .header-container {
        background: linear-gradient(135deg, #111827, #172033);
        border: 1px solid #2a3850;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .header-title {
        font-size: 34px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 5px;
    }

    .header-subtitle {
        font-size: 16px;
        color: #94a3b8;
    }

    .section-heading {
        font-size: 22px;
        font-weight: 650;
        color: #f8fafc;
        margin-top: 20px;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
    
if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

if "scan_timestamp" not in st.session_state:
    st.session_state.scan_timestamp = None

if "scan_latency" not in st.session_state:
    st.session_state.scan_latency = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_finding_title(finding):

    if not isinstance(finding, dict):
        return "Security Finding"

    description = str(
        finding.get("description", "")
    )

    description_upper = description.upper()

    if "X-FRAME-OPTIONS" in description_upper:
        return "Missing X-Frame-Options Header"

    if "X-CONTENT-TYPE-OPTIONS" in description_upper:
        return "Missing X-Content-Type-Options Header"

    if "CONTENT-SECURITY-POLICY" in description_upper:
        return "Missing Content-Security-Policy Header"

    if "STRICT-TRANSPORT-SECURITY" in description_upper:
        return "Missing Strict-Transport-Security Header"

    if "REFERRER-POLICY" in description_upper:
        return "Missing Referrer-Policy Header"

    if "PERMISSIONS-POLICY" in description_upper:
        return "Missing Permissions-Policy Header"

    if "CROSS-ORIGIN-RESOURCE-POLICY" in description_upper:
        return "Missing Cross-Origin-Resource-Policy Header"

    if "CROSS-ORIGIN-OPENER-POLICY" in description_upper:
        return "Missing Cross-Origin-Opener-Policy Header"

    if "JWT" in description_upper:
        return "JWT Security Check"

    if "SQL" in description_upper:
        return "Potential SQL Error Disclosure"

    if "STACK TRACE" in description_upper:
        return "Stack Trace Disclosure"

    if "JAVA" in description_upper:
        return "Verbose Java Error Disclosure"

    if "ERROR" in description_upper:
        return "Verbose Error Disclosure"

    return "Security Finding"


def get_status_text(status_code):

    if not isinstance(status_code, int):
        return "UNKNOWN"

    if 200 <= status_code < 300:
        return "SUCCESS"

    if 300 <= status_code < 400:
        return "REDIRECT"

    if 400 <= status_code < 500:
        return "CLIENT ERROR"

    if 500 <= status_code < 600:
        return "SERVER ERROR"

    return "UNKNOWN"


def calculate_risk_level(risk_score):

    if risk_score == 0:
        return "CLEAN"

    if risk_score <= 10:
        return "LOW"

    if risk_score <= 25:
        return "MEDIUM"

    if risk_score <= 50:
        return "HIGH"

    return "CRITICAL"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("APISweeper")

    st.caption(
        "REST API Security Assessment Platform"
    )

    st.divider()

    st.subheader("Scanner Configuration")

    enable_headers = st.checkbox(
        "Security Headers",
        value=True
    )

    enable_verbose_errors = st.checkbox(
        "Verbose Error Detection",
        value=True
    )

    enable_jwt = st.checkbox(
        "JWT Token Verification",
        value=True
    )

    st.divider()

    st.subheader("Module Status")

    active_modules = []

    if enable_headers:
        active_modules.append("Security Headers")

    if enable_verbose_errors:
        active_modules.append("Verbose Error Detection")

    if enable_jwt:
        active_modules.append("JWT Token Verification")

    st.write(
        f"Active Modules: {len(active_modules)}"
    )

    for module in active_modules:
        st.caption(module)

    st.divider()

    st.success("Assessment Engine Ready")

    st.caption(
        "Only scan systems and APIs you are authorized to test."
    )

st.divider()

st.subheader("Recent Scans")

history = st.session_state.scan_history

if history:

    for item in history:

        st.caption(
            item.get(
                "timestamp",
                "Unknown Time"
            )
        )

        st.write(
            item.get(
                "target",
                "Unknown Target"
            )
        )

        st.caption(
            f"Risk: "
            f"{item.get('risk_level', 'N/A')} | "
            f"Findings: "
            f"{item.get('findings', 0)}"
        )

        st.divider()

else:

    st.caption(
        "No scans performed yet."
    )

# ============================================================
# APPLICATION HEADER
# ============================================================

st.markdown(
    """
    <div class="header-container">
        <div class="header-title">
            APISweeper
        </div>
        <div class="header-subtitle">
            REST API Security Assessment Platform
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TARGET SCAN CONSOLE
# ============================================================

st.markdown(
    '<div class="section-heading">Target Scan Console</div>',
    unsafe_allow_html=True
)

st.caption(
    "Configure an authorized API endpoint and execute a security assessment."
)


# ============================================================
# SCAN FORM
# ============================================================

with st.form("scan_form"):

    col1, col2 = st.columns([3, 1])

    with col1:

        target_url = st.text_input(
            "Target API URL",
            placeholder="http://localhost:5000/api/status"
        )

    with col2:

        http_method = st.selectbox(
            "HTTP Method",
            ["GET", "POST"]
        )

    col3, col4 = st.columns(2)

    with col3:

        auth_token = st.text_input(
            "Authentication Token",
            type="password",
            placeholder="Optional Bearer token"
        )

    with col4:

        request_body = st.text_area(
            "Request Body (JSON)",
            placeholder='{"key": "value"}',
            height=100
        )

    start_scan = st.form_submit_button(
        "Start Security Scan",
        use_container_width=True,
        type="primary"
    )


# ============================================================
# EXECUTE SCAN
# ============================================================

if start_scan:

    cleaned_url = target_url.strip()

    if not cleaned_url:

        st.error(
            "Please enter a target API URL."
        )

    elif not (
        cleaned_url.startswith("http://")
        or cleaned_url.startswith("https://")
    ):

        st.error(
            "Target URL must start with http:// or https://"
        )

    else:

        post_data = None
        json_valid = True

        if http_method == "POST":

            body = request_body.strip()

            if body:

                try:
                    post_data = json.loads(body)

                except json.JSONDecodeError as error:

                    json_valid = False

                    st.error(
                        f"Invalid JSON request body: {error}"
                    )

        if json_valid:

            token = (
                auth_token.strip()
                if auth_token.strip()
                else None
            )

            try:

                with st.spinner(
                    "Running security assessment..."
                ):

                    start_time = time.perf_counter()

                    result = run_scan(
                        url=cleaned_url,
                        token=token,
                        method=http_method,
                        data=post_data,
                        enable_headers=enable_headers,
                        enable_verbose_errors=enable_verbose_errors,
                        enable_jwt=enable_jwt
                    )

                    elapsed_time = (
                        time.perf_counter()
                        - start_time
                    ) * 1000

                if result is None:

                    st.error(
                        "Scan failed. Unable to connect to the target."
                    )

                    st.session_state.scan_result = None
                    st.session_state.scan_timestamp = None
                    st.session_state.scan_latency = None

                else:

                    st.session_state.scan_result = result

                    st.session_state.scan_timestamp = (
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )

                    st.session_state.scan_latency = elapsed_time

                    st.success(
                        "Security assessment completed successfully."
                    )

            except Exception as error:

                st.error(
                    f"Scanner error: {error}"
                )


# ============================================================
# DISPLAY RESULTS
# ============================================================

scan_data = st.session_state.scan_result


if scan_data:

    st.divider()


    # ========================================================
    # TARGET INFORMATION
    # ========================================================

    st.markdown(
        '<div class="section-heading">Target Information</div>',
        unsafe_allow_html=True
    )

    target_col1, target_col2, target_col3 = st.columns(
        [4, 1, 2]
    )

    with target_col1:

        st.metric(
            "Target URL",
            scan_data.get("target", "N/A")
        )

    with target_col2:

        st.metric(
            "Method",
            scan_data.get("method", "N/A")
        )

    with target_col3:

        st.metric(
            "Scan Time",
            st.session_state.scan_timestamp or "N/A"
        )


    # ========================================================
    # GET DATA
    # ========================================================

    status_code = scan_data.get(
        "status_code",
        "N/A"
    )

    headers = scan_data.get(
        "headers",
        {}
    )

    response = scan_data.get(
        "response",
        ""
    )

    findings = scan_data.get(
        "findings",
        []
    )


    # ========================================================
    # RESPONSE SIZE
    # ========================================================

    response_size = len(
        str(response).encode("utf-8")
    )

    if response_size >= 1024:

        response_size_display = (
            f"{response_size / 1024:.2f} KB"
        )

    else:

        response_size_display = (
            f"{response_size} B"
        )


    # ========================================================
    # SCAN SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-heading">Scan Summary</div>',
        unsafe_allow_html=True
    )

    summary_col1, summary_col2, summary_col3, summary_col4 = (
        st.columns(4)
    )

    latency = st.session_state.scan_latency

    latency_display = (
        f"{latency:.2f} ms"
        if latency is not None
        else "N/A"
    )

    with summary_col1:

        st.metric(
            "HTTP Status",
            status_code,
            get_status_text(status_code)
        )

    with summary_col2:

        st.metric(
            "Response Latency",
            latency_display
        )

    with summary_col3:

        st.metric(
            "Response Size",
            response_size_display
        )

    with summary_col4:

        st.metric(
            "Security Findings",
            len(findings)
        )


    # ========================================================
    # NORMALIZE FINDINGS
    # ========================================================

    normalized_findings = []

    for finding in findings:

        if isinstance(finding, dict):

            severity = str(
                finding.get(
                    "severity",
                    "INFO"
                )
            ).upper().strip()

            endpoint = finding.get(
                "endpoint",
                scan_data.get(
                    "target",
                    "Unknown"
                )
            )

            description = finding.get(
                "description",
                "No description available."
            )

            title = get_finding_title(finding)

        else:

            severity = "INFO"

            endpoint = scan_data.get(
                "target",
                "Unknown"
            )

            description = str(finding)

            title = "Security Finding"

        if severity not in [
            "HIGH",
            "MEDIUM",
            "LOW",
            "INFO"
        ]:

            severity = "INFO"

        normalized_findings.append(
            {
                "severity": severity,
                "title": title,
                "endpoint": endpoint,
                "description": description
            }
        )


    # ========================================================
    # RISK SUMMARY
    # ========================================================

    high_count = sum(
        1
        for item in normalized_findings
        if item["severity"] == "HIGH"
    )

    medium_count = sum(
        1
        for item in normalized_findings
        if item["severity"] == "MEDIUM"
    )

    low_count = sum(
        1
        for item in normalized_findings
        if item["severity"] == "LOW"
    )

    info_count = sum(
        1
        for item in normalized_findings
        if item["severity"] == "INFO"
    )

    risk_score = (
        high_count * 10
        + medium_count * 5
        + low_count * 2
    )

    risk_level = calculate_risk_level(
        risk_score
    )

    # ========================================================
    # MODULE EXECUTION STATUS
    # ========================================================

    st.markdown(
        '<div class="section-heading">Module Execution Status</div>',
        unsafe_allow_html=True
    )

    module_status = scan_data.get(
        "module_status",
        []
    )

    if module_status:

        if isinstance(module_status, dict):
            module_status = [
                {
                    "name": name,
                    "status": status
                }
                for name, status in module_status.items()
            ]

        for module in module_status:

            if not isinstance(module, dict):
                st.info(str(module))
                continue

            name = module.get(
                "name",
                "Unknown Module"
            )

            status = str(
                module.get(
                    "status",
                    "UNKNOWN"
                )
            ).upper()

            findings_count = module.get(
                "findings",
                0
            )

            execution_time = module.get(
                "execution_time_ms",
                0
            )

            error = module.get("error")

            if status == "COMPLETED":

                st.success(
                    f"{name} — Completed | "
                    f"Findings: {findings_count} | "
                    f"Time: {execution_time} ms"
                )

            elif status == "FAILED":

                st.error(
                    f"{name} — Failed | "
                    f"Error: {error or 'Unknown error'}"
                )

            else:

                st.info(
                    f"{name} — {status}"
                )

    else:

        st.info(
            "No module execution information available."
        )



    # ========================================================
    # SECURITY FINDINGS
    # ========================================================

    st.markdown(
        '<div class="section-heading">Security Findings</div>',
        unsafe_allow_html=True
    )

    risk_col1, risk_col2, risk_col3, risk_col4, risk_col5 = (
        st.columns(5)
    )

    with risk_col1:
        st.metric("High", high_count)

    with risk_col2:
        st.metric("Medium", medium_count)

    with risk_col3:
        st.metric("Low", low_count)

    with risk_col4:
        st.metric("Informational", info_count)

    with risk_col5:
        st.metric("Risk Score", risk_score)

    st.caption(
        f"Overall Risk Assessment: {risk_level}"
    )



    # ========================================================
    # SEVERITY FILTER
    # ========================================================

    severity_filter = st.selectbox(
        "Filter Findings",
        [
            "All",
            "HIGH",
            "MEDIUM",
            "LOW",
            "INFO"
        ]
    )

    if severity_filter == "All":

        filtered_findings = (
            normalized_findings.copy()
        )

    else:

        filtered_findings = [
            finding
            for finding in normalized_findings
            if finding["severity"] == severity_filter
        ]



    # ========================================================
    # SORT FINDINGS
    # ========================================================

    severity_order = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
        "INFO": 4
    }

    filtered_findings.sort(
        key=lambda item: severity_order.get(
            item["severity"],
            5
        )
    )



    # ========================================================
    # DISPLAY FINDINGS
    # ========================================================

    if not filtered_findings:

        st.info(
            "No security findings match the selected filter."
        )

    else:

        for index, finding in enumerate(
            filtered_findings,
            start=1
        ):

            severity = finding["severity"]
            title = finding["title"]
            endpoint = finding["endpoint"]
            description = finding["description"]

            with st.container(border=True):

                col_badge, col_title = st.columns(
                    [1, 6]
                )

                with col_badge:

                    if severity == "HIGH":

                        st.error("HIGH")

                    elif severity == "MEDIUM":

                        st.warning("MEDIUM")

                    elif severity == "LOW":

                        st.success("LOW")

                    else:

                        st.info("INFO")

                with col_title:

                    st.subheader(title)

                st.caption(
                    f"Endpoint: {endpoint}"
                )

                st.write(description)
                
    # ========================================================
    # HTTP RESPONSE INSPECTOR
    # ========================================================

    st.markdown(
        '<div class="section-heading">HTTP Response Inspector</div>',
        unsafe_allow_html=True
    )

    headers_tab, body_tab = st.tabs(
        [
            "Response Headers",
            "Response Body"
        ]
    )

    with headers_tab:

        if headers:

            st.json(headers)

        else:

            st.info(
                "No response headers available."
            )

    with body_tab:

        if not response:

            st.info(
                "No response body received."
            )

        else:

            try:

                parsed_response = json.loads(
                    response
                )

                st.json(
                    parsed_response
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):

                st.text_area(
                    "Response Content",
                    value=str(response),
                    height=300,
                    disabled=True
                )


    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.markdown(
        '<div class="section-heading">Assessment Report</div>',
        unsafe_allow_html=True
    )

    report = {
        "target": scan_data.get("target"),
        "method": scan_data.get("method"),
        "status_code": scan_data.get("status_code"),
        "headers": headers,
        "response": response,
        "findings": normalized_findings,
        "risk_summary": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "info": info_count,
            "risk_score": risk_score,
            "risk_level": risk_level
        },
        "scan_timestamp": (
            st.session_state.scan_timestamp
        ),
        "scan_latency_ms": (
            st.session_state.scan_latency
        )
    }

    report_json = json.dumps(
        report,
        indent=4,
        default=str
    )

    filename_timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    st.download_button(
        label="Download Assessment Report",
        data=report_json,
        file_name=(
            f"apisweeper_report_"
            f"{filename_timestamp}.json"
        ),
        mime="application/json",
        use_container_width=True
    )