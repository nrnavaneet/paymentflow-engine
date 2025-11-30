from flask import Blueprint, request, jsonify
from app.utils.logger import get_logger

logger = get_logger(__name__)
webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/gateway', methods=['POST'])
def gateway_webhook():
    try:
        data = request.get_json()
        signature = request.headers.get('X-Webhook-Signature')
        gateway = request.headers.get('X-Gateway', 'stripe')
        
        # Verify webhook signature
        if not _verify_webhook_signature(data, signature, gateway):
            logger.warning(f"Invalid webhook signature from {gateway}")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Process webhook based on event type
        event_type = data.get('type')
        event_data = data.get('data', {})
        
        if event_type == 'payment.succeeded':
            _handle_payment_succeeded(event_data, gateway)
        elif event_type == 'payment.failed':
            _handle_payment_failed(event_data, gateway)
        elif event_type == 'payment.refunded':
            _handle_payment_refunded(event_data, gateway)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        logger.info(f"Gateway webhook processed: {event_type} from {gateway}")
        return jsonify({'status': 'processed'}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def _verify_webhook_signature(data, signature, gateway):
    """Verify webhook signature"""
    # TODO: Implement actual signature verification based on gateway
    # For now, return True if signature is provided
    return signature is not None

def _handle_payment_succeeded(event_data, gateway):
    """Handle payment succeeded webhook"""
    from app.repositories.payment_repository import PaymentRepository
    payment_repo = PaymentRepository()
    
    gateway_transaction_id = event_data.get('transaction_id') or event_data.get('id')
    if gateway_transaction_id:
        payment = payment_repo.get_by_gateway_transaction_id(gateway_transaction_id)
        if payment:
            payment.status = 'completed'
            payment_repo.update(payment)
            logger.info(f"Payment {payment.id} marked as completed via webhook")

def _handle_payment_failed(event_data, gateway):
    """Handle payment failed webhook"""
    from app.repositories.payment_repository import PaymentRepository
    payment_repo = PaymentRepository()
    
    gateway_transaction_id = event_data.get('transaction_id') or event_data.get('id')
    if gateway_transaction_id:
        payment = payment_repo.get_by_gateway_transaction_id(gateway_transaction_id)
        if payment:
            payment.status = 'failed'
            payment.failure_reason = event_data.get('error_message', 'Payment failed')
            payment_repo.update(payment)
            logger.info(f"Payment {payment.id} marked as failed via webhook")

def _handle_payment_refunded(event_data, gateway):
    """Handle payment refunded webhook"""
    from app.repositories.payment_repository import PaymentRepository
    payment_repo = PaymentRepository()
    
    gateway_transaction_id = event_data.get('transaction_id') or event_data.get('id')
    if gateway_transaction_id:
        payment = payment_repo.get_by_gateway_transaction_id(gateway_transaction_id)
        if payment:
            payment.status = 'refunded'
            payment_repo.update(payment)
            logger.info(f"Payment {payment.id} marked as refunded via webhook")


