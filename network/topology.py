import networkx as nx


def create_sample_network():
    """Create the original sample network."""
    network = nx.Graph()

    network.add_edge("R1", "R2", cost=2)
    network.add_edge("R1", "R3", cost=5)
    network.add_edge("R2", "R3", cost=1)
    network.add_edge("R2", "R4", cost=4)
    network.add_edge("R3", "R4", cost=2)

    return network


def create_star_topology(number_of_routers=5):
    """Create a star topology with R1 as the central router."""
    if number_of_routers < 2:
        raise ValueError("A star needs at least 2 routers.")

    network = nx.Graph()
    routers = [f"R{i}" for i in range(1, number_of_routers + 1)]
    network.add_nodes_from(routers)

    center = routers[0]

    for router in routers[1:]:
        network.add_edge(center, router, cost=1)

    return network


def create_ring_topology(number_of_routers=5):
    """Create a ring topology."""
    if number_of_routers < 3:
        raise ValueError("A ring needs at least 3 routers.")

    network = nx.Graph()
    routers = [f"R{i}" for i in range(1, number_of_routers + 1)]

    for i, router in enumerate(routers):
        next_router = routers[(i + 1) % number_of_routers]
        network.add_edge(router, next_router, cost=1)

    return network


def create_mesh_topology(number_of_routers=5):
    """Create a full mesh where every router connects to every other."""
    if number_of_routers < 2:
        raise ValueError("A mesh needs at least 2 routers.")

    network = nx.complete_graph(number_of_routers)
    network = nx.relabel_nodes(
        network,
        {i: f"R{i + 1}" for i in range(number_of_routers)}
    )

    for router1, router2 in network.edges():
        network[router1][router2]["cost"] = 1

    return network
