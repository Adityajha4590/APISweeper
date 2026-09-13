import base64
import json
import time

from core.base import BaseScanner


class JWTScanner(BaseScanner):
    """
    Active JWT security checks for APISweeper.

    Checks:
    - JWT structure
    - 'none' algorithm
    - missing/invalid expiration
    - expired token
    - sensitive information in JWT payload
    """

    def __init__(self, target_url: str, token: str = None):
        super().__init__(target_url, token)

    @staticmethod
    def _decode_segment(segment: str):
        """Decode a base64url encoded JWT segment."""
        try:
            padding = "=" * (-len(segment) % 4)
            decoded = base64.urlsafe_b64decode(
                segment + padding
            )
            return json.loads(decoded.decode("utf-8"))
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
            return None

    def _parse_token(self):
        """Parse the JWT into header and payload."""
        if not self.token:
            return None, None

        token = self.token.strip()

        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        parts = token.split(".")

        if len(parts) != 3:
            return None, None

        header = self._decode_segment(parts[0])
        payload = self._decode_segment(parts[1])

        return header, payload

    def check_structure(self):
        """Check whether the supplied token has valid JWT structure."""
        if not self.token:
            return

        token = self.token.strip()

        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        if len(token.split(".")) != 3:
            self.add_finding(
                "LOW",
                self.target_url,
                "The supplied authentication token does not follow the "
                "standard three-part JWT structure."
            )

    def check_none_algorithm(self, header):
        """Detect the insecure JWT 'none' signing algorithm."""
        if not header:
            return

        algorithm = str(header.get("alg", "")).lower()

        if algorithm == "none":
            self.add_finding(
                "HIGH",
                self.target_url,
                "The JWT uses the 'none' algorithm, which provides no "
                "cryptographic signature. If accepted by the API, an "
                "attacker may be able to forge authentication tokens."
            )

    def check_expiration(self, payload):
        """Check the JWT expiration claim."""
        if not payload:
            return

        if "exp" not in payload:
            self.add_finding(
                "MEDIUM",
                self.target_url,
                "The JWT does not contain an expiration ('exp') claim. "
                "Without an expiration mechanism, a token may remain "
                "valid indefinitely."
            )
            return

        try:
            expiration = float(payload["exp"])
        except (TypeError, ValueError):
            self.add_finding(
                "MEDIUM",
                self.target_url,
                "The JWT contains an invalid expiration ('exp') claim."
            )
            return

        if expiration < time.time():
            self.add_finding(
                "LOW",
                self.target_url,
                "The supplied JWT is already expired. The API should "
                "reject expired authentication tokens."
            )

    def check_sensitive_data(self, payload):
        """Detect obviously sensitive information in the JWT payload."""
        if not payload:
            return

        sensitive_fields = {
            "password",
            "passwd",
            "secret",
            "private_key",
            "credit_card",
            "card_number"
        }

        exposed = [
            key for key in payload
            if str(key).lower() in sensitive_fields
        ]

        if exposed:
            self.add_finding(
                "HIGH",
                self.target_url,
                "The JWT payload contains potentially sensitive "
                "information: " + ", ".join(exposed) +
                ". JWT payloads are encoded rather than encrypted and "
                "should not contain sensitive secrets."
            )

    def scan(self) -> None:
        """Run all JWT security checks."""

        if not self.token:
            self.add_finding(
                "LOW",
                self.target_url,
                "No JWT/Bearer token was supplied. JWT security checks "
                "could not be performed."
            )
            return

        header, payload = self._parse_token()

        if header is None or payload is None:
            self.add_finding(
                "MEDIUM",
                self.target_url,
                "The supplied token is not a valid JWT and could not "
                "be decoded."
            )
            return

        self.check_structure()
        self.check_none_algorithm(header)
        self.check_expiration(payload)
        self.check_sensitive_data(payload)
