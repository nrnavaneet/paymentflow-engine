from app.repositories.base_repository import BaseRepository
from app.models.user import User
from typing import Optional, List
from app import db

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        return User.query.filter_by(username=username).first()
    
    def get_users_requiring_kyc(self, amount_threshold: float) -> List[User]:
        # TODO: Implement proper query to find users requiring KYC based on transaction amounts
        # This is a placeholder - needs proper implementation
        return User.query.filter_by(kyc_status='pending').all()

