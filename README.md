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

## 🚀 Future Scope

Potential improvements for future versions of APISweeper include:

-Expanded OWASP API Coverage: Add more checks for broken authentication, object property authorization, resource consumption, SSRF, and other API security risks.
-OpenAPI/Swagger Integration: Import API specifications to discover endpoints, methods, parameters, and authentication requirements.
-Improved BOLA Detection: Automate more authorization comparisons across users and object identifiers.
-Advanced Authentication Testing: Expand checks for token validation, authentication bypass, and session-management weaknesses.
-Improved Reporting: Provide richer evidence, remediation guidance, and additional report formats.
-CI/CD Integration: Run authorized security checks during automated build and deployment workflows.
-Testing Improvements: Add more repeatable automated tests for scanner behaviour, error handling, and vulnerability detection.

These are potential enhancements, not claims that the features are already implemented.

---

## 🏆 Supervisor Resume Highlights (Aditya Kumar Jha)
If you are adding this project to your resume, consider using these bullet points:
*   **Technical Leadership:** Supervised and architected a 5-person engineering team to build **APISweeper**, a modular Dynamic Application Security Testing (DAST) tool over a 20-day agile sprint.
*   **System Architecture:** Designed the extensible core engine in Python, establishing standard inheritance patterns (`BaseScanner`) enabling concurrent development of passive, active, and logic-based vulnerability modules.
*   **Full-Stack Development:** Engineered both a vulnerable Flask-based dummy target API for zero-risk local testing, and supervised the integration of a premium Streamlit Web UI dashboard to visualize scanner findings in real-time.
*   **Project Management:** Enforced strict Git Flow (feature branching, PR reviews) and defined the project roadmap, ensuring seamless integration of complex modules (BOLA checks, Rate Limiting, JWT validation).

---

## 📚 References
-APISweeper Repository
-OWASP API Security Top 10
-OWASP Web Security Testing Guide
-Python Requests Documentation
-Flask Documentation
-Streamlit Documentation
-JSON Web Token Specification — RFC 7519