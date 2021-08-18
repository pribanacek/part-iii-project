import zmq
from MessageClient import MessageClient
from MessageServer import MessageServer


class SocketManager:
    def __init__(self, server_port, container_addresses, formulation, on_message=None, on_reply=None):
        self.server = MessageServer(server_port)
        self.message_clients = {}
        self.client_states = {}
        self.formulation = formulation
        for container_id in container_addresses:
            self.message_clients[container_id] = MessageClient(container_id, port=server_port)
            self.client_states[container_id] = 'READY_TO_SEND'
        self.poller = zmq.Poller()
        self.server.register_poller(self.poller)
        for client in self.message_clients.values():
            client.register_poller(self.poller)
        
        if on_message is not None:
            self.on_receive_message = on_message
        if on_reply is not None:
            self.on_receive_reply = on_reply
    
    def start(self):
        self.server.bind()
        for container_id in self.message_clients:
            client = self.message_clients[container_id]
            client.connect()
    
    def poll(self, expecting_reply):
        socks = dict(self.poller.poll())

        if not expecting_reply and self.server.has_data(socks):
            msg = self.server.recv()
            if msg.message_type != "SOCKET_TEST":
                self.on_receive_message(msg)
        
        if expecting_reply:
            for container_id in self.message_clients:
                client = self.message_clients[container_id]
                if client.has_data(socks):
                    msg = client.recv()
                    self.client_states[container_id] = 'READY_TO_SEND'
                    if msg.message_type != "SOCKET_TEST":
                        self.on_receive_reply(msg)
    
    def send_reply(self, msg):
        self.server.send(msg)
    
    def send_message_to_container(self, container_id, msg):
        if container_id not in self.message_clients:
            container_id = self.formulation.intermediary
        self.message_clients[container_id].send(msg)
        self.client_states[container_id] = 'WAITING_FOR_REPLY'

    def on_receive_message(self, message):
        pass
    
    def on_receive_reply(self, message):
        pass
