from app import db
from datetime import datetime
import uuid

class ComplianceCheck(db.Model):
    __tablename__ = 'compliance_checks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = db.Column(db.String(36), db.ForeignKey('transactions.id'), nullable=False, unique=True, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    check_type = db.Column(db.String(50), nullable=False, index=True)  # aml, kyc, sanctions, pep
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)  # pending, passed, failed, review
    result = db.Column(db.JSON)  # Detailed check results
    provider = db.Column(db.String(100))  # External compliance provider
    provider_reference = db.Column(db.String(255))
    flags = db.Column(db.JSON)  # List of compliance flags
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
            'check_type': self.check_type,
            'status': self.status,
            'result': self.result,
            'provider': self.provider,
            'flags': self.flags,
            'decision_reason': self.decision_reason,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ComplianceCheck {self.id} {self.check_type}>'

class KYCRecord(db.Model):
    __tablename__ = 'kyc_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    document_type = db.Column(db.String(50), nullable=False)  # passport, id_card, driver_license
    document_number = db.Column(db.String(255))
    document_front_url = db.Column(db.String(500))
    document_back_url = db.Column(db.String(500))
    selfie_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)  # pending, verified, rejected
    verified_by = db.Column(db.String(36), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text)
    provider = db.Column(db.String(100))
    provider_reference = db.Column(db.String(255))
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_type': self.document_type,
            'status': self.status,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<KYCRecord {self.id} {self.status}>'


