
import ipaddress


def assign_ip_addresses(routers, subnet="192.168.1.0/24"):
    """Assign a unique IPv4 address to each router."""
    network = ipaddress.ip_network(subnet, strict=True)
    available_ips = network.hosts()
    addresses = {}

    for router in routers:
        try:
            addresses[router] = str(next(available_ips))
        except StopIteration:
            raise ValueError("Not enough IP addresses for all routers.")

    return addresses


def validate_ip_address(address):
    """Return True if the address is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def get_subnet_details(subnet="192.168.1.0/24"):
    """Return basic information about an IPv4 subnet."""
    network = ipaddress.ip_network(subnet, strict=True)

    return {
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "subnet_mask": str(network.netmask),
        "prefix_length": network.prefixlen,
        "total_addresses": network.num_addresses,
        "usable_hosts": network.num_addresses - 2,
    }
