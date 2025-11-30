from app.repositories.base_repository import BaseRepository
from app.models.compliance import ComplianceCheck, KYCRecord
from typing import Optional, List
from app import db

class ComplianceRepository(BaseRepository):
    def __init__(self):
        super().__init__(ComplianceCheck)
    
    def get_by_transaction(self, transaction_id: str) -> Optional[ComplianceCheck]:
        return ComplianceCheck.query.filter_by(transaction_id=transaction_id).first()
    
    def get_user_kyc(self, user_id: str) -> Optional[KYCRecord]:
        return KYCRecord.query.filter_by(user_id=user_id).order_by(
            KYCRecord.created_at.desc()
        ).first()
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[ComplianceCheck]:
        query = ComplianceCheck.query.filter_by(user_id=user_id)
        if limit:
            query = query.limit(limit)
        return query.order_by(ComplianceCheck.created_at.desc()).all()
    
    def get_pending_kyc(self, limit: int = 100) -> List[KYCRecord]:
        return KYCRecord.query.filter_by(status='pending').limit(limit).all()


