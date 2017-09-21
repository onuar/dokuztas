class ChainNotCreatedException(Exception):
    def __init__(self):
        super(ChainNotCreatedException, self).__init__()


class MinerException(Exception):
    def __init__(self):
        super(MinerException, self).__init__()


class PendingTxException(Exception):
    def __init__(self):
        super(PendingTxException, self).__init__()
