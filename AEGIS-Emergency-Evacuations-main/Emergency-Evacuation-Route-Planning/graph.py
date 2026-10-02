import json


def load_building_map(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    graph = {}

    # Create an empty list for every location
    for location in data["locations"]:
        graph[location] = []

    # Add connections in both directions
    for source, destination, distance in data["connections"]:
        graph[source].append((destination, distance))
        graph[destination].append((source, distance))

    return graph, data["locations"], data["exits"]


if __name__ == "__main__":
    graph, locations, exits = load_building_map(
        "data/building_map.json"
    )

    print("Locations:")
    for code, name in locations.items():
        print(f"{code} → {name}")

    print("\nExits:")
    for exit_code in exits:
        print(f"{exit_code} → {locations[exit_code]}")

    print("\nConnections:")
    for location, neighbours in graph.items():
        print(f"{location}: {neighbours}")