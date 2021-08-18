import numpy as np
import os
import time
import psycopg2
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
DB_NAME = "intermediary_db"

class Database:
    def __init__(self, local_targets):
        self.local_targets = local_targets
        self.conn = None
        self.cursor = None
    
    def connect(self, max_tries=20, timeout=0.25):
        attempt = 1
        while attempt < max_tries:
            try:
                self.conn = connect(
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    database=DB_NAME,
                )
                self.initialise_local_data()
                print('connected after %d tries' % attempt)
                return
            except Exception as e:
                print('Failed to connect to postgres, retrying...')
                print(e)
                attempt += 1
                time.sleep(timeout)
        raise Exception('Failed to connect to postgres')
    
    def is_ready(self):
        return self.conn is not None and self.cursor is not None
        
    def execute(self, query, vars=None):
        while True:
            try:
                with self.conn as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, vars)
                        result = None if cursor.description is None else cursor.fetchall()
                        break
            except (psycopg2.errors.AdminShutdown, psycopg2.InterfaceError) as e:
                print('Had admin shutdown, need to reconnect')
                self.connect()
        return result
    
    def initialise_local_data(self):
        values = []
        for i in range(len(self.local_targets)):
            values.append(self.local_targets[i])
            values.append(list(np.random.rand(1000)))
        query = "INSERT INTO sample_dataset (target_id, val) VALUES %s;" % ','.join(["(%s, %s)"] * len(self.local_targets))
        self.execute(query, tuple(values))
