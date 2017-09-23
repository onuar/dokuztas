import time, functools


def _log(type, message):
    print(">>> {0}: {1}".format(type, message))


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
