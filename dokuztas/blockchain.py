class Blockchain():
    def __init__(self):
        self.blocks = []
        self._generate_genesis()

    def _generate_genesis(self):
        genesis = Block()
        genesis.previous_hash = 0
        genesis.id = 0
        genesis.data = {'info': 'ilk block'}
        genesis.calculate_hash()
        self.blocks.append(genesis)

    def get_all_blocks(self):
        return self.blocks

    def add_block(self, block):
        blocks_len = len(self.blocks)
        block.id = blocks_len
        block.previous_hash = self.blocks[blocks_len - 1].hash
        block.calculate_hash()
        self.blocks.append(block)

    def validate(self):
        blocks_len = len(self.blocks)
        if blocks_len == 0 or blocks_len == 1:
            return True
        for i in range(1, blocks_len):
            if self.blocks[i].previous_hash != self.blocks[i - 1].hash:
                return False

        return True


import hashlib as hasher


class Block():
    def __init__(self, data=None):
        self.id = None
        self.previous_hash = None
        self.data = data
        self.hash = None

    def calculate_hash(self):
        sha = hasher.sha256()
        id_enc = str(self.id).encode('utf-8')
        data_enc = str(self.data).encode('utf-8')
        prv_hash_enc = str(self.previous_hash).encode('utf-8')
        sha.update(id_enc + data_enc + prv_hash_enc)
        self.hash = sha.hexdigest()
