from app.repositories.base_repository import BaseRepository
from app.models.payment import Payment, PaymentMethod
from typing import Optional, List
from app import db

class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Payment)
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Payment]:
        query = Payment.query.filter_by(user_id=user_id)
        if limit:
            query = query.limit(limit)
        return query.order_by(Payment.created_at.desc()).all()
    
    def get_by_gateway_transaction_id(self, gateway_transaction_id: str) -> Optional[Payment]:
        return Payment.query.filter_by(gateway_transaction_id=gateway_transaction_id).first()
    
    def get_pending_payments(self, limit: int = 100) -> List[Payment]:
        return Payment.query.filter_by(status='pending').limit(limit).all()

