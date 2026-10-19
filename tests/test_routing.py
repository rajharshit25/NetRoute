
import networkx as nx
import pytest

from network.topology import create_sample_network
from network.routing import find_shortest_route


def test_shortest_route():
    network = create_sample_network()

    result = find_shortest_route(network, "R1", "R4")

    assert result["reachable"] is True
    assert result["path"] == ["R1", "R2", "R3", "R4"]
    assert result["cost"] == 5


def test_same_source_and_destination():
    network = create_sample_network()

    result = find_shortest_route(network, "R1", "R1")

    assert result["reachable"] is True
    assert result["path"] == ["R1"]
    assert result["cost"] == 0


def test_unreachable_destination():
    network = nx.Graph()
    network.add_edge("R1", "R2", cost=1)
    network.add_node("R3")

    result = find_shortest_route(network, "R1", "R3")

    assert result["reachable"] is False
    assert result["path"] == []
    assert result["cost"] is None


def test_unknown_router():
    network = create_sample_network()

    with pytest.raises(ValueError):
        find_shortest_route(network, "R1", "R99")
