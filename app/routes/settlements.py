from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, require_admin
from app.services.settlement_service import SettlementService
from app.utils.logger import get_logger

logger = get_logger(__name__)
settlements_bp = Blueprint('settlements', __name__)
settlement_service = SettlementService()

@settlements_bp.route('/batches', methods=['POST'])
@jwt_required()
@require_admin
def create_settlement_batch():
    try:
        data = request.get_json() or {}
        currency = data.get('currency', 'USD')
        
        batch = settlement_service.create_settlement_batch(currency)
        return jsonify(batch.to_dict()), 201
    except Exception as e:
        logger.error(f"Error creating settlement batch: {str(e)}")
        return jsonify({'error': 'Failed to create settlement batch'}), 500

@settlements_bp.route('/batches/<batch_id>/process', methods=['POST'])
@jwt_required()
@require_admin
def process_settlement_batch(batch_id):
    try:
        batch = settlement_service.process_settlement_batch(batch_id)
        return jsonify(batch.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing settlement batch: {str(e)}")
        return jsonify({'error': 'Failed to process settlement batch'}), 500

# TODO: Add settlement batch listing endpoint
# TODO: Add settlement reconciliation endpoint

