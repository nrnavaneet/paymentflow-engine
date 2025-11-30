from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.transaction_service import TransactionService
from app.utils.logger import get_logger

logger = get_logger(__name__)
transactions_bp = Blueprint('transactions', __name__)
transaction_service = TransactionService()

@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('account_id') or not data.get('amount'):
            return jsonify({'error': 'Account ID and amount are required'}), 400
        
        # Get request metadata for fraud detection
        request_data = {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'device_fingerprint': request.headers.get('X-Device-Fingerprint'),
            'geolocation': data.get('geolocation')
        }
        
        transaction = transaction_service.create_transaction(
            data['account_id'],
            user_id,
            data
        )
        
        return jsonify(transaction.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        return jsonify({'error': 'Failed to create transaction'}), 500

@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        user_id = get_jwt_identity()
        account_id = request.args.get('account_id')
        
        if account_id:
            transactions = transaction_service.transaction_repo.get_by_account(account_id)
        else:
            transactions = transaction_service.transaction_repo.get_by_user(user_id)
        
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({'error': 'Failed to get transactions'}), 500

@transactions_bp.route('/<transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    try:
        user_id = get_jwt_identity()
        transaction = transaction_service.transaction_repo.get_by_id(transaction_id)
        
        if not transaction or transaction.user_id != user_id:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify(transaction.to_dict(include_metadata=True)), 200
    except Exception as e:
        logger.error(f"Error getting transaction: {str(e)}")
        return jsonify({'error': 'Failed to get transaction'}), 500

# TODO: Add transaction reversal endpoint
# TODO: Add transaction refund endpoint
# TODO: Add transaction cancellation endpoint

