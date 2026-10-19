
import networkx as nx


def find_shortest_route(network, source, destination):
    """Find the lowest-cost route between two routers."""

    if source not in network:
        raise ValueError(f"Unknown source router: {source}")

    if destination not in network:
        raise ValueError(f"Unknown destination router: {destination}")

    try:
        path = nx.shortest_path(
            network,
            source=source,
            target=destination,
            weight="cost",
        )

        total_cost = nx.shortest_path_length(
            network,
            source=source,
            target=destination,
            weight="cost",
        )

        return {
            "source": source,
            "destination": destination,
            "path": path,
            "cost": total_cost,
            "reachable": True,
        }

    except nx.NetworkXNoPath:
        return {
            "source": source,
            "destination": destination,
            "path": [],
            "cost": None,
            "reachable": False,
        }
