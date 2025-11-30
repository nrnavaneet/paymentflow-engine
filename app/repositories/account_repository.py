from app.repositories.base_repository import BaseRepository
from app.models.account import Account, Wallet
from typing import Optional, List
from app import db

class AccountRepository(BaseRepository):
    def __init__(self):
        super().__init__(Account)
    
    def get_by_user(self, user_id: str) -> List[Account]:
        return Account.query.filter_by(user_id=user_id).all()
    
    def get_user_main_account(self, user_id: str, currency: str = 'USD') -> Optional[Account]:
        return Account.query.filter_by(
            user_id=user_id,
            account_type='standard',
            currency=currency,
            status='active'
        ).first()
    
    def get_wallet(self, account_id: str, wallet_type: str, currency: str) -> Optional[Wallet]:
        return Wallet.query.filter_by(
            account_id=account_id,
            wallet_type=wallet_type,
            currency=currency
        ).first()
    
    def get_or_create_wallet(self, account_id: str, wallet_type: str, currency: str) -> Wallet:
        wallet = self.get_wallet(account_id, wallet_type, currency)
        if not wallet:
            wallet = Wallet(
                account_id=account_id,
                wallet_type=wallet_type,
                currency=currency
            )
            db.session.add(wallet)
            db.session.commit()
        return wallet

