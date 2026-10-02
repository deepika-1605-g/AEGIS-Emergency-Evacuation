import heapq

from graph import load_building_map


def dijkstra(graph, start, blocked_edges=None):

    if blocked_edges is None:
        blocked_edges = set()

    # Shortest known distance to every location
    distances = {}

    # Previous location used to reach each location
    previous = {}

    # Initially, every location is infinitely far away
    for location in graph:
        distances[location] = float("inf")
        previous[location] = None

    # Starting location has distance 0
    distances[start] = 0

    # Priority queue
    priority_queue = [(0, start)]

    while priority_queue:

        current_distance, current_location = heapq.heappop(
            priority_queue
        )

        # Ignore outdated information
        if current_distance > distances[current_location]:
            continue

        # Check neighbouring locations
        for neighbour, edge_distance in graph[current_location]:

            # Represent the connection between two locations
            edge = frozenset([current_location, neighbour])

            # Skip blocked paths
            if edge in blocked_edges:
                continue

            # Calculate new distance
            new_distance = current_distance + edge_distance

            # If this route is shorter
            if new_distance < distances[neighbour]:

                distances[neighbour] = new_distance

                previous[neighbour] = current_location

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbour)
                )

    return distances, previous


def build_path(previous, start, destination):

    path = []

    current = destination

    while current is not None:

        path.append(current)

        if current == start:
            break

        current = previous[current]

    # No route exists
    if path[-1] != start:
        return []

    path.reverse()

    return path


# --------------------------------------------------
# TEST THE EMERGENCY ROUTE
# --------------------------------------------------

if __name__ == "__main__":

    # Load building
    graph, locations, exits = load_building_map(
        "data/building_map.json"
    )

    # Person starts in Room 101
    start = "G3"

    # Emergency:
    # Staircase A → Exit A is blocked
    blocked_edges = {
        frozenset(["G5", "G6"])
    }

    # Run Dijkstra
    distances, previous = dijkstra(
        graph,
        start,
        blocked_edges
    )

    print("\n========================================")
    print("   EMERGENCY EVACUATION ROUTE PLANNER")
    print("========================================")

    print(f"\nStarting Location: {locations[start]}")

    print("\nBlocked Route:")
    print("Staircase A → Exit A")

    print("\nAvailable Exit Routes:")

    for exit_location in exits:

        path = build_path(
            previous,
            start,
            exit_location
        )

        if path:

            route = " → ".join(
                locations[location]
                for location in path
            )

            print(
                f"\n{locations[exit_location]}"
            )

            print(f"Route: {route}")

            print(
                f"Distance: "
                f"{distances[exit_location]} m"
            )

        else:

            print(
                f"\n{locations[exit_location]}: "
                "NO ROUTE AVAILABLE"
            )