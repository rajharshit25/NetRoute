
def disable_link(network, router1, router2):
    """Disable a link between two routers."""
    if not network.has_edge(router1, router2):
        raise ValueError(
            f"No link exists between {router1} and {router2}"
        )

    network[router1][router2]["active"] = False


def enable_link(network, router1, router2):
    """Restore a previously disabled link."""
    if not network.has_edge(router1, router2):
        raise ValueError(
            f"No link exists between {router1} and {router2}"
        )

    network[router1][router2]["active"] = True


def get_active_network(network):
    """Return a copy containing only active links."""
    active_network = network.copy()

    for router1, router2, data in list(active_network.edges(data=True)):
        if data.get("active", True) is False:
            active_network.remove_edge(router1, router2)

    return active_network
