from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.logger import get_logger

logger = get_logger(__name__)
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/transactions', methods=['GET'])
@jwt_required()
def transaction_report():
    try:
        user_id = get_jwt_identity()
        from app.repositories.transaction_repository import TransactionRepository
        from datetime import datetime, timedelta
        
        transaction_repo = TransactionRepository()
        
        # Get date range from query params
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        transactions = transaction_repo.get_by_date_range(start_date, end_date)
        user_transactions = [t for t in transactions if t.user_id == user_id]
        
        total_amount = sum(float(t.amount) for t in user_transactions)
        total_fees = sum(float(t.fee) for t in user_transactions)
        
        by_type = {}
        by_status = {}
        
        for t in user_transactions:
            by_type[t.transaction_type] = by_type.get(t.transaction_type, 0) + 1
            status = t.status.value if hasattr(t.status, 'value') else t.status
            by_status[status] = by_status.get(status, 0) + 1
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_transactions': len(user_transactions),
                'total_amount': total_amount,
                'total_fees': total_fees,
                'net_amount': total_amount - total_fees
            },
            'breakdown': {
                'by_type': by_type,
                'by_status': by_status
            }
        }
        
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500

@reports_bp.route('/compliance', methods=['GET'])
@jwt_required()
def compliance_report():
    try:
        user_id = get_jwt_identity()
        from app.repositories.compliance_repository import ComplianceRepository
        
        compliance_repo = ComplianceRepository()
        checks = compliance_repo.get_by_user(user_id)
        
        report = {
            'total_checks': len(checks),
            'by_status': {},
            'kyc_status': 'not_submitted'
        }
        
        for check in checks:
            status = check.status
            report['by_status'][status] = report['by_status'].get(status, 0) + 1
        
        kyc = compliance_repo.get_user_kyc(user_id)
        if kyc:
            report['kyc_status'] = kyc.status
        
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        return jsonify({'error': 'Failed to generate compliance report'}), 500

@reports_bp.route('/fraud', methods=['GET'])
@jwt_required()
def fraud_report():
    try:
        user_id = get_jwt_identity()
        from app.repositories.fraud_repository import FraudRepository
        
        fraud_repo = FraudRepository()
        checks = fraud_repo.get_by_user(user_id)
        
        report = {
            'total_checks': len(checks),
            'by_risk_level': {},
            'average_risk_score': 0.0
        }
        
        total_score = 0.0
        for check in checks:
            risk_level = check.risk_level
            report['by_risk_level'][risk_level] = report['by_risk_level'].get(risk_level, 0) + 1
            total_score += check.risk_score
        
        if checks:
            report['average_risk_score'] = total_score / len(checks)
        
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error generating fraud report: {str(e)}")
        return jsonify({'error': 'Failed to generate fraud report'}), 500


