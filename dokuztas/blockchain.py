import hashlib as hasher

from dokuztas.exceptions import *


class Blockchain:
    def __init__(self):
        self.blocks = []
        self.difficulty = 4
        self.mine_continue = True

    def _generate_genesis(self):
        genesis = Block(id=0, blockhash=0, previous_hash=0, nonce=0, merkleroot=0, data=['genesis'])
        self.blocks.append(genesis)

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
        self.mine_continue = True
        root_hash = self.calculate_merkle(pending_block.pending_txs)
        last_block = self.blocks[len(self.blocks) - 1]
        nonce = 0
        sha = hasher.sha256()
        root_hash_enc = str(root_hash).encode('utf-8')
        prv_hash_enc = str(last_block.previous_hash).encode('utf-8')
        block_id_enc = str(last_block.id).encode('utf-8')
        challenge_string = root_hash_enc + prv_hash_enc + block_id_enc
        sha.update(challenge_string)
        difficulty_indicator = ''.join(["0" for x in range(0, self.difficulty)])
        while self.mine_continue:
            nonce_enc = str(nonce).encode('utf-8')
            sha.update(nonce_enc)

            blockhash = sha.hexdigest()
            if blockhash[0:self.difficulty] == difficulty_indicator:
                # aranan nonce bulundu!
                print('nonce bulundu! nonce: {0} block_hash: {1}'.format(str(nonce), blockhash))
                self.mine_continue = False
                new_id = len(self.blocks)
                block_to_add = Block(id=new_id, blockhash=blockhash,
                                     previous_hash=last_block.blockhash, nonce=nonce,
                                     merkleroot=root_hash, data=pending_block.pending_txs)
                self.blocks.append(block_to_add)

            nonce += 1


class Block:
    def __init__(self, id, blockhash, previous_hash, nonce, merkleroot, data):
        self.id = id
        self.blockhash = blockhash
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkleroot = merkleroot
        self.data = data


class PendingBlock:
    def __init__(self):
        self.pending_txs = []

    def add_txs(self, txs=[]):
        if len(txs) == 0:
            raise PendingTxException()
        self.pending_txs = txs
