# 🛡️ APISweeper: Lightweight Vulnerable API Scanner

**APISweeper** is a lightweight, Python-based Dynamic Application Security Testing (DAST) tool purpose-built for REST APIs. It automatically scans target endpoints for critical security misconfigurations and vulnerabilities mapped to the **OWASP API Security Top 10**.

Unlike heavy, enterprise-grade scanners (like Burp Suite or OWASP ZAP), APISweeper is designed to be fast, modular, and easy to run from the command line, generating severity-scored vulnerability reports.

---

## 👥 Meet the Team

This project was developed over a 20-day sprint by a 5-person security engineering team:

*   **[Your Name]** (Supervisor / Lead Architect) - Core integration, target dummy API, and project management.
*   **Jatin** - Core Scanner CLI Engine & HTTP handling.
*   **Keshav** - Passive Scanning (Security Headers, Verbose Error Leaks).
*   **Rishab** - Active Scanning (Rate Limiting, JWT algorithm checks).
*   **Pranav** - Logic Scanning (BOLA/IDOR) & PDF/JSON Report Generation.

---

## 🚀 Project Roadmap & Phases

This project was strictly managed and developed across 4 agile phases:

### Phase 1: Foundation & Setup (Days 1 - 4)
*   **Repository Initialization:** Set up Git flow, branch protections, and contribution guidelines.
*   **Dummy Target API:** Developed a deliberately vulnerable local API (using Flask/FastAPI) to safely test our scanner payloads against without hitting live internet targets.
*   **Architecture Design:** Defined the base Python classes so all vulnerability modules plug into the main engine uniformly.

### Phase 2: Core Framework & Basic Modules (Days 5 - 10)
*   **CLI Engine (`scanner.py`):** Implemented `argparse` for robust command-line target ingestion.
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
