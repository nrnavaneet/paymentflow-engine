from app.repositories.base_repository import BaseRepository
from app.models.settlement import Settlement, SettlementBatch, SettlementStatus
from typing import Optional, List
from app import db

class SettlementRepository(BaseRepository):
    def __init__(self):
        super().__init__(Settlement)
    
    def get_pending_batches(self) -> List[SettlementBatch]:
        return SettlementBatch.query.filter_by(status=SettlementStatus.PENDING).all()
    
    def create_batch(self, batch_number: str, currency: str) -> SettlementBatch:
        batch = SettlementBatch(
            batch_number=batch_number,
            currency=currency,
            status=SettlementStatus.PENDING
        )
        db.session.add(batch)
        db.session.commit()
        return batch

