from app import db
from datetime import datetime
import uuid
import json

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # create, update, delete, approve, reject, etc.
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # transaction, account, payment, etc.
    entity_id = db.Column(db.String(36), nullable=False, index=True)
    changes = db.Column(db.Text)  # JSON string of changes
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def set_changes(self, changes_dict):
        self.changes = json.dumps(changes_dict)
    
    def get_changes(self):
        if self.changes:
            return json.loads(self.changes)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'changes': self.get_changes(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type} {self.entity_id}>'


