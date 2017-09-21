import argparse
import requests
from flask import Flask, jsonify

from dokuztas.blockchain import Blockchain, PendingBlock
from dokuztas.exceptions import *


class NodeComponent(object):
    def __init__(self, miner=False):
        self.chain = None
        self.miner = miner
        self.pending_txs = []
        self.pending_blocks = []

    def create_genesis_chain(self):
        print(">>> GENESIS")
        self.chain = Blockchain()

    def pick_honest_chain(self, node_chains):
        # consensus
        # todo: en uzun ve demokratik seçim sonucu çoğunluktan gelen chain'i seç
        print(">>> LOADED: Blocks")
        self.chain = Blockchain()
        self.chain.blocks = node_chains[0]

    def load_chain(self, nodes_chains):
        print(str(nodes_chains))
        if len(nodes_chains) == 0:
            # tüm node'lar kontrol edilmiş fakat yaratılmış bir chain bulunamamışsa, GENESIS gerçekleşir.
            self.create_genesis_chain()
        else:
            """
            ağa daha önceden bağlanmış ve GENESIS'i oluşturmuş node'lar var demektir.
            Sadece bunların yüklenmesi gerekir
            """
            self.pick_honest_chain(nodes_chains)

    def get_blocks(self):
        if not self.chain:
            raise ChainNotCreatedException()
        return self.chain.blocks

    def mine(self):
        if not self.miner:
            raise MinerException()

        if self.pending_blocks > 0:
            self.chain.mine(self.pending_blocks[0])

    def block_added(self, new_block):
        """
        bu fonksiyon çağırıldığında diğer node'lardan biri block'u eklemiş demektir,
        devam etmekte olan mine işlemi sonlandırılır
        :param new_block:
        :return:
        """

        pass

    def add_transaction(self, tx):
        """
        node'lar tarafından eklenen tx'ler içindir.

        mine işlemini, tx sayısı 10'a ulaştığında bir kez tetikler. sonrasında mine bir döngü
        :param tx:
        :return:
        """
        self.pending_txs.append(tx)

        if len(self.pending_txs) > 10:
            p_block = PendingBlock()
            p_block.add_txs(self.pending_txs)
            self.pending_blocks.append(p_block)
            self.pending_txs = []

            if len(self.pending_blocks) == 1 and self.miner:
                self.mine()


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
        print('>>> Bilgilendirme: Blockchain ağına bağlanıldı.')
    else:
        print('>>> Hata: {0}'.format(http_response.json()['message']))


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
            print(
                '>>> Bilgilendirme: {0} porta sahip node offline olabilir'.format(node))

    active_node.load_chain(all_blocks)


@app.route('/chain', methods=['GET'])
def get_chain():
    frozen = None
    try:
        import jsonpickle
        frozen = jsonpickle.encode(active_node.chain.blocks)
    except Exception as exc:
        print(">>> HATA /chain: {0}".format(str(exc)))
    return jsonify({'blocks': frozen})


@app.route('/mine', methods=['GET'])
def new_block_added_triggered():
    # yeni eklenen block'un problemini çözmeye çalış
    return jsonify({'status': 'ok'})


@app.route('/add', methods=['POST'])
def add_new_block():
    # tx'i alıp blockchain'e ver. o da block yaratsın.
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
        """
        mevcut node sayısı 1 ise, ilk node network'e bağlanmıştır. 
        bu durumda chain'in ilk kez yaratılması gerekir, doğal olarak da genesis'in.
        """
        active_node.create_genesis_chain()
    else:
        """
        bu durumda, ağda başka node'lar var demektir. yani bir blockchain ve genesis block'u çoktan yaratılmıştır.
        ağa 1. olarak dahil olmayan tüm node'lar, giriş anlarında mevcut chain'i ve block'ları yüklemeleri gerekmektedir.
        """
        load_chain(current_port, nodes=nodes)
    run(current_port)


if __name__ == '__main__':
    command_line_runner()
