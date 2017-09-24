import argparse
import requests
from flask import Flask, jsonify, request

from dokuztas.blockchain import Blockchain, PendingBlock
from dokuztas.exceptions import *
from dokuztas._internals import _log, MiningThread


class NodeComponent(object):
    def __init__(self, miner=False, cb_notify_nodes=None, difficulty=4):
        self.chain = None
        self.stop_mining = False
        self.difficulty = difficulty
        self.cb_notify_nodes = cb_notify_nodes
        self.miner = miner
        self.pending_txs = []
        self.pending_blocks = []

    def create_genesis_chain(self):
        """Genesis block yaratır."""
        _log('info', 'Genesis! Blockchain ilk kez oluşturuldu.')
        self.chain = Blockchain(difficulty=self.difficulty)
        self.chain._generate_genesis()

    def pick_honest_chain(self, node_chains):
        """
        Genesis block'un yaratıldığı bir ağa bağlanan node için çalıştırılır.
        Node, consensus sonucu, değiştirilmemiş block'u bulmaya çalışır.

        v0.0.1 itibari ile, sadece ilk node'dan gelen block'u doğru kabul edip almaktadır.
        İlerki versiyonlarda değiştirilecektir. Roadmap'e eklenmiş durumda.

        :param node_chains: Ağdaki tüm ağlardan alınan block'lar.
        """
        _log('info', 'Ağdaki block\'lar toplanılarak, consensus sonrası en uygun block seçildi')
        self.chain = Blockchain(difficulty=self.difficulty)
        self.chain.blocks = node_chains[0][1]

    def load_chain(self, nodes_chains):
        """
        Ağdan gelen block'lara bakarak, genesis block mu yaratılacak, consensus sonucu en uygun chain mi seçilecek kararını verir.

        :param nodes_chains: Ağdaki tüm ağlardan alınan block'lar.
        """
        if len(nodes_chains) == 0:
            self.create_genesis_chain()
        else:
            self.pick_honest_chain(nodes_chains)

    def get_blocks(self):
        if not self.chain:
            raise ChainNotCreatedException()
        return self.chain.blocks

    def miner_check(self):
        # aktif node bir miner mı kontrolü yapar. Değilse MinerException fırlatır.
        if not self.miner:
            raise MinerException()

    def terminate_mining(self):
        """
        Blockchain.mine metoduna parametre olarak geçilir ve Blockchain.mine metodu nonce'u ararken, her iterasyonda bu metodu çağırır.
        Burada amaç, NodeComponent üzerinden, Blockchain üzerinde çalışan mining thread'ini durdurabilmektir. self.stop_mining = True olduğunda,
        Blockchain.mine duracaktır. Bu durum sadece, başka bir miner'ın problemi, aktif node'dan önce çözmesi durumunda oluşur. Aktif node'un
        üzerinde çalıştığı block'u bırakarak, yeni block'a geçmesini sağlar.
        """
        return self.stop_mining

    def add_transaction(self, tx):
        """
        Mine edilmesi için yeni bir transaction ekemek içindir.
        Her bekleyen transaction'ı, bir (1) block'a çevirir ve bu şekilde bekletir.

        Mine işlemini, tx sayısı 10'a ulaştığında bir kez tetikler. Sonrasında mine bir döngü şeklinde çalışmaya devam eder.

        :param tx: Mine edilesi için eklenen transaction.
        """
        self.miner_check()

        self.pending_txs.append(tx)

        if len(self.pending_txs) > 10:
            p_block = PendingBlock()
            p_block.add_txs(self.pending_txs)
            self.pending_blocks.append(p_block)
            self.pending_txs = []

            if len(self.pending_blocks) == 1:
                self.mine()

    def block_found(self):
        """
        Çalışan node block'u bulmuşsa, blockchain objesi tarafından bu metod çağırılır.
        """
        _log('dev', 'NodeComponent.mine.block_found')
        if len(self.pending_blocks) > 0:
            self.pending_blocks.remove(self.pending_blocks[0])
        elif len(self.pending_txs) > 0:
            self.pending_txs = []
        self.mine()

        if self.cb_notify_nodes:
            self.cb_notify_nodes(self.chain.blocks[len(self.chain.blocks) - 1])

    def _internal_mine(self, args=()):
        """
        Normal şartlar altında mine işlemi ayrı bir thread içersinde çalışmalıdır. Bu metod da bunu sağlamaktadır.
        Bu işlemin NodeComponent.mine metodu içersinde yapılmamasının tek sebebi, dışardan mock'lama ihtiyacının oluşmasıdır.
        Unit test'lerde kimi zaman senkronize mining yapılması gerekebiliyor.

        :param args: Her zaman Blockchain.mine metodu ile aynı olmalıdır.
        """
        th_mine = MiningThread(mine_target=self.chain.mine,
                               args=args)
        th_mine.start()

    def mine(self):
        """
        Mine işleminin başlatıldığı yerdir. Bu işlemin blockchain objesi tarafından yönetilmemesinin sebebi,
        ilerde node'ların, transaction fee'ye göre mine etme veya mine etmek istedikleri block'ları kendilerinin
        seçebilmesi gibi özellikleri olabilmesi ihtimalidir. Şu an için roadmap'te böyle bir özellik bulunmamaktadır.
        """
        self.miner_check()

        if len(self.pending_blocks) > 0:
            self.stop_mining = False
            self._internal_mine(args=(self.pending_blocks[0],
                                      self.terminate_mining,
                                      self.block_found))
        elif len(self.pending_txs) > 0:
            self.stop_mining = False
            temp_block = PendingBlock()
            temp_block.add_txs(self.pending_txs)
            self.pending_txs = []
            self._internal_mine(args=(temp_block,
                                      self.terminate_mining,
                                      self.block_found))

    def block_added(self, new_block):
        """
        Diğer node'lardan biri, mining sonucu block eklediğinde, aktif node'un sync kalması için çağırılır.
        Devam etmekte olan bir mine işlemi varsa, sonlandırılır.

        :param new_block: Yeni eklenen block.
        """
        _log('debug', 'node.NodeComponent.block_added')
        self.chain.blocks.append(new_block)
        if self.miner:
            self.stop_mining = True
            # Normal şartlar altında bu if bloguna ihtiyaç olmaması gerekiyor.
            # HTTP çalıştığımız için ve queue olmadığı için, diğer miner'lardan birisi
            # iki kez üst üste problemi çözerse, IndexError: list index out of range
            # oluşuyor.
            if len(self.pending_blocks) > 0:
                self.pending_blocks.remove(self.pending_blocks[0])
            self.mine()


