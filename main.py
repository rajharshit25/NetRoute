
from network.topology import create_sample_network
from network.addressing import assign_ip_addresses
from network.routing import find_shortest_route
from network.failures import (
    disable_link,
    enable_link,
    get_active_network,
)


def show_route(network, source, destination):
    result = find_shortest_route(network, source, destination)

    if result["reachable"]:
        print("Route:", " -> ".join(result["path"]))
        print("Total cost:", result["cost"])
    else:
        print(f"No route exists from {source} to {destination}.")


def main():
    network = create_sample_network()

    print("=" * 45)
    print("       NETROUTE NETWORK SIMULATOR")
    print("=" * 45)

    # Step 1: Show router IP addresses
    print("\n1. ROUTER IP ADDRESSES")
    addresses = assign_ip_addresses(network.nodes())

    for router, ip in addresses.items():
        print(f"{router}: {ip}")

    # Step 2: Show original connections
    print("\n2. NETWORK CONNECTIONS")

    for router1, router2, data in network.edges(data=True):
        print(f"{router1} <--> {router2} | Cost: {data['cost']}")

    # Step 3: Find the original shortest route
    print("\n3. ORIGINAL ROUTE: R1 TO R4")
    show_route(get_active_network(network), "R1", "R4")

    # Step 4: Simulate a link failure
    print("\n4. SIMULATING LINK FAILURE: R2 -- R3")
    disable_link(network, "R2", "R3")
    print("Link R2 -- R3 is now DOWN.")

    print("\n5. ROUTE AFTER FAILURE")
    show_route(get_active_network(network), "R1", "R4")

    # Step 5: Restore the link
    print("\n6. RESTORING LINK: R2 -- R3")
    enable_link(network, "R2", "R3")
    print("Link R2 -- R3 is now UP.")

    print("\n7. ROUTE AFTER RECOVERY")
    show_route(get_active_network(network), "R1", "R4")

    print("\n" + "=" * 45)
    print("       SIMULATION COMPLETE")
    print("=" * 45)


if __name__ == "__main__":
    main()
