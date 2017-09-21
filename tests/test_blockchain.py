from dokuztas.blockchain import Blockchain, Block, PendingBlock


def mined_chain_patcher():
    def chain_decorator(func):
        def func_wrapper():
            chain = Blockchain()
            chain._generate_genesis()
            p = PendingBlock()
            p.add_txs(['a', 'b', 'c', 'd', 'f'])
            chain.mine(p)

            p2 = PendingBlock()
            p2.add_txs(['y', 'z'])
            chain.mine(p2)

            func(chain)

        return func_wrapper

    return chain_decorator


def test_when_blockchain_is_created_first_time_then_first_block_should_be_genesis_block():
    chain = Blockchain()
    chain._generate_genesis()
    assert len(chain.blocks) == 1
    assert chain.blocks[0].id == 0


def test_when_genesis_block_is_added_then_genesis_block_id_should_be_assigned_zero():
    chain = Blockchain()
    chain._generate_genesis()
    assert chain.blocks[0].id == 0


def test_genesis_block_s_previous_block_hash_should_be_assigned_zero():
    chain = Blockchain()
    chain._generate_genesis()
    assert chain.blocks[0].previous_hash == 0


@mined_chain_patcher()
def test_blocks_ids_should_increase_one_by_one(chain):
    assert chain.blocks[0].id == 0
    assert chain.blocks[1].id == 1


@mined_chain_patcher()
def test_each_block_s_previous_hash_property_should_be_previous_block_s_hash(chain):
    assert chain.blocks[0].blockhash == chain.blocks[1].previous_hash
    assert chain.blocks[1].blockhash == chain.blocks[2].previous_hash


@mined_chain_patcher()
def test_if_the_blocks_are_not_changed_then_chain_should_be_a_valid_chain(chain):
    assert chain.validate() == True


@mined_chain_patcher()
def test_if_a_block_is_changed_then_chain_should_not_be_a_valid_chain(chain):
    chain.blocks[1].blockhash = 'f061426fe6391873b640128bcf8abcf897f1254d09500291eb72966b263da07d'
    assert chain.validate() == False


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
    assert chain.blocks[1].nonce == 13106
    assert chain.blocks[1].blockhash == '00005df8b04cb42e62c5be0766af2caa884dd52b51b7ff1549aab3c77e88b84d'
