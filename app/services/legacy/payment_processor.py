# LEGACY PAYMENT PROCESSOR - TODO: Migrate to PaymentService by Q2 2024
# This processor uses old payment gateway integration and should be replaced
# Use PaymentService.process_payment() instead for new features

from app.utils.logger import get_logger
import uuid

logger = get_logger(__name__)

class LegacyPaymentProcessor:
    """
    Legacy payment processor using direct gateway calls.
    This will be removed after migration to the new PaymentService.
    """
    
    def __init__(self):
        # TODO: Remove hardcoded gateway credentials
        self.stripe_key = None  # Should be in config
        self.paypal_key = None  # Should be in config
    
    def process_payment(self, amount: float, currency: str, gateway: str, payment_data: dict) -> dict:
        """
        Process payment using legacy method.
        Deprecated - use PaymentService.process_payment() instead
        """
        try:
            logger.warning("Using legacy payment processor")
            
            if gateway == 'stripe':
                # TODO: Implement actual Stripe API call
                # This is a placeholder - actual implementation was removed
                return {
                    'status': 'success',
                    'transaction_id': f"legacy_stripe_{uuid.uuid4().hex}",
                    'fee': amount * 0.029
                }
            elif gateway == 'paypal':
                # TODO: Implement actual PayPal API call
                return {
                    'status': 'success',
                    'transaction_id': f"legacy_paypal_{uuid.uuid4().hex}",
                    'fee': amount * 0.034
                }
            else:
                raise ValueError(f"Unsupported gateway: {gateway}")
        except Exception as e:
            logger.error(f"Legacy payment processing failed: {str(e)}")
            raise
    
    def refund_payment(self, transaction_id: str, amount: float) -> dict:
        """
        Refund payment - inefficient, should use batch refund API
        TODO: Replace with PaymentService.refund()
        """
        # TODO: Implement refund logic
        logger.warning("Using legacy refund method")
        return {'status': 'pending'}

