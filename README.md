# 🛡️ APISweeper: Lightweight Vulnerable API Scanner

**APISweeper** is a lightweight, Python-based Dynamic Application Security Testing (DAST) tool purpose-built for REST APIs. It automatically scans target endpoints for critical security misconfigurations and vulnerabilities mapped to the **OWASP API Security Top 10**.

Unlike heavy, enterprise-grade scanners (like Burp Suite or OWASP ZAP), APISweeper is designed to be fast, modular, and easy to run from the command line, generating severity-scored vulnerability reports.

---

## 👥 Meet the Team & Work Distribution

This project was developed over a 20-day sprint by a 5-person security engineering team:

*   **Aditya Kumar Jha** (Supervisor / Lead Architect)
    *   Core Integration (`core/base.py`)
    *   Target Dummy API (`dummy_api/app.py`)
    *   Project Management
*   **Jatin** - Core Scanner CLI Engine & HTTP handling (`scanner.py`), and Premium Web UI Dashboard (`ui.py` using Streamlit).
*   **Keshav** - Passive Scanning (`modules/passive/security_headers.py`, `modules/passive/verbose_errors.py`).
*   **Rishab** - Active Scanning (`modules/active/rate_limiting.py`, `modules/active/jwt_checks.py`).
*   **Pranav** - Logic Scanning (`modules/logic/bola_idor.py`) & Reporting Engine (`core/reporting.py`).

---

## 🚀 Project Roadmap & Phases

This project was strictly managed and developed across 4 agile phases:

### Phase 1: Foundation & Setup (Days 1 - 4)
*   **Repository Initialization:** Set up Git flow, branch protections, and contribution guidelines.
*   **Dummy Target API:** Developed a deliberately vulnerable local API (using Flask) to safely test our scanner payloads.
*   **Architecture Design:** Defined the base Python classes (`core/base.py`) so all vulnerability modules plug into the main engine uniformly.
*   **Web UI Scaffold:** Designed a premium, dark-mode cybersecurity dashboard (`ui.py`) using **Streamlit** (100% Python frontend).

### Phase 2: Core Framework & Basic Modules (Days 5 - 10)
*   **CLI Engine & UI Backend:** Implemented `argparse` for robust command-line target ingestion (`scanner.py`) and integrated it into the Streamlit dashboard (`ui.py`).
*   **Missing Security Headers Module:** Automatically flags missing standard defenses (e.g., `Strict-Transport-Security`, `X-Content-Type-Options`).
*   **Verbose Error Leaks Module:** Uses pattern matching to detect stack traces (Python, Java, SQL syntax) improperly returned in HTTP 500 responses.

### Phase 3: Complex Vulnerability Modules (Days 11 - 16)
*   **Rate Limiting Check:** Blasts a target endpoint with high-frequency rapid requests to verify the presence of `429 Too Many Requests` controls.
*   **BOLA / IDOR Check:** Tests Broken Object Level Authorization by attempting cross-user data access via ID manipulation (e.g., swapping `?user_id=1` to `?user_id=2`).
*   **JWT Security Check:** Inspects Authorization tokens for missing signatures or acceptance of the `alg: none` vulnerability.
*   **Reporting Engine:** Aggregates findings and assigns CVSS-based severity scores (Low, Medium, High, Critical).

### Phase 4: Testing, Refinement & Documentation (Days 17 - 20)
*   **Integration Testing:** Running the full APISweeper suite against the Dummy Target API to eliminate false positives and negatives.
*   **Code Review:** Final pull request merges and code quality standardization.
*   **Documentation:** Finalizing this README and usage instructions.

---

## 📁 Project Structure
The repository is structured as follows:

