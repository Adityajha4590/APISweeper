from modules.passive.verbose_errors import VerboseErrorsScanner


scanner = VerboseErrorsScanner(
    target_url="https://gorest.co.in/public/v2/users",
    token="YOUR_TOKEN"
)

scanner.scan()

results = scanner.get_results()

print(results)