app = Flask(__name__)
active_node = None
curr_port = None


def get_other_nodes():
    http_response = requests.get(
        'http://localhost:5001/list')
    response = http_response.json()
    nodes = response["nodes"]
    return nodes


def connect_to_network(port):
    data = {'port': port}
    http_response = requests.post(
        'http://localhost:5001/connect', json=data)
    if http_response.status_code == 200:
        _log('info', 'Blockchain ağına bağlanıldı.')
    else:
        _log('error', 'Ağa bağlanırken hata ile karşılaşıldı: {0}'.format(http_response.json()['message']))


def broadcast_nodes(cb_iter, cb_error, nodes=None):
    if not nodes:
        nodes = get_other_nodes()

    for node in nodes:
        if node != curr_port:
            try:
                cb_iter(node)
            except Exception as exc:
                cb_error(exc, node)


def load_chain(current_port, nodes=None):
    all_blocks = []
    from requests.exceptions import ConnectionError
    import jsonpickle
    for node in nodes:
        try:
            # kendi kendisine chain sormaması için.
            if node != current_port:
                http_response = requests.get(
                    'http://localhost:{0}/chain'.format(node))
                serialized = http_response.json()['blocks']
                thawed = jsonpickle.decode(serialized)

                all_blocks.append((node, thawed))
        except ConnectionError as conerr:
            _log('info', '{0} porta sahip node offline olabilir'.format(node))

    active_node.load_chain(all_blocks)


