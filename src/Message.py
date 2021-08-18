import os
import random
from MessageType import MessageType

class Message:
    def __init__(self, name, seqno=0, message_type="GENERIC", parent=None):
        self.name = name
        self.seqno = seqno
        self.message_id = name + "-" + str(seqno)
        self.message_type = message_type
        self.parent_msg_id = parent
        self.multi_result = False
        self.targets = None
    
    def has_parent(self):
        return self.parent_msg_id is not None
    
    def has_child(self):
        return False
    
    def get_child_message(self):
        return None
    
    def execute(self, target_ids, child_result):
        return None
    
    def get_fragment(self, target_ids):
        return None


DEFAULT_CALLER = "caller"


class ComputeMessage(Message):
    def __init__(self, name, targets, seqno=0, caller=DEFAULT_CALLER, compute_functions=None, message_type=MessageType.COMPUTE_AGGREGATE, parent=None):
        super().__init__(name, seqno=seqno, message_type=message_type, parent=parent)
        self.targets = targets
        self.caller = caller
        self.compute_functions = compute_functions
        self.multi_result = message_type != MessageType.COMPUTE_AGGREGATE
    
    def has_child(self):
        return self.message_type != MessageType.DATA
    
    def get_child_message(self):
        if self.message_type == MessageType.DATA:
            return None
        message_type = MessageType.DATA if self.message_type == MessageType.COMPUTE_MAP else MessageType.COMPUTE_MAP
        return ComputeMessage(self.name, self.targets, self.seqno+1, self.caller, self.compute_functions, message_type, parent=self.message_id)

    def execute(self, target_ids, child_result):
        return self.compute_functions[self.message_type](target_ids, child_result)
    
    def get_fragment(self, target_ids):
        return ComputeMessage(
            self.name, target_ids, seqno=self.seqno, caller=self.caller,
            compute_functions=self.compute_functions, message_type=self.message_type, parent=self.parent_msg_id
        )


class ResultMessage(Message):
    def __init__(self, original_message, result=None):
        super().__init__(original_message.name, seqno=original_message.seqno + 1, message_type="RESULT")
        self.original_message_id = original_message.message_id
        self.original_targets = original_message.targets
        self.result = result or {}
    
    def is_complete(self):
        return len(self.result) >= len(self.original_targets)
    
    def get_missing_targets(self):
        return set(self.original_targets) - set(self.result.keys())
    
    def combine_partial_result(self, other_result):
        for k in other_result.result:
            if k not in self.result:
                self.result[k] = other_result.result[k]
    
    def fill_incomplete_values(self):
        for t in self.original_targets:
            if t not in self.result:
                self.result[t] = None

class SocketTestMessage(Message):
    def __init__(self, length):
        super().__init__('SOCKET_TEST', message_type="SOCKET_TEST")
        self.payload = bytearray(length)
