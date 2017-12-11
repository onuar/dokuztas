from dokuztas.node import NodeComponent
from dokuztas.exceptions import *

import pytest
from unittest.mock import patch


def fake_mined_node_patcher(txs_count):
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


def async_mined_node_patcher(txs_count, difficulty=4):
    def node_decorator(func):
        def func_wrapper():
            from dokuztas.blockchain import Blockchain
            node = NodeComponent()
            node.chain = Blockchain(difficulty=difficulty)
            node.miner = True
            node.create_genesis_chain()
            for x in range(0, txs_count):
                node.add_transaction(str(x))
            func(node)

        return func_wrapper

    return node_decorator


@fake_mined_node_patcher(10)
def test_max_pending_txs_count_should_be_10(node):
    assert len(node.pending_txs) == 10


@fake_mined_node_patcher(11)
def test_after_each_10_txs_pending_txs_count_should_be_zero(node):
    assert len(node.pending_txs) == 0


@fake_mined_node_patcher(22)
def test_every_10_txs_should_be_packed_in_pending_block_object(node):
    assert len(node.pending_txs) == 0
    assert len(node.pending_blocks) == 2


@fake_mined_node_patcher(11)
def test_pending_blocks_should_be_typed_with_pendingblock_object(node):
    from dokuztas.blockchain import PendingBlock
    assert isinstance(node.pending_blocks[0], PendingBlock)


def test_if_node_is_not_a_miner_then_mine_function_should_throw_minerexception():
    node = NodeComponent(miner=False)
    node.create_genesis_chain()
    with pytest.raises(MinerException):
        node.mine()


def test_if_first_pendingblock_is_just_created_then_mining_should_be_started_once():
    node = NodeComponent(miner=True)
    node.create_genesis_chain()
    patcher = patch('dokuztas.node.NodeComponent.mine')
    mock = patcher.start()
    for x in range(0, 200):
        node.add_transaction(x)
    patcher.stop()
    mock.assert_called_once_with()


def test_for_mining_it_should_be_start_new_thread():
    from dokuztas.blockchain import Blockchain, PendingBlock
    patcher = patch('dokuztas._internals.MiningThread.start')
    mock = patcher.start()
    node = NodeComponent(miner=True)
    node.chain = Blockchain(difficulty=1)
    node.chain._generate_genesis()
    pending_block = PendingBlock()
    pending_block.add_txs(['a', 'b', 'c'])
    node.pending_blocks.append(pending_block)
    node.mine()
    patcher.stop()
    assert mock.called


def test_if_correct_hash_is_found_then_block_found_function_should_be_called_once():
    from dokuztas.blockchain import Blockchain, PendingBlock
    patcher = patch('dokuztas.node.NodeComponent.block_found')
    mock = patcher.start()
    node = NodeComponent(miner=True)
    node.chain = Blockchain(difficulty=4)
    node.chain._generate_genesis()
    pending_block = PendingBlock()
    pending_block.add_txs(['a', 'b', 'c'])
    node.pending_blocks.append(pending_block)

    def sync_runner():
        def always_mine():
            return False

        node.chain.mine(node.pending_blocks[0],
                        always_mine,
                        mock)

    mine_patcher = patch('dokuztas.node.NodeComponent.mine', side_effect=sync_runner)
    mine_patcher.start()
    node.mine()
    patcher.stop()
    mine_patcher.stop()
    assert mock.called


def test_any_other_node_found_correct_hash_then_mining_should_be_stopped():
    from dokuztas.blockchain import Blockchain, PendingBlock, Block
    node = NodeComponent(miner=True)
    node.chain = Blockchain(difficulty=10)

    def adds_genesis():
        genesis = Block(id=0, blockhash=0, previous_hash=0, nonce=0, merkleroot=0, data=['genesis'])
        node.chain.blocks.append(genesis)

    genesis_patcher = patch('dokuztas.node.NodeComponent.create_genesis_chain', side_effect=adds_genesis)
    genesis_patcher.start()
    node.create_genesis_chain()
    genesis_patcher.stop()

    pending_block = PendingBlock()
    pending_block.add_txs(['a', 'b', 'c'])
    node.pending_blocks.append(pending_block)
    node.mine()
    block_to_add = Block(id=123, previous_hash=0, nonce=123, merkleroot=123, blockhash=111, data=['a', 'b', 'c'])
    node.block_added(block_to_add)
    assert node.chain.blocks[1].blockhash == 111
    assert len(node.chain.blocks) == 2


def test_after_first_block_is_mined_then_pending_txs_should_be_mined():
    from dokuztas.blockchain import Blockchain
    node = NodeComponent()
    node.miner = True
    node.chain = Blockchain(difficulty=1)
    node.chain._generate_genesis()

    def sync_mine(**kwargs):
        node.chain.mine(kwargs['args'][0],
                        kwargs['args'][1],
                        kwargs['args'][2])

    thread_patcher = patch('dokuztas.node.NodeComponent._internal_mine', side_effect=sync_mine)
    thread_patcher.start()
    for x in range(0, 22):
        node.add_transaction(str(x))
    thread_patcher.stop()
    assert len(node.chain.blocks) == 3


@async_mined_node_patcher(txs_count=12, difficulty=10)
def test_while_mining_new_txs_can_be_adding(node):
    from dokuztas.blockchain import Block
    assert len(node.pending_txs) == 1

    # Mevcut mining'i durdurmak için.
    block_to_add = Block(id=123, previous_hash=0, nonce=123, merkleroot=123, blockhash=111, data=['a', 'b', 'c'])
    node.block_added(block_to_add)

    # todo: test_if_one_block__mining_is_finised_then_other_transactions_should_get_in_a_block()