def notify_nodes(last_block):
    nodes = get_other_nodes()
    for node in nodes:
        try:
            import jsonpickle
            if node != curr_port:
                frozen = jsonpickle.encode(last_block)
                data = {'block': frozen}
                requests.post(
                    'http://localhost:{0}/found'.format(node), json=data)
        except ConnectionError as conerr:
            _log('info', '{0} porta sahip node offline olabilir'.format(node))


@app.route('/found', methods=['POST'])
def block_added():
    import jsonpickle
    serialized = request.json['block']
    thawed = jsonpickle.decode(serialized)
    active_node.block_added(thawed)
    _log('debug', 'Başka bir miner block problemini çözdü. Çözülen block, chain\'e eklendi.')
    return jsonify({'status': 'ok'})


@app.route('/chain', methods=['GET'])
def get_chain():
    frozen = None
    try:
        import jsonpickle
        frozen = jsonpickle.encode(active_node.chain.blocks)
    except Exception as exc:
        _log('error', '/chain: {0}'.format(str(exc)))
    return jsonify({'blocks': frozen})


@app.route('/added', methods=['POST'])
def added_transaction():
    data = request.json["tx"]
    active_node.add_transaction(data)
    return jsonify({'status': 'ok'})


@app.route('/add', methods=['POST'])
def add_transaction():
    data = request.json["tx"]
    if active_node.miner:
        active_node.add_transaction(data)

    def send_tx(node):
        req_data = {'tx': request.json["tx"]}
        requests.post(
            'http://localhost:{0}/added'.format(node), json=req_data)

    def exc_occurs(exc, node):
        if exc is ConnectionError:
            _log('info', '{0} porta sahip node offline olabilir'.format(node))

    broadcast_nodes(cb_iter=send_tx, cb_error=exc_occurs)
    return jsonify({'status': 'ok'})


def run(node_port):
    app.run(debug=False, port=node_port)


def get_parser():
    parser = argparse.ArgumentParser(
        description='Blockchain')
    parser.add_argument('-p', '--port',
                        help='node\'un port\'unu belirtir.', type=int)
    parser.add_argument('-m', '--miner',
                        help='node\'un mine işlemi yapıp yapmayacağını belirtir. 0 ya da 1 olmalıdır.', type=int)

    return parser


def command_line_runner():
    parser = get_parser()
    args = parser.parse_args()
    current_port = args.port

    global active_node
    active_node = NodeComponent(miner=args.miner, cb_notify_nodes=notify_nodes, difficulty=5)

    if not current_port:
        current_port = 5000

    global curr_port
    curr_port = current_port
    connect_to_network(current_port)

    nodes = get_other_nodes()
    if len(nodes) == 1:
        # mevcut node sayısı 1 ise, ilk node network'e bağlanmıştır.
        # bu durumda chain'in ilk kez yaratılması gerekir, doğal olarak da genesis'in.
        active_node.create_genesis_chain()
    else:
        # bu durumda, ağda başka node'lar var demektir. yani bir blockchain ve genesis block'u çoktan yaratılmıştır.
        # ağa 1. olarak dahil olmayan tüm node'lar, giriş anlarında mevcut chain'i ve block'ları
        # yüklemeleri gerekmektedir.
        load_chain(current_port, nodes=nodes)

    # todo: ağa yeni dahil olan node bir miner ise, önceden ağa girmiş olan node'lardan,
    # bekleyen block'ları ve tx'leri alması gerekiyor ve hemen mining'e başlaması gerekiyor.

    run(current_port)


if __name__ == '__main__':
    command_line_runner()
