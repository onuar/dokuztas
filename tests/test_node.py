from dokuztas.node import NodeComponent
from dokuztas.exceptions import *

import pytest
from unittest.mock import patch


def mined_node_patcher(txs_count):
    def node_decorator(func):
        def func_wrapper():
            patcher = patch('dokuztas.node.NodeComponent.mine')
            patcher.start()
            node = NodeComponent()
            node.miner = True
            node.create_genesis_chain()
            for x in range(0, txs_count):
                node.add_transaction(str(x))
            patcher.stop()
            func(node)

        return func_wrapper

    return node_decorator


@mined_node_patcher(10)
def test_max_pending_txs_count_should_be_10(node):
    assert len(node.pending_txs) == 10


@mined_node_patcher(11)
def test_after_each_10_txs_pending_txs_count_should_be_zero(node):
    assert len(node.pending_txs) == 0


@mined_node_patcher(22)
def test_every_10_txs_should_be_packed_in_pending_block_object(node):
    assert len(node.pending_txs) == 0
    assert len(node.pending_blocks) == 2


@mined_node_patcher(11)
def test_pending_blocks_should_be_typed_with_pendingblock_object(node):
    from dokuztas.blockchain import PendingBlock
    assert isinstance(node.pending_blocks[0], PendingBlock)


def test_if_node_is_not_a_miner_then_mine_function_should_throw_minerexception():
    node = NodeComponent(miner=False)
    node.create_genesis_chain()
    with pytest.raises(MinerException):
        node.mine()


def test_if_first_pendingblock_is_just_created_then_mineing_should_be_started_once():
    patcher = patch('dokuztas.node.NodeComponent.mine')
    mock = patcher.start()
    node = NodeComponent(miner=True)
    node.create_genesis_chain()
    for x in range(0, 200):
        node.add_transaction(x)
    patcher.stop()
    mock.assert_called_once()
