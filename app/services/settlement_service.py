from app.repositories.settlement_repository import SettlementRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.settlement import Settlement, SettlementBatch, SettlementStatus
from app.models.transaction import Transaction
from app import db
from typing import List
from decimal import Decimal
from app.utils.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

class SettlementService:
    def __init__(self):
        self.settlement_repo = SettlementRepository()
        self.transaction_repo = TransactionRepository()
    
    def create_settlement_batch(self, currency: str = 'USD') -> SettlementBatch:
        """Create a new settlement batch"""
        batch_number = f"SETTLE-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        batch = self.settlement_repo.create_batch(batch_number, currency)
        logger.info(f"Settlement batch created: {batch.id}")
        return batch
    
    def process_settlement_batch(self, batch_id: str) -> SettlementBatch:
        """Process all transactions in a settlement batch"""
        batch = self.settlement_repo.get_by_id(batch_id)
        if not batch:
            raise ValueError("Batch not found")
        
        if batch.status != SettlementStatus.PENDING:
            raise ValueError(f"Batch is not pending: {batch.status}")
        
        batch.status = SettlementStatus.PROCESSING
        db.session.commit()
        
        # Get transactions for settlement
        transactions = self.transaction_repo.get_pending_settlement(
            limit=100  # TODO: Make configurable
        )
        
        total_amount = Decimal('0.00')
        total_fees = Decimal('0.00')
        processed_count = 0
        failed_count = 0
        
        for transaction in transactions:
            try:
                settlement = self._create_settlement(transaction, batch)
                total_amount += settlement.amount
                total_fees += settlement.fee
                processed_count += 1
            except Exception as e:
                logger.error(f"Settlement failed for transaction {transaction.id}: {str(e)}")
                failed_count += 1
        
        batch.total_amount = total_amount
        batch.total_fees = total_fees
        batch.transaction_count = len(transactions)
        batch.processed_count = processed_count
        batch.failed_count = failed_count
        batch.status = SettlementStatus.COMPLETED if failed_count == 0 else SettlementStatus.PROCESSING
        batch.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Settlement batch processed: {batch.id} processed={processed_count} failed={failed_count}")
        return batch
    
    def _create_settlement(self, transaction: Transaction, batch: SettlementBatch) -> Settlement:
        """Create settlement record for a transaction"""
        settlement = Settlement(
            id=str(uuid.uuid4()),
            batch_id=batch.id,
            transaction_id=transaction.id,
            account_id=transaction.account_id,
            amount=transaction.amount,
            fee=transaction.fee,
            net_amount=transaction.net_amount,
            currency=transaction.currency,
            status='pending',
            settlement_reference=f"STL-{uuid.uuid4().hex[:12].upper()}"
        )
        
        settlement = self.settlement_repo.create(settlement)
        
        # Update transaction with settlement reference
        transaction.settlement_id = settlement.id
        db.session.commit()
        
        return settlement
    
    # TODO: Add settlement reconciliation
    # TODO: Add settlement reporting
    # TODO: Add automated settlement scheduling

