from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.payment_service import PaymentService
from app.utils.logger import get_logger

logger = get_logger(__name__)
payments_bp = Blueprint('payments', __name__)
payment_service = PaymentService()

@payments_bp.route('', methods=['POST'])
@jwt_required()
def process_payment():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('account_id') or not data.get('amount'):
            return jsonify({'error': 'Account ID and amount are required'}), 400
        
        payment = payment_service.process_payment(user_id, data['account_id'], data)
        
        return jsonify(payment.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        return jsonify({'error': 'Payment processing failed'}), 500

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    try:
        user_id = get_jwt_identity()
        payments = payment_service.payment_repo.get_by_user(user_id)
        return jsonify([p.to_dict() for p in payments]), 200
    except Exception as e:
        logger.error(f"Error getting payments: {str(e)}")
        return jsonify({'error': 'Failed to get payments'}), 500

# TODO: Add payment refund endpoint
# TODO: Add payment status check endpoint

