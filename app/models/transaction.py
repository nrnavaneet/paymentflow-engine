from app import db
from datetime import datetime
from decimal import Decimal
import uuid
import enum

class TransactionStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REVERSED = 'reversed'
    REFUNDED = 'refunded'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False, index=True)  # deposit, withdrawal, transfer, payment, refund
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False, index=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, index=True)
    fee = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    net_amount = db.Column(db.Numeric(20, 2), nullable=False)
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(255), unique=True, index=True)
    external_reference = db.Column(db.String(255), index=True)
    source_wallet_id = db.Column(db.String(36), db.ForeignKey('wallets.id'), nullable=True)
    destination_wallet_id = db.Column(db.String(36), db.ForeignKey('wallets.id'), nullable=True)
    payment_id = db.Column(db.String(36), db.ForeignKey('payments.id'), nullable=True)
    settlement_id = db.Column(db.String(36), db.ForeignKey('settlements.id'), nullable=True)
    fraud_check_id = db.Column(db.String(36), db.ForeignKey('fraud_checks.id'), nullable=True)
    compliance_check_id = db.Column(db.String(36), db.ForeignKey('compliance_checks.id'), nullable=True)
    metadata = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_wallet = db.relationship('Wallet', foreign_keys=[source_wallet_id], backref='outgoing_transactions')
    destination_wallet = db.relationship('Wallet', foreign_keys=[destination_wallet_id], backref='incoming_transactions')
    
    def to_dict(self, include_metadata=False):
        data = {
            'id': self.id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'status': self.status.value if isinstance(self.status, TransactionStatus) else self.status,
            'amount': float(self.amount),
            'currency': self.currency,
            'fee': float(self.fee),
            'net_amount': float(self.net_amount),
            'description': self.description,
            'reference_id': self.reference_id,
            'external_reference': self.external_reference,
            'source_wallet_id': self.source_wallet_id,
            'destination_wallet_id': self.destination_wallet_id,
            'error_message': self.error_message,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_metadata and self.metadata:
            data['metadata'] = self.metadata
        
        return data
    
    def __repr__(self):
        return f'<Transaction {self.id} {self.transaction_type} {self.amount} {self.currency}>'

