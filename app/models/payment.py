from app import db
from datetime import datetime
from decimal import Decimal
import uuid
import enum

class PaymentMethod(enum.Enum):
    CARD = 'card'
    BANK_TRANSFER = 'bank_transfer'
    WALLET = 'wallet'
    CRYPTO = 'crypto'
    OTHER = 'other'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False, index=True)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False, index=True)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, index=True)
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)  # pending, processing, completed, failed, cancelled
    gateway = db.Column(db.String(100))  # stripe, paypal, etc.
    gateway_transaction_id = db.Column(db.String(255), index=True)
    gateway_response = db.Column(db.JSON)
    description = db.Column(db.Text)
    metadata = db.Column(db.JSON)
    failure_reason = db.Column(db.Text)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='payment', lazy='dynamic')
    
    def to_dict(self, include_gateway_response=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'payment_method': self.payment_method.value if isinstance(self.payment_method, PaymentMethod) else self.payment_method,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'gateway': self.gateway,
            'gateway_transaction_id': self.gateway_transaction_id,
            'description': self.description,
            'failure_reason': self.failure_reason,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_gateway_response and self.gateway_response:
            data['gateway_response'] = self.gateway_response
        
        if self.metadata:
            data['metadata'] = self.metadata
        
        return data
    
    def __repr__(self):
        return f'<Payment {self.id} {self.amount} {self.currency}>'

