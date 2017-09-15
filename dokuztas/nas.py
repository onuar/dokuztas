# node address server
from flask import Flask, jsonify, request

app = Flask(__name__)

nodes = []


@app.route('/connect', methods=['POST'])
def new_node_connected():
    new_node = request.json['port']
    if new_node not in nodes:
        nodes.append(new_node)
    return jsonify({'status': 'ok'})


@app.route('/list', methods=['GET'])
def active_node_list():
    return jsonify({'nodes': nodes})


if __name__ == '__main__':
    app.run(debug=False, port=5001)
