import functools
import time
import threading


def _log(log_type, message):
    print(">>> {0}: {1}".format(log_type, message))


def execstat(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        startTime = time.time()
        response = func(*args, **kwargs)
        elapsedTime = time.time() - startTime
        _log('stat', 'function [{}] finished in {} ms'.format(
            func.__name__, int(elapsedTime * 1000)))
        return response

    return newfunc


class MiningThread(threading.Thread):
    def __init__(self, mine_target, args=()):
        super(MiningThread, self).__init__(target=mine_target, args=args)
        self.mine_target = mine_target
        self.target_args = args

    def start(self):
        _log('dev', 'Mining thread started')
        super(MiningThread, self).start()

    def stop(self):
        _log('dev', 'Mining thread stopped')
        # super(MiningThread, self).join()
