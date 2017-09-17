class NasComponent(object):
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def get_nodes(self):
        return self.nodes


# node address server
from flask import Flask, jsonify, request

app = Flask(__name__)

nasComponent = None


@app.route('/connect', methods=['POST'])
def new_node_connected():
    new_node = request.json['port']
    nasComponent.add_node(new_node)
    return jsonify({'status': 'ok'})


@app.route('/list', methods=['GET'])
def active_node_list():
    nodes = nasComponent.get_nodes()
    return jsonify({'nodes': nodes})


if __name__ == '__main__':
    nasComponent = NasComponent()
    app.run(debug=False, port=5001)
