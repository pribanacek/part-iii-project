from Message import ResultMessage
import dill
import zmq
import time


class MessageServer:
    def __init__(self, port):
        context = zmq.Context()
        self.address = '0.0.0.0'
        self.port = port
        self.socket = context.socket(zmq.REP)

    def bind(self):
        target = "tcp://%s:%s" % (self.address, self.port)
        print("Server binding on", target)
        self.socket.bind(target)
    
    def register_poller(self, poller):
        poller.register(self.socket, zmq.POLLIN)
    
    def has_data(self, poller_socks):
        return self.socket in poller_socks and poller_socks[self.socket] == zmq.POLLIN
    
    def recv(self):
        data = self.socket.recv()
        start_time = time.time()
        msg = dill.loads(data)
        end_time = time.time()
        print('Message deserialisation took %.4f seconds' % (end_time - start_time))
        print('Message size %d bytes' % len(data))
        msg_time = msg.timestamp
        print('Comms took %.4f seconds' % (start_time - msg_time))
        if msg.message_type == "SOCKET_TEST":
            response_msg = ResultMessage(msg, (len(data), start_time - msg_time))
            self.send(response_msg)
        return msg
    
    def send(self, msg):
        start_time = time.time()
        msg.timestamp = time.time()
        data = dill.dumps(msg)
        end_time = time.time()
        print('Message serialisation took %.4f seconds' % (end_time - start_time))
        self.socket.send(data)
