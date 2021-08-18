import time
from Role import Role
from SocketManager import SocketManager
from Message import ComputeMessage, ResultMessage
import traceback


class ComputeManager:
    def __init__(self, formulation, container_addresses, local_targets, listen_port, audit_manager):
        self.targets_present = list(container_addresses)
        self.formulation = formulation
        self.local_targets = local_targets
        self.pending_messages = {}  # messages waiting for child responses
        self.partial_results = {}  # results from messages that are arguments for pending messages
        self.socket_manager = SocketManager(
            listen_port, container_addresses, formulation, on_message=self.process_with_errors, on_reply=self.process_reply
        )
        self.audit_manager = audit_manager
        self.socket_manager.start()

    def process_with_errors(self, msg):
        try:
            self.process_message(msg)
        except Exception as e:
            print(e)
    
    def process_message(self, msg):
        self.audit_manager.record_access(msg)
        self.pending_messages[msg.message_id] = msg
        self.partial_results[msg.message_id] = ResultMessage(msg)

        if self.formulation.is_local(msg):
            if msg.has_child():
                child_message = msg.get_child_message()
                self.process_message(child_message)
            else:
                targets = msg.targets
                result_msg = self.process_local_execute(msg, targets, None)
                self.process_reply(result_msg)
        else:
            # forward it onto the relevant place
            target_containers = self.formulation.get_target_containers(msg.message_type, msg.targets)
            container_ids = list(target_containers.keys())
            if len(container_ids) > 1:
                for container_id in target_containers:
                    new_msg = msg.get_fragment(target_containers[container_id])
                    self.socket_manager.send_message_to_container(container_id, new_msg)
            else:
                container_id = container_ids[0]
                self.socket_manager.send_message_to_container(container_id, msg)
    
    def process_local_execute(self, msg, targets, result_msg):
        start_time = time.time()
        try:
            result = msg.execute(targets, None if result_msg is None else result_msg.result)
        except Exception as e:
            traceback.print_exc()
            result = e
        end_time = time.time()

        if type(result) != dict or set(result.keys()) != set(targets):
            result = {t: result for t in targets}
        result_msg = ResultMessage(msg, result)
        missing_targets = result_msg.get_missing_targets()
        if len(missing_targets) > 0:
            result_msg.fill_incomplete_values()
        return result_msg
            
    def process_reply(self, result_msg):
        msg_id = result_msg.original_message_id
        # record the result in case we need it later
        if self.partial_results[msg_id] is None:
            self.partial_results[msg_id] = result_msg
        else:
            self.partial_results[msg_id].combine_partial_result(result_msg)
        
        partial_result = self.partial_results[msg_id]
        if partial_result.is_complete():
            original_msg = self.pending_messages[msg_id]
            if original_msg.has_parent() and original_msg.parent_msg_id in self.pending_messages:
                parent_msg = self.pending_messages[original_msg.parent_msg_id]
                parent_result = self.process_local_execute(parent_msg, parent_msg.targets, partial_result)
                if len(self.pending_messages) <= 1:
                    self.socket_manager.send_reply(parent_result)
                else:
                    self.process_reply(parent_result)
            else:
                self.socket_manager.send_reply(partial_result)
            del self.pending_messages[msg_id]
            del self.partial_results[msg_id]
    
    def run(self):
        while True:
            expecting_reply = len(self.pending_messages) > 0
            self.socket_manager.poll(expecting_reply)
