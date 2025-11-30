from app import db
from datetime import datetime
import uuid

class FraudCheck(db.Model):
    __tablename__ = 'fraud_checks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = db.Column(db.String(36), db.ForeignKey('transactions.id'), nullable=False, unique=True, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    risk_score = db.Column(db.Float, nullable=False, index=True)
    risk_level = db.Column(db.String(50), nullable=False, index=True)  # low, medium, high, critical
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, approved, rejected, review
    rules_triggered = db.Column(db.JSON)  # List of triggered fraud rules
    device_fingerprint = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    geolocation = db.Column(db.JSON)
    velocity_checks = db.Column(db.JSON)  # Transaction velocity data
    pattern_analysis = db.Column(db.JSON)  # Behavioral pattern analysis
    decision_reason = db.Column(db.Text)
    reviewed_by = db.Column(db.String(36), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'status': self.status,
            'rules_triggered': self.rules_triggered,
            'decision_reason': self.decision_reason,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<FraudCheck {self.id} risk={self.risk_score}>'

class RiskScore(db.Model):
    __tablename__ = 'risk_scores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False, index=True)
    account_age_score = db.Column(db.Float)
    transaction_history_score = db.Column(db.Float)
    velocity_score = db.Column(db.Float)
    device_score = db.Column(db.Float)
    location_score = db.Column(db.Float)
    kyc_score = db.Column(db.Float)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'overall_score': self.overall_score,
            'account_age_score': self.account_age_score,
            'transaction_history_score': self.transaction_history_score,
            'velocity_score': self.velocity_score,
            'device_score': self.device_score,
            'location_score': self.location_score,
            'kyc_score': self.kyc_score,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }
    
    def __repr__(self):
        return f'<RiskScore {self.user_id} score={self.overall_score}>'


