from modules.passive.security_headers import SecurityHeadersScanner


scanner = SecurityHeadersScanner(
    "http://127.0.0.1:5001/api/v1/status"
)

scanner.scan()

results = scanner.get_results()

print(results)