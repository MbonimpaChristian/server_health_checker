import json
import time
import requests


SLOW_RESPONSE_LIMIT_MS = 500


def load_servers():
    with open("config.json", "r") as file:
        config = json.load(file)

    servers = config["servers"]
    return servers


def validate_json_body(response):
    try:
        data = response.json()

        if data.get("status") == "ok":
            return "JSON_OK"
        else:
            return "JSON_STATUS_MISSING"

    except ValueError:
        return "NOT_JSON"


def check_server(url):
    start_time = time.time()

    try:
        response = requests.get(url, timeout=5)

        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000)

        status_code = response.status_code
        json_status = validate_json_body(response)

        if 200 <= status_code <= 299:
            health_status = "OK"
        else:
            health_status = "DOWN"

        is_slow = response_time_ms > SLOW_RESPONSE_LIMIT_MS

        result = {
            "url": url,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "health_status": health_status,
            "json_status": json_status,
            "is_slow": is_slow
        }

        return result

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "health_status": "TIMEOUT",
            "json_status": "NOT_CHECKED",
            "is_slow": False
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


def format_result(result):
    url = result["url"]
    health_status = result["health_status"]
    status_code = result["status_code"]
    response_time_ms = result["response_time_ms"]
    is_slow = result["is_slow"]

    if health_status == "TIMEOUT":
        return f"{url:<35} — TIMEOUT"

    if health_status == "ERROR":
        return f"{url:<35} — ERROR"

    slow_text = ""

    if is_slow:
        slow_text = " [slow]"

    return f"{url:<35} — {health_status} ({status_code}) — {response_time_ms}ms{slow_text}"


def main():
    servers = load_servers()
    print(f"Loaded {len(servers)} servers")
    print()

    for server in servers:
        result = check_server(server)
        formatted_result = format_result(result)
        print(formatted_result)


if __name__ == "__main__":
    main()