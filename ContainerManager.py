from threading import local
import docker
import os 
import signal
import sys
import json
from numpy import number

from numpy.lib.user_array import container
from src.Role import Role
from src.MessageType import MessageType


current_directory = os.path.dirname(os.path.realpath(__file__))


class ContainerManager:
    def __init__(self):
        self.network_name = 'intermediary-network'
        self.client = docker.from_env()
        self.containers = {role: [] for role in Role}
        self.create_network_if_not_exists()
        signal.signal(signal.SIGINT, self.signal_handler)
        for c in self.client.containers.list(all=True):
            print('Removing trash first')
            c.stop(timeout=0)
            c.remove()
    
    def create_network_if_not_exists(self):
        if len(self.client.networks.list(names=[self.network_name])) == 0:
            self.client.networks.create(self.network_name)

    def spawn_container(self, container_id, role, server_port, formulation, container_addresses, local_data, number_of_users):
        json_formulation = {k.value: v.value for (k, v) in formulation.items()}
        environment_variables = {
            'ROLE': role.value,
            'CONTAINER_ID': container_id,
            'SERVER_PORT': server_port,
            'CONTAINERS': json.dumps(container_addresses),
            'LOCAL_DATA': json.dumps(local_data),
            'ACTION_LOCATIONS': json.dumps(json_formulation),
            'NUMBER_OF_USERS': number_of_users,
        }

        source_dir = current_directory + '/src'
        volume = {
            source_dir: {'bind': '/src', 'mode': 'rw'},
            source_dir + '/db': {'bind': '/docker-entrypoint-initdb.d', 'mode': 'rw'},
        }
        container = self.client.containers.run(
            'data_intermediary:latest',
            'python3 -u run.py',
            detach=True,
            environment=environment_variables,
            name=container_id,
            volumes=volume,
            network=self.network_name,
        )

        container.exec_run('bash /docker-entrypoint.sh postgres', detach=True)

        if role == Role.INTERMEDIARY and len(self.containers[role]) > 0:
            print('WARNING: intermediary container is already running')

        self.containers[role].append(container)

    def cleanup(self):
        for k in self.containers:
            for container in self.containers[k]:
                container.stop(timeout=0)
                container.remove()
        self.containers = {role: [] for role in Role}

    def signal_handler(self, sig, frame):
        self.cleanup()
        sys.exit(0)
    
    def get_known_containers(self, containers, role):
        if role in (Role.THIRD_PARTY, Role.USER):
            return containers[Role.INTERMEDIARY]
        return containers[Role.THIRD_PARTY] + containers[Role.USER]
    
    def get_local_data(self, container_id, role, formulation, containers):
        local_data = [container_id]
        if formulation[MessageType.DATA] in (Role.THIRD_PARTY, Role.INTERMEDIARY):
            if role == Role.USER:
                local_data = []
            elif formulation[MessageType.DATA] == role:
                local_data += containers[Role.USER]
        return local_data
    
    def spawn(self, containers, formulation, number_of_users):
        for role in containers:
            for container_id in containers[role]:
                server_port = 8000
                known_containers = self.get_known_containers(containers, role)
                local_data = self.get_local_data(container_id, role, formulation, containers)
                self.spawn_container(container_id, role, server_port, formulation, known_containers, local_data, number_of_users)

    def run_experiment(self, experiment, formulation, formulation_name, user_numbers=[3], iterations=3):
        print('Running experiment %s with %d iterations' % (experiment, iterations))

        final_results = {}
        
        for number_of_users in user_numbers:

            print('Running with %d users' % number_of_users)

            containers = {
                Role.INTERMEDIARY: ['intermediary'],
                Role.THIRD_PARTY: ['third-party'],
                Role.USER: ['user-' + str(i) for i in range(number_of_users)]
            }
            self.spawn(containers, formulation, number_of_users)
            third_party = self.containers[Role.THIRD_PARTY][0]
            cmd = "python3 controller.py %s %d" % (experiment, iterations)
            result = third_party.exec_run(cmd, stdout=True, stderr=True)

            print('Finished experiment:')
            result_text = result.output.decode('utf8')

            def f(x):
                lines = result_text.split('\n')
                stuff = list(filter(lambda l: l.lower().startswith(x), lines))
                if len(stuff) < 1:
                    return 0
                return float(stuff[0].split(' ')[1])
            final_results[number_of_users] = (f('mean'), 2 * f('stdev'))
            if final_results[number_of_users] == (0, 0):
                print('result_text')
                print(result_text)

            self.cleanup()

        print('\nFinal results')
        print('x\ty\t\tey\t\tlabel')
        for n in final_results:
            x, ey = final_results[n]
            print("%d\t%.4f\t%.4f\t%s" % (n, x, ey, formulation_name))
        print()
