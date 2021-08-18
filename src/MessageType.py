from enum import Enum

class MessageType(Enum):
    DATA = 'DATA'
    COMPUTE_MAP = 'COMPUTE_MAP'
    COMPUTE_AGGREGATE = 'COMPUTE_AGGREGATE'
    AUDIT = 'AUDIT'
    CONTROL = 'CONTROL'
