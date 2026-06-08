import json
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


SLOW_RESPONSE_LIMIT_MS = 500
CONFIG_FILE = "config.json"
REQUEST_TIMEOUT_SECONDS = 5
MAX_WORKERS = 5
MAX_RETRIES = 2


def load_servers():
    servers_from_env = os.getenv("SERVERS")

    if servers_from_env:
        servers = servers_from_env.split(",")
        cleaned_servers = []

        for server in servers:
            cleaned_server = server.strip()

            if cleaned_server:
                cleaned_servers.append(cleaned_server)

        return cleaned_servers

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

        servers = config.get("servers", [])

        if servers:
            return servers

    raise ValueError(
        "No servers found. Please set SERVERS environment variable or create config.json."
    )


def validate_json_body(response):
    try:
        data = response.json()

        if data.get("status") == "ok":
            return "JSON_OK"

        return "JSON_STATUS_MISSING"

    except ValueError:
        return "NOT_JSON"


def get_health_status(status_code):
    if 200 <= status_code <= 299:
        return "OK"

    return "DOWN"


def is_slow_response(response_time_ms):
    return response_time_ms > SLOW_RESPONSE_LIMIT_MS


def check_server_once(url):
    start_time = time.time()

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)

        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000)

        status_code = response.status_code
        health_status = get_health_status(status_code)
        json_status = validate_json_body(response)
        is_slow = is_slow_response(response_time_ms)

        return {
            "url": url,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "health_status": health_status,
            "json_status": json_status,
            "is_slow": is_slow,
            "error": None
        }

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "health_status": "TIMEOUT",
            "json_status": "NOT_CHECKED",
            "is_slow": False,
            "error": "Request timed out"
        }

    except requests.exceptions.RequestException as error:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "health_status": "ERROR",
            "json_status": "NOT_CHECKED",
            "is_slow": False,
            "error": str(error)
        }


def check_server(url):
    attempts = 0
    last_result = None

    while attempts <= MAX_RETRIES:
        attempts += 1

        result = check_server_once(url)
        result["attempts"] = attempts

        if result["health_status"] == "OK":
            return result

        last_result = result

    return last_result


def format_result(result):
    url = result["url"]
    health_status = result["health_status"]
    status_code = result["status_code"]
    response_time_ms = result["response_time_ms"]
    is_slow = result["is_slow"]
    attempts = result.get("attempts", 1)

    retry_text = ""

    if attempts > 1:
        retry_text = f" after {attempts} attempts"

    if health_status == "TIMEOUT":
        return f"{url:<35} — TIMEOUT{retry_text}"

    if health_status == "ERROR":
        return f"{url:<35} — ERROR{retry_text}"

    slow_text = ""

    if is_slow:
        slow_text = " [slow]"

    return f"{url:<35} — {health_status} ({status_code}) — {response_time_ms}ms{slow_text}{retry_text}"


def check_all_servers(servers):
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_server = {}

        for server in servers:
            future = executor.submit(check_server, server)
            future_to_server[future] = server

        for future in as_completed(future_to_server):
            result = future.result()
            results.append(result)

    failed_services = []

    for result in results:
        print(format_result(result))

        if result["health_status"] in ["DOWN", "TIMEOUT", "ERROR"]:
            failed_services.append(result["url"])

    return failed_services


def print_failed_services(failed_services):
    print()

    if failed_services:
        print(f"Failed services: {', '.join(failed_services)}")
    else:
        print("Failed services: None")


def main():
    try:
        servers = load_servers()

        print(f"Loaded {len(servers)} servers")
        print()

        failed_services = check_all_servers(servers)
        print_failed_services(failed_services)

    except ValueError as error:
        print(f"Configuration error: {error}")


if __name__ == "__main__":
    main()