"""
Node Address Server

Ağa bağlanan node'ların birbirinden haberdar olması için kullanılır.

Ağı başlatmadan önce ayağa kalkmış olması gerekmektedir. 5001 portundan sunulur.
Node.py değiştirilmeden, port bilgisi de değiştirilmemelidir.
"""
from flask import Flask, jsonify, request


class NasComponent(object):
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def get_nodes(self):
        return self.nodes


app = Flask(__name__)
nasComponent = None


@app.route('/connect', methods=['POST'])
def new_node_connected():
    """
    Ağa yeni bir node eklendi!
    """
    try:
        new_node = request.json['port']
        nasComponent.add_node(new_node)
        return jsonify({'status': 'ok'})
    except Exception as exc:
        return jsonify({'message': exc.message})


@app.route('/list', methods=['GET'])
def active_node_list():
    """
    Bir node (kim olduğunun bir önemi yok), ağdaki diğer node'larla haberleşmek için node listesini istiyor!

    :return tüm tree'nin hash'i. Node listesini string array olarak döner.
    """
    try:
        nodes = nasComponent.get_nodes()
        return jsonify({'nodes': nodes})
    except Exception as exc:
        return jsonify({'message': exc.message})


if __name__ == '__main__':
    nasComponent = NasComponent()
    app.run(debug=False, port=5001)
