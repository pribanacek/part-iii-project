import numpy as np

from MessageType import MessageType
from Message import ComputeMessage

DEFAULT_MAP = lambda x, y: y
DEFAULT_REDUCE = lambda x, y: y

def basic_fetch(caller, targets):

    def fetch_data(target_ids, result):
        result = {}
        for t in target_ids:
            result[t] = np.random.rand(4000000)  # about 32MB in size
        return result

    compute_functions = {
        MessageType.COMPUTE_AGGREGATE: DEFAULT_REDUCE,
        MessageType.COMPUTE_MAP: DEFAULT_MAP,
        MessageType.DATA: fetch_data,
    }

    computation = ComputeMessage('BASIC_FETCH', targets, caller=caller, compute_functions=compute_functions)
    return computation
