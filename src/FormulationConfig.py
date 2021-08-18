import os
from Role import Role
from MessageType import MessageType


LOCAL = "LOCAL"

DEFAULT_ROLE = Role.INTERMEDIARY


class Formulation:
    def __init__(self, role, data=DEFAULT_ROLE, compute=DEFAULT_ROLE, audit=DEFAULT_ROLE, control=DEFAULT_ROLE):
        self.role = role
        self.action_locations = {
            MessageType.DATA: data,
            MessageType.COMPUTE_AGGREGATE: compute,
            MessageType.COMPUTE_MAP: data,
            MessageType.AUDIT: audit,
            MessageType.CONTROL: control,
        }
        self.third_parties = []
        self.intermediary = None
        self.users = []
    
    def register_third_party(self, container_id):
        self.third_parties.append(container_id)
    
    def register_user(self, container_id):
        self.users.append(container_id)
    
    def register_intermediary(self, container_id):
        self.intermediary = container_id
    
    def is_local(self, msg):
        return self.role == self.action_locations[msg.message_type]
    
    def get_location(self, msg_type):
        return self.action_locations[msg_type]
            
    def get_target_containers(self, msg_type, targets):
        role = self.get_location(msg_type)
        containers = {}
        if role == self.role:
            containers = {LOCAL: targets}
        if role == Role.INTERMEDIARY:
            containers = {self.intermediary: targets}
        if role == Role.THIRD_PARTY:
            if len(self.third_parties) > 0:
                container_id = self.third_parties[0]
            else:
                container_id = self.intermediary
            containers = {container_id: targets}
        if role == Role.USER:
            if len(self.users) > 0:
                containers = {t: [t] for t in targets}
            else:
                containers = {self.intermediary: targets}
        return containers
