from dokuztas.nas import NasComponent

def test_when_new_node_is_connected_then_it_should_be_added():
    nas = NasComponent()
    nas.add_node('5002')
    nodes = nas.get_nodes()
    assert '5002' in nodes

def test_if_connecting_node_exist_then_it_should_not_be_added_twice():
    nas = NasComponent()
    nas.add_node('5002')
    nas.add_node('5002')
    nodes = nas.get_nodes()
    assert len(nodes) == 1