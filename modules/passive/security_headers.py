import requests
from core.base import BaseScanner

class SecurityHeadersScanner(BaseScanner):

    REQUIRED_HEADERS = {
        "X-Frame-Options": {
            "severity": "LOW",
            "description": "Missing X-Frame-Options header may increase clickjacking risk."
        },
        "X-Content-Type-Options": {
            "severity": "MEDIUM",
            "description": "Missing X-Content-Type-Options header may increase MIME sniffing risk."
        },
        "Content-Security-Policy": {
            "severity": "HIGH",
            "description": "Missing Content-Security-Policy header may increase XSS risk."
        },
        "Strict-Transport-Security": {
            "severity": "HIGH",
            "description": "Missing Strict-Transport-Security header may increase SSL stripping risk."
        },
        "Referrer-Policy": {
            "severity": "MEDIUM",
            "description": "Missing Referrer-Policy header may expose sensitive information."
        },      
        "Permissions-Policy": {
            "severity": "HIGH",
            "description": "Missing Permissions-Policy header may increase privacy risks."
        },
        "Cross-Origin-Resource-Policy": {
            "severity": "MEDIUM",
            "description": "Missing Cross-Origin-Resource-Policy header may increase cross-origin resource access risks."
        },
        "Cross-Origin-Opener-Policy": {
            "severity": "HIGH",
            "description": "Missing Cross-Origin-Opener-Policy header may increase cross-origin opener risks."
        }
    }

    def scan(self) -> None:
        try:
            response = requests.get(self.target_url , timeout=10)

            for header, details in self.REQUIRED_HEADERS.items():
                if header not in response.headers:
                    self.add_finding(
                        severity=details["severity"],
                        endpoint=self.target_url,
                        description=details["description"]
                    )

        except requests.RequestException as error:
            print(f"Error scanning {self.target_url}: {error}")