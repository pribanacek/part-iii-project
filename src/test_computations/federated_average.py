import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from MessageType import MessageType
from Message import ComputeMessage


def fed_avg(caller, targets):
    N = 1000 # number of data points
    model_iterations = 1000
    server_weights = torch.randn(1, 1) * 100

    def compute_map(target_ids, result):
        new_results = {}
        for target_id, (X, t) in result.items():
            # initialise client model with server model
            client_model = nn.Linear(1, 1)
            with torch.no_grad():
                client_model.weight.copy_(server_weights)

            optimizer = optim.SGD(client_model.parameters(), lr=0.05)
            loss_fn = nn.MSELoss()
            for _ in range(model_iterations):
                optimizer.zero_grad()
                predictions = client_model(X)
                loss = loss_fn(predictions, t)
                loss.backward()
                optimizer.step()
            new_A = list(client_model.parameters())[0].data[0, 0].numpy()
            new_b = list(client_model.parameters())[1].data[0].numpy()
            new_results[target_id] = np.array((new_A, new_b))
        return new_results

    def compute_reduce(target_ids, result):
        client_models = np.array(list(result.values()))
        new_params = np.mean(client_models, axis=0)
        return new_params
    
    def fetch_data(target_ids, result):
        A = np.random.uniform(3, 4)
        b = np.random.uniform(5, 6)
        error = 0.1
        X = Variable(torch.randn(N, 1))
        t = A * X + b + Variable(torch.randn(N, 1) * error)
        return (X, t)

    compute_functions = {
        MessageType.COMPUTE_AGGREGATE: compute_reduce,
        MessageType.COMPUTE_MAP: compute_map,
        MessageType.DATA: fetch_data,
    }

    computation = ComputeMessage('FED_AVG', targets, caller=caller, compute_functions=compute_functions)
    return computation
