import time

from core.base import BaseScanner


class RateLimitScanner(BaseScanner):
    """
    Active rate-limiting security checks for APISweeper.

    Checks whether the target API appears to enforce request
    throttling by sending a configurable number of requests
    in a short period.

    Indicators of rate limiting:
    - HTTP 429 responses
    - Retry-After header
    - X-RateLimit-* headers
    - RateLimit-* headers
    """

    def __init__(
        self,
        target_url: str,
        token: str = None,
        request_count: int = 20,
        delay: float = 0.0,
    ):
        super().__init__(target_url, token)

        self.request_count = request_count
        self.delay = delay

    def scan(self) -> None:
        """Run the rate-limiting security check."""

        if not self.target_url:
            return

        if self.request_count <= 0:
            self.add_finding(
                "INFO",
                self.target_url,
                "Rate-limit test skipped because request_count "
                "must be greater than zero."
            )
            return

        session = getattr(self, "session", None)

        if session is None:
            import requests
            session = requests.Session()

        headers = {}

        if self.token:
            token = self.token.strip()

            if token.lower().startswith("bearer "):
                headers["Authorization"] = token
            else:
                headers["Authorization"] = f"Bearer {token}"

        successful_requests = 0
        rate_limited_requests = 0
        response_times = []

        rate_limit_headers = set()

        for _ in range(self.request_count):
            start = time.perf_counter()

            try:
                response = session.get(
                    self.target_url,
                    headers=headers,
                    timeout=10,
                )

                elapsed = time.perf_counter() - start
                response_times.append(elapsed)

                if response.status_code == 429:
                    rate_limited_requests += 1

                else:
                    successful_requests += 1

                for header in response.headers:
                    header_lower = header.lower()

                    if (
                        "ratelimit" in header_lower
                        or header_lower == "retry-after"
                    ):
                        rate_limit_headers.add(header)

            except Exception as exc:
                self.add_finding(
                    "INFO",
                    self.target_url,
                    f"Rate-limit testing encountered a request error: "
                    f"{type(exc).__name__}."
                )
                return

            if self.delay > 0:
                time.sleep(self.delay)

        # ---------------------------------------------------------
        # Evidence that rate limiting exists
        # ---------------------------------------------------------

        if rate_limited_requests > 0:

            self.add_finding(
                "INFO",
                self.target_url,
                f"Rate limiting appears to be enabled. "
                f"{rate_limited_requests} of {self.request_count} "
                f"requests returned HTTP 429."
            )

            return

        if rate_limit_headers:

            headers_found = ", ".join(sorted(rate_limit_headers))

            self.add_finding(
                "INFO",
                self.target_url,
                "The API exposes rate-limiting related headers: "
                f"{headers_found}. However, active throttling was not "
                "observed during this test."
            )

            return

        # ---------------------------------------------------------
        # No obvious rate limiting detected
        # ---------------------------------------------------------

        self.add_finding(
            "MEDIUM",
            self.target_url,
            f"No effective rate limiting was detected after sending "
            f"{self.request_count} requests. All requests completed "
            f"without receiving HTTP 429 or recognizable rate-limit "
            f"headers. This may expose the API to brute-force, "
            f"credential-stuffing, scraping, or resource-exhaustion "
            f"attacks."
        )
