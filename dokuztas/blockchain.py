import hashlib as hasher

from dokuztas.exceptions import *
from dokuztas._internals import _log


class Blockchain:
    def __init__(self, difficulty=4):
        self.blocks = []
        self.difficulty = difficulty
        self.mine_continue = True

    def _generate_genesis(self):
        """
        Genesis block'u oluşturup, chain'in ilk block'u olarak ekler.
        """
        genesis = Block(id=0, blockhash=0, previous_hash=0, nonce=0, merkleroot=0, data=['genesis'])
        self.blocks.append(genesis)

    def validate(self):
        """
        Chain'deki block'lar değiştirilmiş mi kontrolü yapar. Bunu, her block'un previous_hash değeri, bir önceki block'un
        blockhash'i ile aynı mı diye bakarak yapar.
        """
        blocks_len = len(self.blocks)
        if blocks_len == 0 or blocks_len == 1:
            return True
        for i in range(1, blocks_len):
            if self.blocks[i].previous_hash != self.blocks[i - 1].blockhash:
                return False

        return True

    def calculate_merkle(self, pending_txs):
        """
        Ağa eklenecek transaction'ların merkle root hash'ini hesaplamak için kullanılır. Her bir ikili transaction'un,
        hash'ini alır ve bunları tek bir hash olarak birleştirir. Ve çıkan hash_list'i, tekrar aynı işleme tabi tutmak için
        yine bu metoda parametre olarak geçer. Bu sayede tüm transacation'ların hash'leri, tek bir hash olana kadar
        bu fonksiyon çalıştırılmış olunur.

        Eğer block'a alınacak olan transaction sayısı bir (1) ise, sadece bunun hash'i alınıp geri döndürülür.

        :param pending_txs: Block'a eklenecek olan transaction'lar.
        :return tüm tree'nin hash'i.
        """
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

    def mine(self, pending_block, stop_mining_check, cb_block_found=None):
        """
        Eklenmek istenen block'un merkle root hash'ini alıp,
            * son block'un hash'i,
            * eklenecek olan block'un id'si,
            * ve nonce
        değerini alarak hash'ler ve problemi çözmeye çalışır. Problemi çözdüğünde chain'e block'u ekler ve diğer
        node'ları haberdar eder.

        :param pending_block: Chain'e eklenmek istenen block.
        :param stop_mining_check: Node'un, mining'i durdurabilmesi içindir.
        :param cb_block_found: Block bulunduğunda node'u notify etmesi için bir callback.
        """
        mine_continue = True
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
        while mine_continue and not stop_mining_check():
            # _log('debug', 'Mining iter {0}'.format(str(nonce)))
            nonce_enc = str(nonce).encode('utf-8')
            sha.update(nonce_enc)

            blockhash = sha.hexdigest()
            if blockhash[0:self.difficulty] == difficulty_indicator:
                # aranan nonce bulundu!
                _log('info', 'Nonce bulundu! Nonce: {0} Block_hash: {1}'.format(str(nonce), blockhash))
                mine_continue = False
                new_id = len(self.blocks)
                block_to_add = Block(id=new_id, blockhash=blockhash,
                                     previous_hash=last_block.blockhash, nonce=nonce,
                                     merkleroot=root_hash, data=pending_block.pending_txs)
                self.blocks.append(block_to_add)
                if cb_block_found:
                    cb_block_found()

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
