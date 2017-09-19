from blockchain import Block, Blockchain
from exceptions import ChainNotCreatedException
import argparse
from flask import Flask, jsonify, request
import requests


class NodeComponent(object):
    def __init__(self):
        self.chain = None

    def create_genesis_chain(self):
        self.chain = Blockchain()

    def load_chain(self, nodes_chains):
        pass

    def get_blocks(self):
        if not self.chain:
            raise ChainNotCreatedException()
        return self.chain.blocks

    def mine(self, new_block):
        pass

    def add(self, new_block):
        pass


app = Flask(__name__)
chain = None


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


def create_genesis_chain():
    global chain
    print('>>> Bilgilendirme: Genesis-time:zero')
    chain = Blockchain()


def pick_honest_chain(node_chains):
    # todo: en uzun ve demokratik seçim sonucu çoğunluktan gelen chain'i seç
    global chain
    chain = Blockchain()
    chain.blocks = node_chains[0]


def load_chain(current_port, nodes=None):
    global chain
    all_blocks = []
    from requests.exceptions import ConnectionError
    import jsonpickle
    for node in nodes:
        try:
            # kendi kendisine chain sormaması için.
            if (node != current_port):
                http_response = requests.get(
                    'http://localhost:{0}/chain'.format(node))
                serialized = http_response.json()['blocks']
                thawed = jsonpickle.decode(serialized)

                all_blocks.append((node, thawed))
        except ConnectionError as con:
            print(
                '>>> Bilgilendirme: {0} porta sahip node, online görünmüyor'.format(node))

    if len(all_blocks) == 0:
        # tüm node'lar kontrol edilmiş fakat yaratılmış bir chain bulunamamışsa, GENESIS gerçekleşir.
        create_genesis_chain()
    else:
        """
        ağa daha önceden bağlanmış ve GENESIS'i oluşturmuş node'lar var demektir.
        Sadece bunların yüklenmesi gerekir
        """
        pick_honest_chain(all_blocks)


@app.route('/chain', methods=['GET'])
def get_chain():
    import jsonpickle
    frozen = jsonpickle.encode(chain.blocks)
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
        create_genesis_chain()
    else:
        """
        bu durumda, ağda başka node'lar var demektir. yani bir blockchain ve genesis block'u çoktan yaratılmıştır.
        ağa 1. olarak dahil olmayan tüm node'lar, giriş anlarında mevcut chain'i ve block'ları yüklemeleri gerekmektedir.
        """
        load_chain(current_port, nodes=nodes)
    run(current_port)


if __name__ == '__main__':
    command_line_runner()
