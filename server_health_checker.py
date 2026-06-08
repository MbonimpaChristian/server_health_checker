import json


def load_servers():
    with open("config.json", "r") as file:
        config = json.load(file)

    servers = config["servers"]
    return servers


def main():
    servers = load_servers()
    print(f"Loaded {len(servers)} servers")

    for server in servers:
        print(server)


if __name__ == "__main__":
    main()