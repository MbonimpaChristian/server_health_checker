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

    response = requests.get(url)

    end_time = time.time()

    response_time_ms = round((end_time - start_time) * 1000)

    result = {
        "url": url,
        "status_code": response.status_code,
        "response_time_ms": response_time_ms
    }

    return result


def main():
    servers = load_servers()
    print(f"Loaded {len(servers)} servers")

    first_server = servers[0]

    result = check_server(first_server)

    print(result)


if __name__ == "__main__":
    main()