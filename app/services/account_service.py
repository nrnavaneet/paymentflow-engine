from app.repositories.account_repository import AccountRepository
from app.repositories.user_repository import UserRepository
from app.models.account import Account, Wallet
from app import db
from typing import Dict, Optional
from app.utils.logger import get_logger
import uuid

logger = get_logger(__name__)

class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.user_repo = UserRepository()
    
    def create_account(self, user_id: str, data: Dict) -> Account:
        """Create a new account for user"""
        # Verify user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        account = Account(
            id=str(uuid.uuid4()),
            user_id=user_id,
            account_type=data.get('account_type', 'standard'),
            currency=data.get('currency', 'USD'),
            status='active'
        )
        
        account = self.account_repo.create(account)
        
        # Create main wallet
        wallet = Wallet(
            id=str(uuid.uuid4()),
            account_id=account.id,
            wallet_type='main',
            currency=account.currency
        )
        db.session.add(wallet)
        db.session.commit()
        
        logger.info(f"Account created: {account.id} for user {user_id}")
        return account
    
    def get_account_balance(self, account_id: str, currency: str = None) -> Dict:
        """Get account balance information"""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        wallets = account.wallets.filter_by(currency=currency).all() if currency else account.wallets.all()
        
        total_balance = sum(float(w.balance) for w in wallets)
        total_available = sum(float(w.available_balance) for w in wallets)
        total_frozen = sum(float(w.frozen_balance) for w in wallets)
        
        return {
            'account_id': account_id,
            'currency': currency or 'all',
            'total_balance': total_balance,
            'total_available': total_available,
            'total_frozen': total_frozen,
            'wallets': [w.to_dict() for w in wallets]
        }
    
    # TODO: Add account suspension
    # TODO: Add account closure
    # TODO: Add account limits management

