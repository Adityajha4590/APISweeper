import argparse
import requests
import json


def scan_target(url, token=None, method="GET", data=None):
    print("[+] Sending HTTP request...")

    try:
        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        if method == "POST":
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=10
            )
        else:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

        print("[+] Response received successfully!")
        return response

    except requests.exceptions.ConnectionError:
        print("[!] Error: Could not connect to the target.")
        print("[!] Make sure the API is running and the URL is correct.")
        return None

    except requests.exceptions.Timeout:
        print("[!] Error: The target took too long to respond.")
        return None

    except requests.exceptions.RequestException as error:
        print("[!] HTTP request failed.")
        print("[!] Error:", error)
        return None


def create_scan_result(url, response):
    return {
        "target": url,
        "method": response.request.method,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "response": response.text,
        "findings": []
    }


def save_report(scan_result, output_file):
    try:
        with open(output_file, "w") as file:
            json.dump(scan_result, file, indent=4)

        print(f"\n[+] Report saved to: {output_file}")

    except OSError as error:
        print("[!] Could not save report.")
        print("[!] Error:", error)

def run_scan(url, token=None, method="GET", data=None):
    """
    Run the HTTP request and return the basic scan result.
    """

    response = scan_target(
        url,
        token,
        method,
        data
    )

    if response is None:
        return None

    return create_scan_result(
        url,
        response
    )


def main():
    parser = argparse.ArgumentParser(
        description="APISweeper - REST API Security Scanner"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Target API URL to scan"
    )

    parser.add_argument(
        "--output",
        help="Save scan results to a JSON file"
    )

    parser.add_argument(
        "--token",
        help="Authentication token for the target API"
    )

    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST"],
        help="HTTP method to use for the scan"
    )

    parser.add_argument(
        "--data",
        help="JSON request body for POST requests"
    )

    args = parser.parse_args()

    url = args.url
    output_file = args.output
    token = args.token
    method = args.method
    data = args.data

    # Convert command-line JSON text into a Python object
    if isinstance(data, str):
        try:
            data = json.loads(data)

        except json.JSONDecodeError:
            print("[!] Error: Invalid JSON data.")
            return

    # POST requests should receive JSON data
    if method == "POST" and data is None:
        print("[!] Error: POST requests require --data.")
        print(
            '[!] Example: '
            '--data \'{"username":"admin","password":"admin123"}\''
        )
        return

    print("=" * 50)
    print("          APISWEEPER SECURITY SCANNER")
    print("=" * 50)
    print("Target:", url)
    print("Method:", method)
    print()

    response = scan_target(
        url,
        token,
        method,
        data
    )

    if response is None:
        return

    print()
    print("Status Code:", response.status_code)

    print("\nHTTP Headers:")

    for header, value in response.headers.items():
        print(f"{header}: {value}")

    # Create the basic scan result.
    # Security modules will add their findings later.
    scan_result = create_scan_result(
        url,
        response
    )

    if output_file:
        save_report(
            scan_result,
            output_file
        )

    print("\nResponse:")
    print(response.text)

    print("\n" + "=" * 50)
    print("SCAN COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()