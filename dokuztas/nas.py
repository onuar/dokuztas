# node address server
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
    try:
        new_node = request.json['port']
        nasComponent.add_node(new_node)
        return jsonify({'status': 'ok'})
    except Exception as exc:
        return jsonify({'message': exc.message})


@app.route('/list', methods=['GET'])
def active_node_list():
    try:
        nodes = nasComponent.get_nodes()
        return jsonify({'nodes': nodes})
    except Exception as exc:
        return jsonify({'message': exc.message})


if __name__ == '__main__':
    nasComponent = NasComponent()
    app.run(debug=False, port=5001)
