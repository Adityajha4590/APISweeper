from modules.passive.security_headers import SecurityHeadersScanner


scanner = SecurityHeadersScanner(
    "https://www.keshavgarg.tech/"
)

scanner.scan()

results = scanner.get_results()

print(results)