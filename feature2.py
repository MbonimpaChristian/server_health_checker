import json
import requests


def load_servers():
    with open("config.json", "r") as file:
        config = json.load(file)

    servers = config["servers"]
    return servers


def check_server(url):
    response = requests.get(url)

    result = {
        "url": url,
        "status_code": response.status_code
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