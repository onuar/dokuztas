from dokuztas.blockchain import Blockchain, Block, PendingBlock


def test_when_blockchain_is_created_first_time_then_first_block_should_be_genesis_block():
    chain = Blockchain()
    assert len(chain.blocks) == 1
    assert chain.blocks[0].id == 0


def test_when_genesis_block_is_added_then_genesis_block_id_should_be_assigned_zero():
    chain = Blockchain()
    assert chain.blocks[0].id == 0


def test_genesis_block_s_previous_block_hash_should_be_assigned_zero():
    chain = Blockchain()
    assert chain.blocks[0].previous_hash == 0


def test_blocks_ids_should_increase_one_by_one():
    chain = Blockchain()
    block_id_one = Block()
    block_id_two = Block()
    chain.add_block(block_id_one)
    chain.add_block(block_id_two)
    assert block_id_one.id == 1
    assert block_id_two.id == 2


def test_each_block_s_previous_hash_property_should_be_previous_block_s_hash():
    chain = Blockchain()
    block_id_zero = Block()
    block_id_one = Block()
    block_id_two = Block()
    chain.add_block(block_id_zero)
    chain.add_block(block_id_one)
    chain.add_block(block_id_two)
    assert block_id_one.previous_hash == block_id_zero.hash
    assert block_id_two.previous_hash == block_id_one.hash


def test_if_the_blocks_are_not_changed_then_chain_should_be_a_valid_chain():
    chain = Blockchain()
    block_id_zero = Block()
    block_id_one = Block()
    block_id_two = Block()

    chain.add_block(block_id_zero)
    first_validation = chain.validate()
    assert first_validation == True

    chain.add_block(block_id_one)
    second_validation = chain.validate()
    assert second_validation == True

    chain.add_block(block_id_two)
    third_validation = chain.validate()
    assert third_validation == True


def test_if_a_block_is_changed_then_chain_should_not_be_a_valid_chain():
    chain = Blockchain()
    block_id_zero = Block()
    block_id_one = Block()
    block_id_two = Block()

    chain.add_block(block_id_zero)
    chain.add_block(block_id_one)
    chain.add_block(block_id_two)

    block_id_one.data = {'hacked'}
    block_id_one.calculate_hash()

    validation = chain.validate()
    assert validation == False


def test_if_there_is_just_one_tx_to_mine_then_its_hash_should_be_merkle_hash():
    chain = Blockchain()
    odd_hash = chain.calculate_merkle(['I shot the sheriff'])
    assert odd_hash == 'f1254d09500291eb72966b263da07df061426fe6391873b640128bcf8abcf897'


def test_if_pending_tx_count_is_odd_number_then_merkle_root_should_be_one_hash():
    chain = Blockchain()
    pending_txs = ['a', 'b', 'c', 'd', 'f']
    root_hash = chain.calculate_merkle(pending_txs=pending_txs)
    assert root_hash == 'dab4b3dd381a192214ffe6dfb8481f741be76e171dc298db75a44eb4df6d4213'


def test_if_pending_tx_count_is_even_number_then_merkle_root_should_be_one_hash():
    chain = Blockchain()
    pending_txs = ['a', 'b', 'c', 'd', 'f', 'g']
    root_hash = chain.calculate_merkle(pending_txs=pending_txs)
    assert root_hash == '1adc308023cbce02e0d90cc31b096ea2a847548b966adc4c18d3f2ae654bfcb3'


def test_mine_tester():
    chain = Blockchain()
    chain._generate_genesis()
    p = PendingBlock()
    p.add_txs(['a', 'b', 'c', 'd', 'f'])
    chain.mine(p)
