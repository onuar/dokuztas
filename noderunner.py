from unittest.mock import patch

from dokuztas.node import command_line_runner


class FakeParser(object):
    def __init__(self, arg_port):
        self.argport = arg_port

    def parse_args(self):
        return self.get_fake_args(self.argport)

    def get_fake_args(self, port):
        class FakeArgs(object):
            def __init__(self, inner_port):
                self.port = inner_port

        return FakeArgs(port)


#
# import threading
# import time
# patcher = patch('dokuztas.node.get_parser')
# mock = patcher.start()
# for i in range(5002, 5005):
#     print(i)
#     mock.return_value = FakeParser(i)
#     t = threading.Thread(target=command_line_runner)
#     # command_line_runner()
#     t.start()
#     time.sleep(3)
#
# patcher.stop()

# python noderunner.py -p 500x
command_line_runner()


# from noderunner import new_node
# def new_node(port):
#     patcher = patch('dokuztas.node.get_parser')
#     mock = patcher.start()
#     mock.return_value = FakeParser(arg_port=port)
#     command_line_runner()
#     patcher.stop()
