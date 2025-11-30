from app.repositories.base_repository import BaseRepository
from app.models.transaction import Transaction, TransactionStatus
from typing import Optional, List
from app import db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Transaction)
    
    def get_by_account(self, account_id: str, limit: Optional[int] = None) -> List[Transaction]:
        query = Transaction.query.filter_by(account_id=account_id)
        if limit:
            query = query.limit(limit)
        return query.order_by(Transaction.created_at.desc()).all()
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Transaction]:
        query = Transaction.query.filter_by(user_id=user_id)
        if limit:
            query = query.limit(limit)
        return query.order_by(Transaction.created_at.desc()).all()
    
    def get_by_status(self, status: TransactionStatus, limit: Optional[int] = None) -> List[Transaction]:
        query = Transaction.query.filter_by(status=status)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_pending_settlement(self, limit: int = 100) -> List[Transaction]:
        return Transaction.query.filter(
            and_(
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.settlement_id.is_(None)
            )
        ).limit(limit).all()
    
    def get_by_reference(self, reference_id: str) -> Optional[Transaction]:
        return Transaction.query.filter_by(reference_id=reference_id).first()
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                         account_id: Optional[str] = None) -> List[Transaction]:
        query = Transaction.query.filter(
            and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        )
        if account_id:
            query = query.filter_by(account_id=account_id)
        return query.order_by(Transaction.created_at).all()
    
    def get_user_transaction_summary(self, user_id: str, days: int = 30) -> dict:
        """Get transaction summary for fraud/risk analysis"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        transactions = Transaction.query.filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.created_at >= cutoff
            )
        ).all()
        
        return {
            'total_count': len(transactions),
            'total_amount': sum(float(t.amount) for t in transactions),
            'avg_amount': sum(float(t.amount) for t in transactions) / len(transactions) if transactions else 0,
            'by_type': {},
            'by_status': {},
        }
    
    # TODO: Add indexes for better query performance
    # TODO: Implement transaction archiving for old transactions

