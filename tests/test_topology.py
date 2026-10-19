
from network.topology import (
    create_star_topology,
    create_ring_topology,
    create_mesh_topology,
)


def test_star_topology():
    network = create_star_topology(5)
    assert network.number_of_nodes() == 5
    assert network.number_of_edges() == 4
    assert network.degree("R1") == 4


def test_ring_topology():
    network = create_ring_topology(5)
    assert network.number_of_nodes() == 5
    assert network.number_of_edges() == 5
    assert all(degree == 2 for _, degree in network.degree())


def test_mesh_topology():
    network = create_mesh_topology(5)
    assert network.number_of_nodes() == 5
    assert network.number_of_edges() == 10
    assert all(degree == 4 for _, degree in network.degree())