```text
APISweeper/
├── core/                  # Architecture & Reporting
│   ├── __init__.py
│   ├── base.py
│   └── reporting.py       
├── dummy_api/             # Vulnerable Targets (Flask)
│   ├── __init__.py
│   └── app.py
├── modules/               # The Scanning Engine
│   ├── __init__.py
│   ├── passive/           
│   │   ├── __init__.py
│   │   ├── security_headers.py
│   │   └── verbose_errors.py
│   ├── active/            
│   │   ├── __init__.py
│   │   ├── rate_limiting.py
│   │   └── jwt_checks.py
│   └── logic/             
│       ├── __init__.py
│       └── bola_idor.py
├── ui.py                  # Streamlit Web UI Dashboard
├── scanner.py             # CLI Entry Point
├── requirements.txt
└── README.md              
```

### What Each Folder is For:
*   **`core/`**: The most critical folder. Contains `base.py`, which is the abstract contract (blueprint) that every other scanner module must follow. Without this integration layer, the engine wouldn't know how to run the different team members' code together.
*   **`dummy_api/`**: A deliberately vulnerable local web server. We build and run this so our scanner has a safe, legal target to attack during development without scanning live public servers.
*   **`modules/`**: Where the actual scanning logic lives. Split into `passive` (checking headers without sending many requests), `active` (sending many requests like rate limiting), and `logic` (complex tests like BOLA/IDOR).
*   **`ui.py`**: Contains the Streamlit Python code for the premium visual dashboard. This is the "frontend" that users will interact with.
*   **`scanner.py`**: The fallback CLI (Command Line Interface) engine for running scans directly from the terminal without the UI.

---

## ⚙️ Installation & Setup

### Prerequisites
*   Python 3.8+
*   `pip` package manager

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/APISweeper.git
   cd APISweeper
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Start the dummy vulnerable API to test locally:
   ```bash
   python dummy_api/app.py
   ```

---

## 💻 Usage

Run the scanner via the command line by passing the target URL:

```bash
# Basic scan against a target API
python scanner.py --url http://localhost:5000/api/v1

# Run with authentication token for BOLA/IDOR checks
python scanner.py --url http://localhost:5000/api/v1 --token "eyJhbGciOiJIUzI1Ni..."

# Output results to a JSON report
python scanner.py --url http://localhost:5000/api/v1 --output report.json
```

---

## 📈 Example Output Report

When the scan finishes, APISweeper generates a concise, actionable report:

```text
==================================================
           APISWEEPER SECURITY REPORT             
==================================================
Target: http://localhost:5000/api/v1
Time: 2023-10-25 14:00:00

[HIGH] Broken Object Level Authorization (IDOR)
- Endpoint: /api/v1/users/2
- Description: Successfully accessed another user's data using User 1's token.

[MEDIUM] Missing Rate Limiting
- Endpoint: /api/v1/login
- Description: Sent 50 requests in 2 seconds; no 429 response received. Brute-force possible.

[LOW] Missing Security Headers
- Endpoint: Global
- Description: Missing 'Strict-Transport-Security' and 'X-Frame-Options'.

Total Vulnerabilities Found: 3
==================================================
```

---

## 🤝 Contribution Guidelines (Internal Team)
1. **Branch Naming:** Format your branches as `feature/module-name` (e.g., `feature/rate-limiting`).
2. **Pull Requests:** Do not merge your own PRs. Assign the Supervisor for review.
3. **Module Structure:** Ensure all new checks inherit from the `BaseScanner` class found in `core/base.py`.

---

## 🏆 Supervisor Resume Highlights (Aditya Kumar Jha)..
If you are adding this project to your resume, consider using these bullet points:
*   **Technical Leadership:** Supervised and architected a 5-person engineering team to build **APISweeper**, a modular Dynamic Application Security Testing (DAST) tool over a 20-day agile sprint.
*   **System Architecture:** Designed the extensible core engine in Python, establishing standard inheritance patterns (`BaseScanner`) enabling concurrent development of passive, active, and logic-based vulnerability modules.
*   **Full-Stack Development:** Engineered both a vulnerable Flask-based dummy target API for zero-risk local testing, and supervised the integration of a premium Streamlit Web UI dashboard to visualize scanner findings in real-time.
*   **Project Management:** Enforced strict Git Flow (feature branching, PR reviews) and defined the project roadmap, ensuring seamless integration of complex modules (BOLA checks, Rate Limiting, JWT validation).
