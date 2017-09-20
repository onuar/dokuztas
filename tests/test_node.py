from dokuztas.node import NodeComponent


def test_max_pending_txs_count_should_be_2400():
    node = NodeComponent()
    for x in range(0, 2400):
        node.add_transaction(x)

    assert len(node.pending_txs) == 2400


def test_after_each_2400_txs_pending_txs_count_should_be_zero():
    node = NodeComponent()
    for x in range(0, 2401):
        node.add_transaction(x)

    assert len(node.pending_txs) == 0


def test_every_2400_txs_should_be_packed_in_pending_block_object():
    node = NodeComponent()
    for x in range(0, 4802):
        node.add_transaction(x)

    assert len(node.pending_txs) == 0
    assert len(node.pending_blocks) == 2
