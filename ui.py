import json
import time
from datetime import datetime

import streamlit as st
st.set_option("client.toolbarMode", "minimal")

from scanner import run_scan


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="APISweeper",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 15% 0%, rgba(37, 99, 235, 0.10), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(14, 165, 233, 0.08), transparent 25%),
            #080d18;
        color: #e5e7eb;
    }

    .block-container {
        max-width: 1350px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: #0d1422;
        border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebarContent"] {
        height: 100vh;
        overflow-y: auto;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #0f172a 0%, #111c32 55%, #0c1527 100%);
        border: 1px solid #26364f;
        border-radius: 20px;
        padding: 30px 32px;
        margin-bottom: 24px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        right: -70px;
        top: -100px;
        border-radius: 50%;
        background: rgba(59, 130, 246, 0.10);
        filter: blur(3px);
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 14px;
        position: relative;
        z-index: 1;
    }

    .brand-mark {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        color: white;
        font-size: 23px;
        font-weight: 800;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);
    }

    .hero-title {
        color: #f8fafc;
        font-size: 34px;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin: 0;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 15px;
        margin-top: 5px;
    }

    .hero-description {
        color: #cbd5e1;
        font-size: 14px;
        margin-top: 20px;
        max-width: 720px;
        position: relative;
        z-index: 1;
    }

    .ready-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.09);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: #86efac;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    .ready-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.75);
    }

    .section-heading {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 750;
        letter-spacing: -0.25px;
        margin-top: 25px;
        margin-bottom: 5px;
    }

    .section-caption {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 14px;
    }

    .entry-shell {
        background:
            radial-gradient(circle at 90% 0%, rgba(37, 99, 235, 0.12), transparent 38%),
            linear-gradient(145deg, #0d1728, #0a1220);
        border: 1px solid #23334b;
        border-radius: 20px;
        padding: 24px;
        min-height: 0;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
    }

    .entry-kicker {
        color: #60a5fa;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .entry-title {
        color: #f8fafc;
        font-size: 27px;
        line-height: 1.12;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-bottom: 9px;
    }

    .entry-copy {
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.65;
        max-width: 430px;
    }

    .workflow {
        margin-top: 25px;
        display: grid;
        gap: 11px;
    }

    .workflow-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 11px;
        border: 1px solid #1e2d43;
        background: rgba(9, 17, 31, 0.68);
        border-radius: 11px;
    }

    .workflow-number {
        width: 27px;
        height: 27px;
        min-width: 27px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        background: rgba(37, 99, 235, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.25);
        color: #93c5fd;
        font-size: 10px;
        font-weight: 800;
    }

    .workflow-name {
        color: #e2e8f0;
        font-size: 12px;
        font-weight: 700;
    }

    .workflow-text {
        color: #64748b;
        font-size: 10px;
        margin-top: 2px;
    }

    .entry-trust {
        display: flex;
        align-items: center;
        gap: 7px;
        margin-top: 22px;
        color: #86efac;
        font-size: 10px;
        font-weight: 650;
    }

    .entry-trust-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 9px rgba(34, 197, 94, 0.7);
    }

    /* Pull the Target Configuration panel upward */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.form-heading) {
        transform: translateY(-58px);
    }

    .form-shell {
        background: linear-gradient(180deg, #101827, #0c1524);
        border: 1px solid #23334b;
        border-radius: 20px;
        padding: 22px 24px 14px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
    }

    .form-heading {
        color: #f8fafc;
        font-size: 16px;
        font-weight: 750;
        margin-bottom: 3px;
    }

    .form-caption {
        color: #64748b;
        font-size: 11px;
        margin-bottom: 14px;
    }

    .module-count {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 9px;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.09);
        border: 1px solid rgba(59, 130, 246, 0.20);
        color: #93c5fd;
        font-size: 10px;
        font-weight: 750;
    }

    .scan-panel {
        background: linear-gradient(180deg, #101827, #0d1524);
        border: 1px solid #23334b;
        border-radius: 16px;
        padding: 18px 20px 8px;
        margin-bottom: 10px;
    }

    .mini-card {
        background: #0f1726;
        border: 1px solid #223047;
        border-radius: 14px;
        padding: 15px 17px;
        min-height: 88px;
    }

    .mini-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }

    .mini-value {
        color: #e2e8f0;
        font-size: 16px;
        font-weight: 650;
        margin-top: 7px;
        word-break: break-word;
    }

    .risk-card {
        background: linear-gradient(135deg, #101827, #0c1525);
        border: 1px solid #26364f;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin: 4px 0 18px;
    }

    .risk-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .risk-score {
        color: #f8fafc;
        font-size: 42px;
        font-weight: 800;
        line-height: 1;
        margin: 10px 0 6px;
    }

    .risk-level {
        color: #fbbf24;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.1px;
    }

    .module-card {
        background: #0e1727;
        border: 1px solid #223047;
        border-radius: 13px;
        padding: 14px 16px;
        margin-bottom: 9px;
    }

    .module-name {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 650;
    }

    .module-meta {
        color: #64748b;
        font-size: 11px;
        margin-top: 5px;
    }

    .finding-card {
        background: linear-gradient(180deg, #101827, #0d1523);
        border: 1px solid #25344b;
        border-radius: 16px;
        padding: 18px;
        margin: 10px 0;
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
    }

    .finding-top {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }

    .severity {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 7px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.7px;
    }

    .severity-critical,
    .severity-high {
        background: rgba(239, 68, 68, 0.13);
        border: 1px solid rgba(239, 68, 68, 0.30);
        color: #fca5a5;
    }

    .severity-medium {
        background: rgba(234, 179, 8, 0.12);
        border: 1px solid rgba(234, 179, 8, 0.28);
        color: #fde68a;
    }

    .severity-low {
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: #86efac;
    }

    .severity-info {
        background: rgba(59, 130, 246, 0.10);
        border: 1px solid rgba(59, 130, 246, 0.25);
        color: #93c5fd;
    }

    .finding-title {
        color: #f1f5f9;
        font-size: 16px;
        font-weight: 700;
    }

    .endpoint {
        background: #09111f;
        border: 1px solid #1d2b40;
        border-radius: 8px;
        color: #93c5fd;
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        padding: 9px 11px;
        margin: 10px 0;
        overflow-wrap: anywhere;
    }

    .finding-description {
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.65;
    }




    .category-row {
        display: flex;
        align-items: center;
        gap: 10px;
        min-height: 30px;
    }

    .category-name {
        color: #e2e8f0;
        font-size: 12px;
        font-weight: 650;
    }

    .category-detail-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        min-height: 34px;
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 650;
    }

    .compact-summary {
        margin-top: 12px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 10px;
    }

    .summary-grid div {
        background: #0b1321;
        border: 1px solid #1e293b;
        border-radius: 9px;
        padding: 9px 10px;
    }

    .summary-grid span {
        display: block;
        color: #64748b;
        font-size: 9px;
        margin-bottom: 3px;
    }

    .summary-grid strong {
        color: #f8fafc;
        font-size: 16px;
    }

    .export-label {
        color: #64748b;
        font-size: 9px;
        font-weight: 750;
        letter-spacing: 1.2px;
        padding-top: 10px;
    }

    .target-strip {
        background: #0f1726;
        border: 1px solid #223047;
        border-radius: 14px;
        padding: 11px 14px;
        min-height: 72px;
    }

    .target-strip-label {
        color: #64748b;
        font-size: 9px;
        font-weight: 750;
        letter-spacing: 1.2px;
    }

    .target-strip-value {
        color: #f8fafc;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        margin-top: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .target-strip-meta {
        color: #64748b;
        font-size: 10px;
        margin-top: 4px;
    }

    .compact-finding {
        margin-bottom: 9px !important;
    }

    .visual-panel {
        background: linear-gradient(180deg, #0f1726, #0b1321);
        border: 1px solid #223047;
        border-radius: 16px;
        padding: 18px;
        margin: 10px 0 18px;
    }

    .visual-title {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 750;
        margin-bottom: 3px;
    }

    .visual-caption {
        color: #64748b;
        font-size: 11px;
        margin-bottom: 10px;
    }

    .pictograph-row {
        display: grid;
        grid-template-columns: 105px 1fr 42px;
        gap: 10px;
        align-items: center;
        margin: 11px 0;
    }

    .pictograph-label {
        color: #cbd5e1;
        font-size: 11px;
        font-weight: 650;
    }

    .pictograph-track {
        height: 9px;
        background: #172235;
        border-radius: 999px;
        overflow: hidden;
        border: 1px solid #223047;
    }

    .pictograph-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #2563eb, #0ea5e9);
    }

    .pictograph-value {
        color: #f8fafc;
        font-size: 12px;
        font-weight: 750;
        text-align: right;
    }

    .risk-meter {
        margin-top: 14px;
        height: 12px;
        background: #172235;
        border: 1px solid #26364f;
        border-radius: 999px;
        overflow: hidden;
    }

    .risk-meter-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #22c55e, #eab308, #ef4444);
    }

    .empty-state {
        text-align: center;
        padding: 45px 20px;
        background: #0d1523;
        border: 1px dashed #293951;
        border-radius: 16px;
        margin-top: 10px;
    }

    .empty-title {
        color: #e2e8f0;
        font-size: 19px;
        font-weight: 700;
    }

    .empty-text {
        color: #64748b;
        font-size: 13px;
        margin-top: 7px;
    }

    .sidebar-brand {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin-top : -20px;
    }

    .sidebar-subtitle {
        color: #64748b;
        font-size: 11px;
        margin-top: -8px;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 10px;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: #0f1726;
        border: 1px solid #223047;
        padding: 12px 14px;
        border-radius: 13px;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 9px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
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

    description = str(finding.get("description", ""))
    description_upper = description.upper()

    if "BOLA" in description_upper or "IDOR" in description_upper:
        return "BOLA / IDOR Vulnerability"

    if "RATE LIMIT" in description_upper:
        return "Missing Effective Rate Limiting"

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
    st.markdown(
        '<div class="sidebar-brand">APISweeper</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-subtitle">API SECURITY ASSESSMENT</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Scanner Configuration")

    enable_headers = st.checkbox("Security Headers", value=False)
    enable_verbose_errors = st.checkbox("Verbose Error Detection", value=False)
    enable_jwt = st.checkbox("JWT Token Verification", value=False)
    enable_rate_limit = st.checkbox("Rate Limiting", value=False)
    enable_bola = st.checkbox("BOLA / IDOR", value=False)

    token_b = None
    endpoints_with_ids = None

    if enable_bola:
        st.caption("BOLA / IDOR Configuration")

        token_b = st.text_input(
            "User B Authentication Token",
            type="password",
            placeholder="Token for second user",
        )

        bola_path = st.text_input(
            "ID-Based Endpoint",
            value="/api/v1/users/{id}",
            placeholder="/api/v1/users/{id}",
        )

        bola_known_id = st.text_input(
            "Known Object ID",
            value="1",
            placeholder="1",
        )

        if token_b.strip() and bola_path.strip() and bola_known_id.strip():
            endpoints_with_ids = [
                {
                    "path_template": bola_path.strip(),
                    "known_id_user_a": bola_known_id.strip(),
                }
            ]

    st.divider()
    st.subheader("Active Modules")

    active_modules = []

    if enable_headers:
        active_modules.append("Security Headers")
    if enable_verbose_errors:
        active_modules.append("Verbose Error Detection")
    if enable_jwt:
        active_modules.append("JWT Token Verification")
    if enable_rate_limit:
        active_modules.append("Rate Limiting")
    if enable_bola:
        active_modules.append("BOLA / IDOR")

    st.write(f"**{len(active_modules)}** security modules enabled")

    for module in active_modules:
        st.caption(f"✓  {module}")

    st.divider()
    st.success("Assessment Engine Ready")

    st.caption("Only scan systems and APIs you are authorized to test.")


# ============================================================
# APPLICATION HEADER
# ============================================================

# ============================================================
# APPLICATION HEADER
# ============================================================

if st.session_state.scan_result is None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-row">
                <div class="brand-mark">A</div>
                <div>
                    <div class="hero-title">APISweeper</div>
                    <div class="hero-subtitle">REST API Security Assessment Platform</div>
                </div>
            </div>
            <div style="margin-top:16px;">
                <span class="ready-pill">
                    <span class="ready-dot"></span>
                    Scanner Engine Ready
                </span>
            </div>
            <div class="hero-description">
                Discover API security weaknesses, analyze risk, and inspect responses
                through a unified security assessment dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TARGET SCAN CONSOLE
# ============================================================

start_scan = False

if st.session_state.scan_result is None:
    st.markdown(
        '<div class="section-heading">Start a Security Assessment</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-caption">Enter the target details and launch a focused API security scan.</div>',
        unsafe_allow_html=True,
    )

    intro_col, form_col = st.columns([0.92, 1.45], gap="large")

    # --------------------------------------------------------
    # LEFT: VISUAL INTRO / WORKFLOW
    # --------------------------------------------------------

    with intro_col:
        # Keep the entire left panel inside ONE HTML block.
        # Splitting the opening <div> across st.markdown calls creates the
        # empty rounded box seen above the actual content.
        intro_html = (
            '<div class="entry-shell">'
            '<div class="entry-kicker">APISWEEPER / SCAN CONSOLE</div>'
            '<div class="entry-title">Find weaknesses before attackers do.</div>'
            '<div class="entry-copy">'
            'Configure your authorized API endpoint once. APISweeper will inspect '
            'the target using the security modules selected in the sidebar.'
            '</div>'
            '<div class="workflow">'
            '<div class="workflow-item">'
            '<div class="workflow-number">01</div>'
            '<div><div class="workflow-name">Connect</div>'
            '<div class="workflow-text">Enter the API endpoint</div></div>'
            '</div>'
            '<div class="workflow-item">'
            '<div class="workflow-number">02</div>'
            '<div><div class="workflow-name">Configure</div>'
            '<div class="workflow-text">Add authentication if required</div></div>'
            '</div>'
            '<div class="workflow-item">'
            '<div class="workflow-number">03</div>'
            '<div><div class="workflow-name">Analyze</div>'
            '<div class="workflow-text">Run enabled security checks</div></div>'
            '</div>'
            '</div>'
            '<div class="entry-trust">'
            '<span class="entry-trust-dot"></span>'
            'Authorized testing environment'
            '</div>'
            '</div>'
        )
        st.markdown(intro_html, unsafe_allow_html=True)

    # --------------------------------------------------------
    # RIGHT: INPUT FORM
    # --------------------------------------------------------

    with form_col:
        with st.container(border=True):
            st.markdown(
                '<div class="form-heading">Target Configuration</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="form-caption">Provide the request details for this assessment.</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<span class="module-count">{len(active_modules)} security modules enabled</span>',
                unsafe_allow_html=True,
            )

            with st.form("scan_form"):
                target_url = st.text_input(
                    "Target API URL",
                    placeholder="https://api.example.com",
                )

                col1, col2 = st.columns([1, 1])

                with col1:
                    http_method = st.selectbox(
                        "HTTP Method",
                        ["GET", "POST"],
                    )

                with col2:
                    auth_token = st.text_input(
                        "Authentication Token",
                        type="password",
                        placeholder="Optional Bearer token",
                    )

                request_body = st.text_area(
                    "Request Body (JSON)",
                    placeholder='{"key": "value"}',
                    height=105,
                )

                st.markdown(
                    '<div style="height:4px"></div>',
                    unsafe_allow_html=True,
                )

                start_scan = st.form_submit_button(
                    "START SECURITY SCAN",
                    use_container_width=True,
                    type="primary",
                )

# EXECUTE SCAN
# ============================================================

if start_scan:
    cleaned_url = target_url.strip()

    if not cleaned_url:
        st.error("Please enter a target API URL.")

    elif not (
        cleaned_url.startswith("http://")
        or cleaned_url.startswith("https://")
    ):
        st.error("Target URL must start with http:// or https://")

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
                    st.error(f"Invalid JSON request body: {error}")

        if json_valid:
            token = auth_token.strip() if auth_token.strip() else None

            try:
                with st.spinner("Running security assessment..."):
                    start_time = time.perf_counter()

                    result = run_scan(
                        url=cleaned_url,
                        token=token,
                        method=http_method,
                        data=post_data,
                        enable_headers=enable_headers,
                        enable_verbose_errors=enable_verbose_errors,
                        enable_jwt=enable_jwt,
                        enable_rate_limit=enable_rate_limit,
                        enable_bola=enable_bola,
                        token_b=token_b,
                        endpoints_with_ids=endpoints_with_ids,
                    )

                    elapsed_time = (time.perf_counter() - start_time) * 1000

                if result is None:
                    st.error("Scan failed. Unable to connect to the target.")
                    st.session_state.scan_result = None
                    st.session_state.scan_timestamp = None
                    st.session_state.scan_latency = None

                else:
                    st.session_state.scan_result = result
                    st.session_state.scan_timestamp = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    st.session_state.scan_latency = elapsed_time

                    findings_for_history = result.get("findings", [])
                    history_item = {
                        "timestamp": st.session_state.scan_timestamp,
                        "target": result.get("target", cleaned_url),
                        "findings": len(findings_for_history),
                        "critical": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0,
                        "info": 0,
                    }

                    raw_score = 0
                    for finding in findings_for_history:
                        if isinstance(finding, dict):
                            severity = str(
                                finding.get("severity", "INFO")
                            ).upper()
                            if severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
                                history_item[severity.lower()] += 1
                            raw_score += {
                                "CRITICAL": 15,
                                "HIGH": 10,
                                "MEDIUM": 5,
                                "LOW": 2,
                            }.get(severity, 0)

                    history_item["risk_score"] = raw_score
                    history_item["risk_level"] = calculate_risk_level(raw_score)
                    st.session_state.scan_history.insert(0, history_item)
                    st.session_state.scan_history = st.session_state.scan_history[:5]

                    # Refresh immediately so the input console disappears
                    # and the results dashboard becomes the main view.
                    st.rerun()

            except Exception as error:
                st.error(f"Scanner error: {error}")


# ============================================================
# DISPLAY RESULTS
# ============================================================

scan_data = st.session_state.scan_result

if scan_data:
    status_code = scan_data.get("status_code", "N/A")
    headers = scan_data.get("headers", {})
    response = scan_data.get("response", "")
    findings = scan_data.get("findings", [])

    normalized_findings = []

    for finding in findings:
        if isinstance(finding, dict):
            severity = str(finding.get("severity", "INFO")).upper().strip()
            endpoint = finding.get(
                "endpoint",
                scan_data.get("target", "Unknown"),
            )
            description = finding.get(
                "description",
                "No description available.",
            )
            title = get_finding_title(finding)
        else:
            severity = "INFO"
            endpoint = scan_data.get("target", "Unknown")
            description = str(finding)
            title = "Security Finding"

        if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            severity = "INFO"

        normalized_findings.append(
            {
                "severity": severity,
                "title": title,
                "endpoint": endpoint,
                "description": description,
            }
        )

    critical_count = sum(
        1 for x in normalized_findings if x["severity"] == "CRITICAL"
    )
    high_count = sum(
        1 for x in normalized_findings if x["severity"] == "HIGH"
    )
    medium_count = sum(
        1 for x in normalized_findings if x["severity"] == "MEDIUM"
    )
    low_count = sum(
        1 for x in normalized_findings if x["severity"] == "LOW"
    )
    info_count = sum(
        1 for x in normalized_findings if x["severity"] == "INFO"
    )

    risk_score = (
        critical_count * 15
        + high_count * 10
        + medium_count * 5
        + low_count * 2
    )
    risk_level = calculate_risk_level(risk_score)

    latency = st.session_state.scan_latency
    latency_display = (
        f"{latency:.0f} ms"
        if latency is not None
        else "N/A"
    )

    response_size = len(str(response).encode("utf-8"))
    response_size_display = (
        f"{response_size / 1024:.1f} KB"
        if response_size >= 1024
        else f"{response_size} B"
    )

    # ========================================================
    # RESULT HEADER
    # ========================================================

    result_title_col, result_button_col = st.columns([7, 1])

    with result_title_col:
        st.markdown(
            '<div class="section-heading">Security Assessment</div>',
            unsafe_allow_html=True,
        )

    with result_button_col:
        if st.button(
            "↩ Dashboard",
            key="return_to_dashboard",
            use_container_width=True,
        ):
            st.session_state.scan_result = None
            st.session_state.scan_timestamp = None
            st.session_state.scan_latency = None
            st.session_state.selected_finding_category = None
            st.rerun()

    header_target, header_findings, header_latency, header_risk = st.columns(
        [3.4, 1, 1, 1.15]
    )

    with header_target:
        st.markdown(
            f"""
            <div class="target-strip">
                <div class="target-strip-label">TARGET</div>
                <div class="target-strip-value">
                    {scan_data.get("target", "N/A")}
                </div>
                <div class="target-strip-meta">
                    {scan_data.get("method", "N/A")} &nbsp;•&nbsp;
                    HTTP {status_code} &nbsp;•&nbsp;
                    {get_status_text(status_code)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_findings:
        st.metric("Findings", len(normalized_findings))

    with header_latency:
        st.metric("Latency", latency_display)

    with header_risk:
        st.metric("Risk", risk_score, risk_level)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ========================================================
    # TOP REPORT EXPORT
    # ========================================================

    report = {
        "target": scan_data.get("target"),
        "method": scan_data.get("method"),
        "status_code": scan_data.get("status_code"),
        "headers": headers,
        "response": response,
        "findings": normalized_findings,
        "risk_summary": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "info": info_count,
            "risk_score": risk_score,
            "risk_level": risk_level,
        },
        "scan_timestamp": st.session_state.scan_timestamp,
        "scan_latency_ms": st.session_state.scan_latency,
    }

    filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    export_col, json_col, pdf_col = st.columns([2.2, 1, 1])

    with export_col:
        st.markdown(
            '<div class="export-label">EXPORT ASSESSMENT REPORT</div>',
            unsafe_allow_html=True,
        )

    with json_col:
        st.download_button(
            "Download JSON",
            data=json.dumps(report, indent=4, default=str),
            file_name=f"apisweeper_report_{filename_timestamp}.json",
            mime="application/json",
            use_container_width=True,
        )

    with pdf_col:
        # PDF is generated below using ReportLab when available.
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )
            from reportlab.lib.units import mm
            from io import BytesIO

            pdf_buffer = BytesIO()
            pdf_doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=16 * mm,
                leftMargin=16 * mm,
                topMargin=16 * mm,
                bottomMargin=16 * mm,
            )

            styles = getSampleStyleSheet()
            story = [
                Paragraph("APISweeper Security Assessment", styles["Title"]),
                Spacer(1, 8),
                Paragraph(
                    f"Target: {scan_data.get('target', 'N/A')}",
                    styles["BodyText"],
                ),
                Paragraph(
                    f"Method: {scan_data.get('method', 'N/A')} | "
                    f"HTTP Status: {status_code}",
                    styles["BodyText"],
                ),
                Paragraph(
                    f"Risk Score: {risk_score} | Risk Level: {risk_level}",
                    styles["BodyText"],
                ),
                Spacer(1, 12),
            ]

            summary_table = Table(
                [
                    ["Severity", "Count"],
                    ["Critical", critical_count],
                    ["High", high_count],
                    ["Medium", medium_count],
                    ["Low", low_count],
                    ["Info", info_count],
                ],
                colWidths=[55 * mm, 25 * mm],
            )
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263248")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(summary_table)
            story.append(Spacer(1, 14))

            story.append(
                Paragraph("Findings", styles["Heading2"])
            )
            story.append(Spacer(1, 6))

            for item in normalized_findings:
                story.append(
                    Paragraph(
                        f"<b>[{item['severity']}] {item['title']}</b>",
                        styles["BodyText"],
                    )
                )
                story.append(
                    Paragraph(
                        f"Endpoint: {item['endpoint']}",
                        styles["BodyText"],
                    )
                )
                story.append(
                    Paragraph(
                        str(item["description"]),
                        styles["BodyText"],
                    )
                )
                story.append(Spacer(1, 8))

            pdf_doc.build(story)
            pdf_data = pdf_buffer.getvalue()

            st.download_button(
                "Download PDF",
                data=pdf_data,
                file_name=f"apisweeper_report_{filename_timestamp}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except ImportError:
            st.button(
                "PDF unavailable",
                disabled=True,
                use_container_width=True,
                help="Install reportlab to enable PDF report export.",
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ========================================================
    # MAIN DASHBOARD
    # LEFT  = SECURITY RECORDS
    # RIGHT = VISUAL ANALYTICS
    # ========================================================

    records_col, visuals_col = st.columns(
        [1.55, 1],
        gap="large",
    )

    # --------------------------------------------------------
    # LEFT: SECURITY RECORD CATEGORIES
    # --------------------------------------------------------

    with records_col:
        st.markdown(
            '<div class="section-heading">Security Records</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-caption">Select a category to view its findings.</div>',
            unsafe_allow_html=True,
        )

        category_data = [
            ("CRITICAL", critical_count, "severity-critical"),
            ("HIGH", high_count, "severity-high"),
            ("MEDIUM", medium_count, "severity-medium"),
            ("LOW", low_count, "severity-low"),
            ("INFO", info_count, "severity-info"),
        ]

        selected_category = st.session_state.get(
            "selected_finding_category"
        )

        # Only the category + count is visible until a category is selected.
        if not selected_category:
            for label, count, severity_class in category_data:
                with st.container(border=True):
                    category_left, category_right = st.columns(
                        [3.2, 1]
                    )

                    with category_left:
                        st.markdown(
                            f"""
                            <div class="category-row">
                                <span class="severity {severity_class}">
                                    {label}
                                </span>
                                <span class="category-name">
                                    {label.title()} Findings
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with category_right:
                        if st.button(
                            f"{count}  ›",
                            key=f"category_{label}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            st.session_state.selected_finding_category = label
                            st.rerun()

        else:
            selected_findings = [
                x
                for x in normalized_findings
                if x["severity"] == selected_category
            ]

            selected_count = len(selected_findings)
            selected_class = f"severity-{selected_category.lower()}"

            back_col, title_col = st.columns([1, 3])

            with back_col:
                if st.button(
                    "← Categories",
                    key="back_to_categories",
                    use_container_width=True,
                ):
                    st.session_state.selected_finding_category = None
                    st.rerun()

            with title_col:
                st.markdown(
                    f"""
                    <div class="category-detail-heading">
                        <span class="severity {selected_class}">
                            {selected_category}
                        </span>
                        <span>{selected_count} finding(s)</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if not selected_findings:
                st.success(
                    f"No {selected_category.lower()} findings detected."
                )
            else:
                for finding in selected_findings:
                    severity = finding["severity"]
                    severity_class = f"severity-{severity.lower()}"

                    st.markdown(
                        f"""
                        <div class="finding-card compact-finding">
                            <div class="finding-top">
                                <span class="severity {severity_class}">
                                    {severity}
                                </span>
                                <span class="finding-title">
                                    {finding["title"]}
                                </span>
                            </div>
                            <div class="endpoint">
                                {finding["endpoint"]}
                            </div>
                            <div class="finding-description">
                                {finding["description"]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # --------------------------------------------------------
    # RIGHT: COMPACT VISUAL ANALYTICS
    # --------------------------------------------------------

    with visuals_col:
        st.markdown(
            '<div class="section-heading">Risk Analytics</div>',
            unsafe_allow_html=True,
        )

        # Risk score
        st.markdown(
            f"""
            <div class="risk-card compact-risk">
                <div class="risk-label">Overall Risk</div>
                <div class="risk-score">{risk_score}</div>
                <div class="risk-level">{risk_level}</div>
                <div class="risk-meter">
                    <div class="risk-meter-fill"
                         style="width:{min(risk_score, 100)}%">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Clean, compact severity chart.
        severity_data = [
            {"severity": "Critical", "count": critical_count},
            {"severity": "High", "count": high_count},
            {"severity": "Medium", "count": medium_count},
            {"severity": "Low", "count": low_count},
            {"severity": "Info", "count": info_count},
        ]

        st.markdown(
            '<div class="visual-panel"><div class="visual-title">'
            'Finding Overview</div><div class="visual-caption">'
            'Number of findings by category</div></div>',
            unsafe_allow_html=True,
        )

        st.vega_lite_chart(
            severity_data,
            {
                "mark": {
                    "type": "bar",
                    "cornerRadiusEnd": 5,
                },
                "encoding": {
                    "y": {
                        "field": "severity",
                        "type": "nominal",
                        "sort": [
                            "Critical",
                            "High",
                            "Medium",
                            "Low",
                            "Info",
                        ],
                        "axis": {
                            "title": None,
                            "labelLimit": 75,
                        },
                    },
                    "x": {
                        "field": "count",
                        "type": "quantitative",
                        "axis": {
                            "title": None,
                            "tickMinStep": 1,
                        },
                    },
                    "tooltip": [
                        {
                            "field": "severity",
                            "type": "nominal",
                            "title": "Category",
                        },
                        {
                            "field": "count",
                            "type": "quantitative",
                            "title": "Findings",
                        },
                    ],
                },
                "height": 175,
            },
            use_container_width=True,
        )

        # Small visual summary instead of the large donut.
        total_findings = len(normalized_findings)

        st.markdown(
            f"""
            <div class="visual-panel compact-summary">
                <div class="visual-title">Scan Summary</div>
                <div class="summary-grid">
                    <div>
                        <span>Total</span>
                        <strong>{total_findings}</strong>
                    </div>
                    <div>
                        <span>Critical + High</span>
                        <strong>{critical_count + high_count}</strong>
                    </div>
                    <div>
                        <span>Medium</span>
                        <strong>{medium_count}</strong>
                    </div>
                    <div>
                        <span>Informational</span>
                        <strong>{info_count}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # TECHNICAL DETAILS
    # ========================================================

    with st.expander("Technical details", expanded=False):
        detail_tabs = st.tabs(
            ["Modules", "Response", "Report"]
        )

        module_status = scan_data.get("module_status", [])

        if isinstance(module_status, dict):
            module_status = [
                {"name": name, "status": status}
                for name, status in module_status.items()
            ]

        module_rows = []

        for module in module_status:
            if isinstance(module, dict):
                module_rows.append(
                    {
                        "Module": module.get("name", "Unknown"),
                        "Status": str(
                            module.get("status", "UNKNOWN")
                        ).upper(),
                        "Findings": int(
                            module.get("findings", 0) or 0
                        ),
                        "Time": f'{float(module.get("execution_time_ms", 0) or 0):.0f} ms',
                    }
                )

        with detail_tabs[0]:
            if module_rows:
                st.dataframe(
                    module_rows,
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info(
                    "No module execution information available."
                )

        with detail_tabs[1]:
            response_tabs = st.tabs(["Headers", "Body"])

            with response_tabs[0]:
                if headers:
                    st.json(headers)
                else:
                    st.info("No response headers available.")

            with response_tabs[1]:
                if not response:
                    st.info("No response body received.")
                else:
                    try:
                        st.json(json.loads(response))
                    except (
                        json.JSONDecodeError,
                        TypeError,
                    ):
                        st.code(
                            str(response),
                            language="text",
                        )
        with detail_tabs[2]:
            st.caption(
                "Use the download controls at the top of the assessment "
                "to export the complete scan report."
            )


    if st.session_state.scan_history:
        with st.expander("Recent scans", expanded=False):
            history_rows = [
                {
                    "Time": item.get("timestamp", "Unknown"),
                    "Target": item.get("target", "Unknown"),
                    "Risk": item.get("risk_level", "N/A"),
                    "Score": item.get("risk_score", 0),
                    "Findings": item.get("findings", 0),
                }
                for item in st.session_state.scan_history
            ]

            st.dataframe(
                history_rows,
                hide_index=True,
                use_container_width=True,
            )