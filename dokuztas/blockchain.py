import hashlib as hasher

from dokuztas.exceptions import *


class Blockchain:
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

    def calculate_merkle(self, pending_txs):
        hash_list = []
        if len(pending_txs) % 2 == 1:
            odd_tx = pending_txs[len(pending_txs) - 1].encode('utf-8')
            odd_sha = hasher.sha256(odd_tx)
            odd_hash = odd_sha.hexdigest()
            pending_txs.remove(pending_txs[len(pending_txs) - 1])
            hash_list.append(odd_hash)

        if len(pending_txs) == 0:
            return hash_list[0]

        for i in range(0, len(pending_txs), 2):
            tx_1_hash = hasher.sha256(pending_txs[i].encode('utf-8')).hexdigest()
            tx_2_hash = hasher.sha256(pending_txs[i + 1].encode('utf-8')).hexdigest()
            sha = hasher.sha256()
            sha.update(tx_1_hash.encode('utf-8'))
            sha.update(tx_2_hash.encode('utf-8'))
            upper_hash = sha.hexdigest()
            hash_list.append(upper_hash)

        result = self.calculate_merkle(hash_list)
        if isinstance(result, str):
            return result

    def mine(self, pending_block):
        merkle_hash = self.calculate_merkle(pending_block.pending_txs)


class Block:
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


class PendingBlock:
    def __init__(self):
        self.pending_txs = []

    def add_txs(self, txs=[]):
        if len(txs) == 0:
            raise PendingTxException()
        self.pending_txs = txs
