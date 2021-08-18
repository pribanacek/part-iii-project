import dill
import zmq
import time

class MessageClient:
    def __init__(self, address, port=8000):
        context = zmq.Context()
        self.address = address
        self.port = port
        self.socket = context.socket(zmq.REQ)

    def connect(self):
        target = "tcp://%s:%s" % (self.address, self.port)
        self.socket.connect(target)
    
    def register_poller(self, poller):
        poller.register(self.socket, zmq.POLLIN)
    
    def has_data(self, poller_socks):
        return self.socket in poller_socks and poller_socks[self.socket] == zmq.POLLIN
    
    def send(self, msg):
        msg.timestamp = time.time()
        start_time = time.time()
        data = dill.dumps(msg)
        end_time = time.time()
        print('message serialization took %.4f seconds' % (end_time - start_time))
        print('sending message with %d bytes' % len(data))
        return self.socket.send(data)
    
    def recv(self):
        data = self.socket.recv()
        msg = dill.loads(data)
        start_time = time.time()
        print('Comms took %.4f seconds' % (msg.timestamp - start_time))
        return msg
