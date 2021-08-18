# ignore tensorflow warnings
# import warnings
# warnings.filterwarnings('ignore',category=FutureWarning)

import json
import os
import time
from Database import Database
from Role import Role
from MessageType import MessageType
from AuditManager import AuditManager
from ComputeManager import ComputeManager
from FormulationConfig import Formulation, LOCAL

import random, numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

args = os.environ

PROFILE = False
if PROFILE:
    import cProfile

ROLE = Role[args['ROLE']]
CONTAINER_ID = args['CONTAINER_ID']
SERVER_PORT = int(args['SERVER_PORT'])
CONTAINERS = json.loads(args['CONTAINERS'])
ACTION_LOCATIONS = json.loads(args['ACTION_LOCATIONS'])
LOCAL_DATA = json.loads(args['LOCAL_DATA'])

formulation = Formulation(ROLE)
formulation.action_locations = {
    MessageType(k): Role(v) for k, v in ACTION_LOCATIONS.items()
}


for container_id in CONTAINERS:
    if container_id.startswith('intermediary'):
        formulation.register_intermediary(container_id)
    elif container_id.startswith('user'):
        formulation.register_user(container_id)
    elif container_id.startswith('third'):
        formulation.register_third_party(container_id)

def main():
    print('Running compute manager')
    db = Database(LOCAL_DATA)
    audit_manager = AuditManager(db, LOCAL_DATA)
    managers = {
        MessageType.DATA: db,
    }
    compute_manager = ComputeManager(formulation, CONTAINERS, LOCAL_DATA, SERVER_PORT, audit_manager)
    db.connect(timeout=1)
    compute_manager.run()

if __name__ == "__main__":
    if PROFILE:
        cProfile.run('main()')
    else:
        main()
