from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.repositories.user_repository import UserRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)
user_repo = UserRepository()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = user_repo.get_by_id(user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'Invalid or inactive user'}), 401
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = user_repo.get_by_id(user_id)
            
            if not user or not user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Admin middleware error: {str(e)}")
            return jsonify({'error': 'Admin access required'}), 403
    
    return decorated_function


