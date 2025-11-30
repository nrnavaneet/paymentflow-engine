from app import db
from datetime import datetime
from decimal import Decimal
import uuid

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    account_type = db.Column(db.String(50), default='standard', nullable=False)  # standard, business, merchant
    status = db.Column(db.String(50), default='active', nullable=False, index=True)  # active, suspended, closed
    currency = db.Column(db.String(3), default='USD', nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallets = db.relationship('Wallet', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')
    
    def to_dict(self, include_balance=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'status': self.status,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_balance:
            total_balance = sum(w.balance for w in self.wallets)
            data['total_balance'] = float(total_balance)
            data['wallets'] = [w.to_dict() for w in self.wallets]
        
        return data
    
    def __repr__(self):
        return f'<Account {self.id}>'

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False, index=True)
    wallet_type = db.Column(db.String(50), nullable=False)  # main, escrow, reserve
    currency = db.Column(db.String(3), nullable=False, index=True)
    balance = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    available_balance = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    frozen_balance = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('account_id', 'wallet_type', 'currency', name='unique_wallet'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'wallet_type': self.wallet_type,
            'currency': self.currency,
            'balance': float(self.balance),
            'available_balance': float(self.available_balance),
            'frozen_balance': float(self.frozen_balance),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Wallet {self.wallet_type} {self.currency}>'

