from app import db
from datetime import datetime
from decimal import Decimal
import uuid
import enum

class SettlementStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class SettlementBatch(db.Model):
    __tablename__ = 'settlement_batches'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum(SettlementStatus), default=SettlementStatus.PENDING, nullable=False, index=True)
    total_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    total_fees = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    transaction_count = db.Column(db.Integer, default=0, nullable=False)
    processed_count = db.Column(db.Integer, default=0, nullable=False)
    failed_count = db.Column(db.Integer, default=0, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    settlements = db.relationship('Settlement', backref='batch', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_number': self.batch_number,
            'status': self.status.value if isinstance(self.status, SettlementStatus) else self.status,
            'total_amount': float(self.total_amount),
            'total_fees': float(self.total_fees),
            'currency': self.currency,
            'transaction_count': self.transaction_count,
            'processed_count': self.processed_count,
            'failed_count': self.failed_count,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<SettlementBatch {self.batch_number}>'

class Settlement(db.Model):
    __tablename__ = 'settlements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = db.Column(db.String(36), db.ForeignKey('settlement_batches.id'), nullable=False, index=True)
    transaction_id = db.Column(db.String(36), db.ForeignKey('transactions.id'), nullable=False, unique=True, index=True)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    fee = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    net_amount = db.Column(db.Numeric(20, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)
    settlement_reference = db.Column(db.String(255), unique=True, index=True)
    error_message = db.Column(db.Text)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'amount': float(self.amount),
            'fee': float(self.fee),
            'net_amount': float(self.net_amount),
            'currency': self.currency,
            'status': self.status,
            'settlement_reference': self.settlement_reference,
            'error_message': self.error_message,
            'processed_at': self.processed_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Settlement {self.id}>'

