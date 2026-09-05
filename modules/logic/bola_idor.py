import requests
from core.base import BaseScanner


class BOLAChecker(BaseScanner):
    """
    Tests whether a user authenticated as User B can access objects
    that actually belong to User A by swapping the object ID while
    keeping User B's own token Also runs a secondary sequentialID
    exposure test using a single account.
    """

    def __init__(self, target_url: str, token: str, token_b: str, endpoints_with_ids: list[dict]):
        
        super().__init__(target_url, token)  
        self.token_b = token_b
        self.endpoints_with_ids = endpoints_with_ids

        self.session_a = requests.Session()
        self.session_a.headers.update({"Authorization": f"Bearer {self.token}"})

        self.session_b = requests.Session()
        self.session_b.headers.update({"Authorization": f"Bearer {self.token_b}"})

    def _full_url(self, path: str) -> str:
        return f"{self.target_url.rstrip('/')}{path}"

    def scan(self) -> None:
        """
        Runs both BOLA tests across every configured endpoint
        """
        for endpoint in self.endpoints_with_ids:
            path_template = endpoint["path_template"]
            user_a_id = endpoint["known_id_user_a"]

            self._check_cross_account_access(path_template, user_a_id)

            try:
                base_id = int(user_a_id)
                self._check_sequential_ids(path_template, range(base_id, base_id + 10))
            except ValueError:
                pass  # non-numeric ID — skip sequential test, cross-account test still ran

    def _check_cross_account_access(self, path_template: str, user_a_object_id: str) -> None:
        """Core test: request User A's object using User B's session."""
        target_path = path_template.replace("{id}", str(user_a_object_id))
        url = self._full_url(target_path)

        response = self.session_b.get(url)

        if response.status_code == 200:
            self.add_finding(
                severity="CRITICAL",
                endpoint=target_path,
                description=(
                    f"BOLA/IDOR: Requested {target_path} (belongs to User A) while "
                    f"authenticated as User B. Server returned HTTP 200 with object "
                    f"data instead of 403/404. Impact: any authenticated user can "
                    f"read another user's resource by changing the ID in the request "
                    f"URL; if this endpoint supports PUT/DELETE, modification or "
                    f"deletion of other users' data is likely possible too."
                ),
            )

    def _check_sequential_ids(self, path_template: str, id_range: range) -> None:
        """Secondary test: predictable/enumerable IDs, tested with User A's own session."""
        successful_ids = []

        for object_id in id_range:
            target_path = path_template.replace("{id}", str(object_id))
            url = self._full_url(target_path)
            response = self.session_a.get(url)
            if response.status_code == 200:
                successful_ids.append(object_id)

        if len(successful_ids) >= (len(id_range) * 0.5):
            self.add_finding(
                severity="HIGH",
                endpoint=path_template,
                description=(
                    f"BOLA/IDOR (enumeration): Tested {len(id_range)} sequential IDs "
                    f"on {path_template}; {len(successful_ids)} returned HTTP 200 to "
                    f"a single session ({successful_ids}). IDs appear predictable and "
                    f"not access-controlled per-ID, allowing bulk data harvesting via "
                    f"enumeration without compromising individual credentials."
                ),
            )


# ---------------------------------------------------------------
# Quick manual test (remove or move to tests/ once pytest is set up)
# ---------------------------------------------------------------
if __name__ == "__main__":
    test_endpoints = [
        {"path_template": "/api/orders/{id}", "known_id_user_a": "1"},
    ]

    checker = BOLAChecker(
        target_url="http://localhost:5001",
        token="token_alice_123",
        token_b="token_bob_456",
        endpoints_with_ids=[
        {"path_template": "/api/v1/orders/{id}", "known_id_user_a": "101"},
    ],
    )
    checker.scan()

    for finding in checker.get_results():
        print(f"[{finding['severity']}] {finding['endpoint']} — {finding['description'][:80]}...")