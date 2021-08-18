import dill
import time
from Role import Role
from SocketManager import SocketManager
from Message import ComputeMessage, ResultMessage


class AuditManager:
    def __init__(self, db, local_targets):
        self.db = db
        self.local_targets = local_targets
    
    def record_access(self, msg):
        entries = ','.join(["(%s, %s, %s, %s)"] * len(msg.targets))
        query = '''INSERT INTO logs (caller_id, target_id, msg_type, msg_content) VALUES %s;''' % entries
        msg_data = dill.dumps(msg)
        vars = []
        for target in msg.targets:
            vars += [msg.caller, target, msg.message_type.value, msg_data]
        self.db.execute(query, tuple(vars))
