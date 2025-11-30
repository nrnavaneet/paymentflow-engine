from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.compliance_service import ComplianceService
from app.utils.logger import get_logger

logger = get_logger(__name__)
compliance_bp = Blueprint('compliance', __name__)
compliance_service = ComplianceService()

@compliance_bp.route('/kyc', methods=['POST'])
@jwt_required()
def submit_kyc():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('document_type'):
            return jsonify({'error': 'Document type is required'}), 400
        
        kyc_record = compliance_service.submit_kyc(user_id, data)
        return jsonify(kyc_record.to_dict()), 201
    except Exception as e:
        logger.error(f"Error submitting KYC: {str(e)}")
        return jsonify({'error': 'Failed to submit KYC'}), 500

@compliance_bp.route('/kyc/status', methods=['GET'])
@jwt_required()
def get_kyc_status():
    try:
        user_id = get_jwt_identity()
        kyc_record = compliance_service.compliance_repo.get_user_kyc(user_id)
        
        if not kyc_record:
            return jsonify({'status': 'not_submitted'}), 200
        
        return jsonify(kyc_record.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting KYC status: {str(e)}")
        return jsonify({'error': 'Failed to get KYC status'}), 500

# TODO: Add compliance check endpoints
# TODO: Add compliance reporting endpoints

