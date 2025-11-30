from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.account_service import AccountService
from app.utils.logger import get_logger

logger = get_logger(__name__)
accounts_bp = Blueprint('accounts', __name__)
account_service = AccountService()

@accounts_bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        account = account_service.create_account(user_id, data)
        return jsonify(account.to_dict(include_balance=True)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
        return jsonify({'error': 'Failed to create account'}), 500

@accounts_bp.route('', methods=['GET'])
@jwt_required()
def get_accounts():
    try:
        user_id = get_jwt_identity()
        accounts = account_service.account_repo.get_by_user(user_id)
        return jsonify([a.to_dict(include_balance=True) for a in accounts]), 200
    except Exception as e:
        logger.error(f"Error getting accounts: {str(e)}")
        return jsonify({'error': 'Failed to get accounts'}), 500

@accounts_bp.route('/<account_id>/balance', methods=['GET'])
@jwt_required()
def get_balance(account_id):
    try:
        user_id = get_jwt_identity()
        currency = request.args.get('currency')
        
        balance = account_service.get_account_balance(account_id, currency)
        return jsonify(balance), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        return jsonify({'error': 'Failed to get balance'}), 500

