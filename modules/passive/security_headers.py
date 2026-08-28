#import necessary libraries

import requests
from core.base import BaseScanner

"""
    ======================================================================
    APISweeper Passive Security Headers Scanner Module
    ======================================================================
"""

#class to scan for security headers in HTTP responses
class SecurityHeadersScanner(BaseScanner):

    #define required security headers and their severity levels
    
    """
    1) X-Frame-Options: Prevents clickjacking attacks by controlling whether
      a page can be displayed in an iframe.
    2) X-Content-Type-Options: Prevents MIME type sniffing, which can lead to
      security vulnerabilities.
    3) Content-Security-Policy: Helps prevent XSS attacks by specifying which
      sources of content are allowed to be loaded.
    4) Strict-Transport-Security: Enforces secure (HTTPS) connections to the server.
    5) Referrer-Policy: Controls how much referrer information is sent with requests.
    6) Permissions-Policy: Allows or denies the use of browser features and APIs.
    7) Cross-Origin-Resource-Policy: Controls how resources are shared across origins.
    8) Cross-Origin-Opener-Policy: Helps isolate browsing contexts to prevent
        cross-origin attacks.
    """

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

    #defining scan function to check for security headers in the HTTP response
    def scan(self) -> None:
        try:
            #make a GET request to the target URL with a timeout of 10 seconds
            response = requests.get(self.target_url , timeout=10)

            #check for each required header in the response headers
            for header, details in self.REQUIRED_HEADERS.items():
                #if the header is not present in the response headers, add a finding with the appropriate severity and description
                if header not in response.headers:
                    #if the header is Strict-Transport-Security and the target URL does not start with https, skip adding a finding
                    if header == "Strict-Transport-Security" and not self.target_url.startswith("https://"):
                        continue
                    #add a finding for the missing header
                    self.add_finding(
                        severity=details["severity"],
                        endpoint=self.target_url,
                        description=details["description"]
                    )
        #handle any request exceptions that may occur during the GET request
        except requests.RequestException as error:
            print(f"Error scanning {self.target_url}: {error}")