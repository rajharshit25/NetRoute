
from network.addressing import (
    assign_ip_addresses,
    validate_ip_address,
    get_subnet_details,
)


def test_ip_assignment():
    addresses = assign_ip_addresses(["R1", "R2", "R3"])

    assert addresses["R1"] == "192.168.1.1"
    assert addresses["R2"] == "192.168.1.2"
    assert addresses["R3"] == "192.168.1.3"
    assert len(set(addresses.values())) == 3


def test_ip_validation():
    assert validate_ip_address("192.168.1.10")
    assert validate_ip_address("10.0.0.1")
    assert not validate_ip_address("300.168.1.10")
    assert not validate_ip_address("hello")


def test_subnet_details():
    details = get_subnet_details("192.168.1.0/24")

    assert details["network_address"] == "192.168.1.0"
    assert details["broadcast_address"] == "192.168.1.255"
    assert details["subnet_mask"] == "255.255.255.0"
    assert details["prefix_length"] == 24
    assert details["usable_hosts"] == 254
