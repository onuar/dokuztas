import argparse
import requests
from flask import Flask, jsonify

from dokuztas.blockchain import Blockchain, PendingBlock
from dokuztas.exceptions import *
from dokuztas._internals import _log, MiningThread


class NodeComponent(object):
    def __init__(self, miner=False):
        self.chain = None
        self.stop_mining = False
        self.miner = miner
        self.pending_txs = []
        self.pending_blocks = []

    def create_genesis_chain(self):
        """Genesis block yaratır."""
        _log('info', 'Genesis! Blockchain ilk kez oluşturuldu.')
        self.chain = Blockchain()
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
        self.chain = Blockchain()
        self.chain.blocks = node_chains[0]

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
        if not self.miner:
            raise MinerException()

    def terminate_mining(self):
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

    def mine(self):
        """
        Mine işleminin başlatıldığı yerdir. Bu işlemin blockchain objesi tarafından yönetilmemesinin sebebi,
        ilerde node'ların, transaction fee'ye göre mine etme veya mine etmek istedikleri block'ları kendilerinin
        seçebilmesi gibi özellikleri olabilmesi ihtimalidir. Şu an için roadmap'te böyle bir özellik bulunmamaktadır.
        """
        th_mine = None
        self.miner_check()
        self.stop_mining = False

        def block_found():
            _log('dev', 'Block found called')
            th_mine.stop()

        if len(self.pending_blocks) > 0:
            th_mine = MiningThread(mine_target=self.chain.mine,
                                   args=(self.pending_blocks[0],
                                         self.terminate_mining,
                                         block_found))
            th_mine.start()

    def block_added(self, new_block):
        """
        Diğer node'lardan biri, mining sonucu block eklediğinde, node'un sync kalması için çağırılır.
        Devam etmekte olan bir mine işlemi varsa, sonlandırılır.

        :param new_block: Yeni eklenen block.
        """
        self.miner_check()

        self.stop_mining = True
        self.pending_blocks.remove(self.pending_blocks[0])

        self.chain.blocks.append(new_block)


app = Flask(__name__)
active_node = None


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
        except ConnectionError as con:
            _log('info', '{0} porta sahip node offline olabilir'.format(node))

    active_node.load_chain(all_blocks)


@app.route('/chain', methods=['GET'])
def get_chain():
    frozen = None
    try:
        import jsonpickle
        frozen = jsonpickle.encode(active_node.chain.blocks)
    except Exception as exc:
        _log('error', '/chain: {0}'.format(str(exc)))
    return jsonify({'blocks': frozen})


@app.route('/mine', methods=['GET'])
def new_block_added_triggered():
    # todo: yeni eklenen block'un problemini çözmeye çalış
    return jsonify({'status': 'ok'})


@app.route('/add', methods=['POST'])
def add_new_block():
    # todo: tx'i alıp blockchain'e ver. o da block yaratsın.
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
    global active_node
    active_node = NodeComponent()

    parser = get_parser()
    args = parser.parse_args()
    current_port = args.port

    if not current_port:
        current_port = 5000
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
    run(current_port)


if __name__ == '__main__':
    command_line_runner()
