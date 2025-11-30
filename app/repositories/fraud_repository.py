from app.repositories.base_repository import BaseRepository
from app.models.fraud import FraudCheck, RiskScore
from typing import Optional, List
from app import db

class FraudRepository(BaseRepository):
    def __init__(self):
        super().__init__(FraudCheck)
    
    def get_by_transaction(self, transaction_id: str) -> Optional[FraudCheck]:
        return FraudCheck.query.filter_by(transaction_id=transaction_id).first()
    
    def get_high_risk_checks(self, limit: int = 50) -> List[FraudCheck]:
        return FraudCheck.query.filter(
            FraudCheck.risk_level.in_(['high', 'critical']),
            FraudCheck.status == 'pending'
        ).limit(limit).all()
    
    def get_latest_risk_score(self, user_id: str) -> Optional[RiskScore]:
        return RiskScore.query.filter_by(user_id=user_id).order_by(
            RiskScore.calculated_at.desc()
        ).first()

