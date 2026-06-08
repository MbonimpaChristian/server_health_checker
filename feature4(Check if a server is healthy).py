import json
import time
import requests


def load_servers():
    with open("config.json", "r") as file:
        config = json.load(file)

    servers = config["servers"]
    return servers


def check_server(url):
    start_time = time.time()

    try:
        response = requests.get(url, timeout=5)

        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000)

        status_code = response.status_code

        if 200 <= status_code <= 299:
            health_status = "OK"
        else:
            health_status = "DOWN"

        result = {
            "url": url,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "health_status": health_status
        }

        return result

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "health_status": "TIMEOUT"
        }

    except requests.exceptions.RequestException as error:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "health_status": "ERROR",
            "error": str(error)
        }


def main():
    servers = load_servers()
    print(f"Loaded {len(servers)} servers")

    for server in servers:
        result = check_server(server)
        print(result)


if __name__ == "__main__":
    main()