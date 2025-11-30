from app.repositories.user_repository import UserRepository
from app.models.user import User
from app import db
from flask_jwt_extended import create_access_token, create_refresh_token
from typing import Optional, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
    
    def register(self, email: str, username: str, password: str, first_name: str = None, last_name: str = None) -> Dict:
        # Check if user already exists
        if self.user_repo.get_by_email(email):
            raise ValueError("Email already registered")
        if self.user_repo.get_by_username(username):
            raise ValueError("Username already taken")
        
        # Create new user
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        try:
            user = self.user_repo.create(user)
            logger.info(f"User registered: {user.id}")
            
            # Generate tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'user': user.to_dict(include_sensitive=False),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            db.session.rollback()
            raise
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        user = self.user_repo.get_by_email(email)
        
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for email: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {user.id}")
            raise ValueError("Account is inactive")
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        self.user_repo.update(user)
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.info(f"User logged in: {user.id}")
        
        return {
            'user': user.to_dict(include_sensitive=False),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def refresh_token(self, user_id: str) -> Dict:
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid user")
        
        access_token = create_access_token(identity=str(user.id))
        return {'access_token': access_token}
    
    def get_current_user(self, user_id: str) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

