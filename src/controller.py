# ignore tensorflow warnings
# from typing import Collection
# import warnings
# warnings.filterwarnings('ignore',category=FutureWarning)

import os
import sys
import time
from Message import ComputeMessage, SocketTestMessage
from MessageClient import MessageClient
from MessageType import MessageType

from test_computations.federated_average import fed_avg
from test_computations.basic_fetch import basic_fetch

import random, numpy as np

CALLER_ID = os.environ['CONTAINER_ID']
SERVER_PORT = os.environ['SERVER_PORT']
NUMBER_OF_USERS = int(os.environ['NUMBER_OF_USERS'])

TARGETS = ['user-' + str(i) for i in range(NUMBER_OF_USERS)]

def wait_for_startup(client):
    compute_msg = basic_fetch(CALLER_ID, TARGETS)
    client.send(compute_msg)
    client.recv()

def time_computation(client, msg):
    start_time = time.time()
    client.send(msg)
    result = client.recv()
    end_time = time.time()
    return end_time - start_time

def run_experiment(computation, repeats=3):
    compute_msg = computation(CALLER_ID, TARGETS)
    client = MessageClient(address='127.0.0.1', port=SERVER_PORT)
    client.connect()

    # first msg will take longer as system may still be starting up, so we exclude it from measurements
    wait_for_startup(client)

    results = np.array([None for _ in range(repeats)])
    for i in range(repeats):
        t = time_computation(client, compute_msg)
        results[i] = t
    return results

def run_socket_test(lengths=[1000], repeats=5):
    client = MessageClient(address='127.0.0.1', port=SERVER_PORT)
    client.connect()

    # first msg will take longer as system may still be starting up, so we exclude it from measurements
    wait_for_startup(client)

    results = {}
    for l in lengths:
        sizes = [None for _ in range(repeats)]
        times = [None for _ in range(repeats)]
        for i in range(repeats):
            msg = SocketTestMessage(l)
            client.send(msg)
            result_msg = client.recv()
            sizes[i], times[i] = result_msg.result
        results[l] = (sizes, times)
    return results

def socket_timing(iterations):
    lengths = list(range(int(10e6), int(100e6) + 1, int(10e6)))
    results = run_socket_test(lengths=lengths, repeats=iterations)
    print('\nFinal results')
    print('x\ty\t\tey')
    for l, (sizes, times) in results.items():
        x = np.mean(sizes)
        y = np.mean(times)
        e = 2 * np.std(times)
        print("%d\t%.4f\t%.4f" % (x, y, e))


EXPERIMENTS = {
    'DATA_FETCH': basic_fetch,
    'FED_AVG': fed_avg,
}

def main():
    iterations = int(sys.argv[2])
    experiment = EXPERIMENTS[sys.argv[1]]

    results = run_experiment(experiment, repeats=iterations)
    print('Mean', np.mean(results))
    print('STDEV', np.std(results))

if __name__ == "__main__":
    main()
