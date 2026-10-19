
import pytest

from network.topology import create_sample_network
from network.routing import find_shortest_route
from network.failures import (
    disable_link,
    enable_link,
    get_active_network,
)


def test_rerouting_after_link_failure():
    network = create_sample_network()

    disable_link(network, "R2", "R3")
    active_network = get_active_network(network)

    result = find_shortest_route(active_network, "R1", "R4")

    assert result["reachable"] is True
    assert result["path"] == ["R1", "R2", "R4"]
    assert result["cost"] == 6


def test_failed_link_is_removed_from_active_network():
    network = create_sample_network()

    disable_link(network, "R2", "R3")
    active_network = get_active_network(network)

    assert network.has_edge("R2", "R3")
    assert not active_network.has_edge("R2", "R3")


def test_restoring_link():
    network = create_sample_network()

    disable_link(network, "R2", "R3")
    enable_link(network, "R2", "R3")

    active_network = get_active_network(network)
    result = find_shortest_route(active_network, "R1", "R4")

    assert result["reachable"] is True
    assert result["cost"] == 5


def test_disabling_unknown_link():
    network = create_sample_network()

    with pytest.raises(ValueError):
        disable_link(network, "R1", "R99")
