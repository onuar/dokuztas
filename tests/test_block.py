from dokuztas.blockchain import Block


def test_block_data_should_be_dict():
    data = {'name': 'Onur', 'surname': 'Aykaç'}
    block = Block(data=data)
    assert isinstance(block.data, dict)


def test_block_hash_should_be_created_by_id_prvhash_and_nonce():
    block = Block()
    block.id = 100
    block.previous_hash = 100
    block.data = {'name': 'Onur', 'surname': 'Aykaç'}
    block.nonce = 100
    block.calculate_hash()
    assert block.hash == "1477b8d1c6b66c77015684ecaae6b23d6373bcab23d067f3926cf8cdd6761b07"