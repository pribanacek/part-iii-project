from ContainerManager import ContainerManager
from src.Role import Role
from src.MessageType import MessageType

USERS = list(range(10, 51, 10))  # range 10-50 users at interval of 10
EXPERIMENT = "DATA_FETCH"
# EXPERIMENT = "FED_AVG"

FORMULATIONS = {
    'SQ': {
        MessageType.AUDIT: Role.THIRD_PARTY,
        MessageType.CONTROL: Role.THIRD_PARTY,
        MessageType.COMPUTE_AGGREGATE: Role.THIRD_PARTY,
        MessageType.COMPUTE_MAP: Role.THIRD_PARTY,
        MessageType.DATA: Role.THIRD_PARTY,
    },
    'A': {
        MessageType.AUDIT: Role.THIRD_PARTY,
        MessageType.CONTROL: Role.THIRD_PARTY,
        MessageType.COMPUTE_AGGREGATE: Role.INTERMEDIARY,
        MessageType.COMPUTE_MAP: Role.INTERMEDIARY,
        MessageType.DATA: Role.INTERMEDIARY,
    },
    'B': {
        MessageType.AUDIT: Role.THIRD_PARTY,
        MessageType.CONTROL: Role.THIRD_PARTY,
        MessageType.COMPUTE_AGGREGATE: Role.INTERMEDIARY,
        MessageType.COMPUTE_MAP: Role.USER,
        MessageType.DATA: Role.USER,
    },
    'C': {
        MessageType.AUDIT: Role.THIRD_PARTY,
        MessageType.CONTROL: Role.THIRD_PARTY,
        MessageType.COMPUTE_AGGREGATE: Role.USER,
        MessageType.COMPUTE_MAP: Role.USER,
        MessageType.DATA: Role.USER,
    },
}

def main():
    formulations = FORMULATIONS.keys()
    for formulation_name in formulations:
        formulation = FORMULATIONS[formulation_name]
        manager = ContainerManager()
        manager.run_experiment(EXPERIMENT, formulation, formulation_name, USERS, iterations=5)
    print('... and we are done.')

if __name__ == '__main__':
    main()
