import json
import time
import textwrap
from datetime import datetime

import streamlit as st

from scanner import run_scan


st.set_page_config(
    page_title="APISweeper | Security Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_html(content):
    clean_html = "\n".join(
        line.strip()
        for line in content.splitlines()
        if line.strip()
    )

    st.markdown(
        clean_html,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        font-family: "Inter", -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebar"] h3 {
        color: #f8fafc;
    }

    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.95),
            rgba(17, 24, 39, 0.95)
        );
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }

    .app-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .app-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    .status-ready {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #059669;
        color: #34d399;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.7);
    }

    .section-heading {
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.9rem;
    }

    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        min-height: 105px;
    }

    .metric-title {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 7px;
    }

    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .metric-subtitle {
        color: #64748b;
        font-size: 0.72rem;
        margin-top: 4px;
    }

    .status-2xx {
        color: #34d399;
    }

    .status-3xx {
        color: #38bdf8;
    }

    .status-4xx {
        color: #fbbf24;
    }

    .status-5xx {
        color: #f87171;
    }

    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-left: 5px;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid #059669;
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid #d97706;
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.12);
        color: #f87171;
        border: 1px solid #dc2626;
    }

    .badge-info {
        background: rgba(14, 165, 233, 0.12);
        color: #38bdf8;
        border: 1px solid #0284c7;
    }

    .target-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px 16px;
    }

    .target-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }

    .target-value {
        color: #e2e8f0;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.85rem;
        word-break: break-all;
    }

    .finding-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .finding-title {
        color: #f8fafc;
        font-size: 0.92rem;
        font-weight: 650;
    }

    .finding-details {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 7px;
        line-height: 1.5;
    }

    .severity {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 7px;
    }

    .severity-high {
        background: rgba(239, 68, 68, 0.12);
        color: #f87171;
        border: 1px solid #dc2626;
    }

    .severity-medium {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid #d97706;
    }

    .severity-low {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid #059669;
    }

    .severity-info {
        background: rgba(14, 165, 233, 0.12);
        color: #38bdf8;
        border: 1px solid #0284c7;
    }

    [data-testid="stForm"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
    }

    button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #0ea5e9,
            #2563eb
        ) !important;
        border: none !important;
        color: white !important;
        font-weight: 650 !important;
        border-radius: 8px !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(
            135deg,
            #38bdf8,
            #1d4ed8
        ) !important;
    }

    .empty-state {
        background: #111827;
        border: 1px dashed #334155;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
    }

    .empty-title {
        color: #e2e8f0;
        font-weight: 650;
    }

    .empty-text {
        color: #64748b;
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


if "scan_result" not in st.session_state:
    st.session_state["scan_result"] = None

if "scan_timestamp" not in st.session_state:
    st.session_state["scan_timestamp"] = None

if "scan_latency" not in st.session_state:
    st.session_state["scan_latency"] = None


with st.sidebar:
    st.markdown("### APISweeper")
    st.caption("REST API Security Assessment Platform")

    st.divider()

    st.markdown("**Scanner Configuration**")

    st.checkbox(
        "Passive Security Headers",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Verbose Error Detection",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Active Rate Limiting",
        value=False,
        disabled=True
    )

    st.checkbox(
        "JWT Token Verification",
        value=False,
        disabled=True
    )

    st.checkbox(
        "BOLA / IDOR Logic Engine",
        value=False,
        disabled=True
    )

    st.divider()

    render_html(
        """
        <div style="
            background:#1e293b;
            padding:12px;
            border-radius:8px;
            border-left:4px solid #10b981;
        ">
            <span style="
                font-size:0.72rem;
                color:#94a3b8;
            ">
                ENGINE STATUS
            </span>
            <br>
            <strong style="color:#34d399;">
                Ready
            </strong>
        </div>
        """
    )


render_html(
    """
    <div class="app-header">
        <div>
            <div class="app-title">
                APISweeper
            </div>

            <div class="app-subtitle">
                REST API Security Assessment Platform
            </div>
        </div>

        <div class="status-ready">
            <span class="status-dot"></span>
            Scanner Ready
        </div>
    </div>
    """
)


render_html(
    """
    <div class="section-heading">
        Target Scan Console
    </div>
    """
)

st.caption(
    "Configure the endpoint and execute an authorized security assessment."
)


with st.form("scan_form"):
    col_url, col_method = st.columns([3, 1])

    with col_url:
        target_url = st.text_input(
            "Target API URL",
            placeholder="http://localhost:5001/api/v1/status",
            help="Enter the HTTP/HTTPS endpoint you are authorized to assess."
        )

    with col_method:
        http_method = st.selectbox(
            "HTTP Method",
            ["GET", "POST"],
            index=0
        )

    col_token, col_body = st.columns([1, 1])

    with col_token:
        auth_token = st.text_input(
            "Authentication Token (Optional)",
            type="password",
            placeholder="Bearer token or API key"
        )

    with col_body:
        request_body = st.text_area(
            "Request Body (JSON)",
            value="" if http_method == "GET" else "{\n  \n}",
            height=100,
            placeholder='{"key": "value"}'
        )

    st.write("")

    execute_btn = st.form_submit_button(
        "Start Security Scan",
        type="primary",
        use_container_width=True
    )


if execute_btn:
    url_cleaned = target_url.strip() if target_url else ""

    token_cleaned = (
        auth_token.strip()
        if auth_token and auth_token.strip()
        else None
    )

    if not url_cleaned:
        st.error(
            "Please enter a Target API URL before starting the scan."
        )

    elif not (
        url_cleaned.startswith("http://")
        or url_cleaned.startswith("https://")
    ):
        st.error(
            "Invalid URL: Target URL must begin with "
            "'http://' or 'https://'."
        )

    else:
        post_data = None
        json_valid = True

        if http_method == "POST":
            body_trimmed = request_body.strip()

            if body_trimmed:
                try:
                    post_data = json.loads(body_trimmed)

                except json.JSONDecodeError as json_err:
                    json_valid = False

                    st.error(
                        f"Invalid JSON in Request Body: "
                        f"{json_err.msg} "
                        f"(line {json_err.lineno}, "
                        f"column {json_err.colno})."
                    )

        if json_valid:
            with st.spinner(
                "Connecting to target and executing security scan..."
            ):
                try:
                    start_time = time.perf_counter()

                    result = run_scan(
                        url=url_cleaned,
                        token=token_cleaned,
                        method=http_method,
                        data=post_data
                    )

                    elapsed_time = (
                        time.perf_counter() - start_time
                    ) * 1000

                except Exception as ex:
                    result = None
                    elapsed_time = None

                    st.error(
                        f"An unexpected error occurred "
                        f"during scan execution: {ex}"
                    )

            if result is None:
                st.error(
                    "Scan Failed: Unable to establish connection "
                    "to the target URL. Please verify that the server "
                    "is running, the URL is correct, and network access "
                    "is permitted."
                )

                st.session_state["scan_result"] = None
                st.session_state["scan_timestamp"] = None
                st.session_state["scan_latency"] = None

            else:
                st.session_state["scan_result"] = result

                st.session_state["scan_timestamp"] = (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                st.session_state["scan_latency"] = elapsed_time

                st.success(
                    "Security scan completed successfully."
                )


scan_data = st.session_state.get("scan_result")


if scan_data:
    st.write("")
    st.divider()

    render_html(
        """
        <div class="section-heading">
            Target Information
        </div>
        """
    )

    target_col1, target_col2, target_col3 = st.columns([4, 1, 2])

    with target_col1:
        render_html(
            f"""
            <div class="target-card">
                <div class="target-label">
                    Target URL
                </div>

                <div class="target-value">
                    {scan_data.get("target", "N/A")}
                </div>
            </div>
            """
        )

    with target_col2:
        render_html(
            f"""
            <div class="target-card">
                <div class="target-label">
                    Method
                </div>

                <div class="target-value">
                    {scan_data.get("method", "GET")}
                </div>
            </div>
            """
        )

    with target_col3:
        render_html(
            f"""
            <div class="target-card">
                <div class="target-label">
                    Scan Time
                </div>

                <div class="target-value">
                    {st.session_state.get(
                        "scan_timestamp",
                        "N/A"
                    )}
                </div>
            </div>
            """
        )

    st.write("")

    render_html(
        """
        <div class="section-heading">
            Scan Summary
        </div>
        """
    )

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

    if isinstance(response, str):
        response_size = len(
            response.encode("utf-8")
        )

    elif isinstance(response, (dict, list)):
        response_size = len(
            json.dumps(response).encode("utf-8")
        )

    elif response is not None:
        response_size = len(
            str(response).encode("utf-8")
        )

    else:
        response_size = 0

    if response_size >= 1024:
        response_size_display = (
            f"{response_size / 1024:.2f} KB"
        )
    else:
        response_size_display = (
            f"{response_size} B"
        )

    status_class = "status-2xx"
    status_badge = "badge-success"
    status_text = "SUCCESS"

    if isinstance(status_code, int):

        if 200 <= status_code < 300:
            status_class = "status-2xx"
            status_badge = "badge-success"
            status_text = "SUCCESS"

        elif 300 <= status_code < 400:
            status_class = "status-3xx"
            status_badge = "badge-info"
            status_text = "REDIRECT"

        elif 400 <= status_code < 500:
            status_class = "status-4xx"
            status_badge = "badge-warning"
            status_text = "CLIENT ERROR"

        elif 500 <= status_code < 600:
            status_class = "status-5xx"
            status_badge = "badge-danger"
            status_text = "SERVER ERROR"

        else:
            status_text = "HTTP"

    latency = st.session_state.get(
        "scan_latency"
    )

    latency_display = (
        f"{latency:.2f} ms"
        if latency is not None
        else "N/A"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_html(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    HTTP Status
                </div>

                <div class="metric-value {status_class}">
                    {status_code}

                    <span class="badge {status_badge}">
                        {status_text}
                    </span>
                </div>

                <div class="metric-subtitle">
                    HTTP response code
                </div>
            </div>
            """
        )

    with col2:
        render_html(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    Response Latency
                </div>

                <div class="metric-value">
                    {latency_display}
                </div>

                <div class="metric-subtitle">
                    Scanner execution time
                </div>
            </div>
            """
        )

    with col3:
        render_html(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    Response Size
                </div>

                <div class="metric-value">
                    {response_size_display}
                </div>

                <div class="metric-subtitle">
                    {response_size:,} bytes
                </div>
            </div>
            """
        )

    with col4:
        finding_count = len(findings)

        if finding_count > 0:
            finding_color = "#f87171"
            finding_status = "FINDINGS"
        else:
            finding_color = "#34d399"
            finding_status = "CLEAN"

        render_html(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    Security Findings
                </div>

                <div class="metric-value"
                     style="color:{finding_color};">

                    {finding_count}

                    <span class="badge badge-info">
                        {finding_status}
                    </span>
                </div>

                <div class="metric-subtitle">
                    Scanner findings
                </div>
            </div>
            """
        )

    st.write("")

    render_html(
        """
        <div class="section-heading">
            Security Findings
        </div>
        """
    )

    if not findings:
        render_html(
            """
            <div class="empty-state">
                <div class="empty-title">
                    No security findings available
                </div>

                <div class="empty-text">
                    Findings will appear here when the
                    scanning modules provide results.
                </div>
            </div>
            """
        )

    else:
        severity_map = {
            "high": "severity-high",
            "medium": "severity-medium",
            "low": "severity-low",
            "info": "severity-info"
        }

        for finding in findings:

            finding_name = finding.get(
                "name",
                "Security Finding"
            )

            severity = str(
                finding.get(
                    "severity",
                    "Info"
                )
            ).strip()

            severity_class = severity_map.get(
                severity.lower(),
                "severity-info"
            )

            details = finding.get(
                "details",
                "No additional details available."
            )

            render_html(
                f"""
                <div class="finding-card">
                    <div>
                        <span class="severity {severity_class}">
                            {severity}
                        </span>

                        <span class="finding-title">
                            {finding_name}
                        </span>
                    </div>

                    <div class="finding-details">
                        {details}
                    </div>
                </div>
                """
            )

    render_html(
        """
        <div class="section-heading">
            HTTP Response Inspector
        </div>
        """
    )

    tab_headers, tab_body = st.tabs(
        [
            "Headers",
            "Response Body"
        ]
    )

    with tab_headers:

        if headers and isinstance(headers, dict):
            st.json(headers)

        elif headers:
            st.code(
                str(headers),
                language="text"
            )

        else:
            st.info(
                "No response headers were returned."
            )

    with tab_body:

        if isinstance(response, dict):
            st.json(response)

        elif isinstance(response, list):
            st.json(response)

        elif isinstance(response, str):

            try:
                parsed_response = json.loads(response)

                st.json(parsed_response)

            except (
                json.JSONDecodeError,
                TypeError
            ):
                st.code(
                    response
                    if response
                    else "(Empty Response Body)",
                    language="text"
                )

        elif response is not None:
            st.code(
                str(response),
                language="text"
            )

        else:
            st.info(
                "No response body received."
            )

    render_html(
        """
        <div class="section-heading">
            Assessment Report
        </div>
        """
    )

    report = {
        "target": scan_data.get("target"),
        "method": scan_data.get("method"),
        "status_code": scan_data.get("status_code"),
        "headers": scan_data.get("headers"),
        "response": scan_data.get("response"),
        "findings": scan_data.get("findings", []),
        "scan_timestamp": st.session_state.get(
            "scan_timestamp"
        ),
        "scan_latency_ms": st.session_state.get(
            "scan_latency"
        )
    }

    report_json = json.dumps(
        report,
        indent=2,
        default=str
    )

    filename_timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    st.download_button(
        label="Download JSON Report",
        data=report_json,
        file_name=(
            f"apisweeper_scan_report_"
            f"{filename_timestamp}.json"
        ),
        mime="application/json",
        use_container_width=True
    )