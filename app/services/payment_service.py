from app.repositories.payment_repository import PaymentRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.payment import Payment, PaymentMethod
from app.models.transaction import Transaction, TransactionStatus
from app import db
from typing import Dict, Optional
from decimal import Decimal
from app.utils.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

class PaymentService:
    def __init__(self):
        self.payment_repo = PaymentRepository()
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()
    
    def process_payment(self, user_id: str, account_id: str, data: Dict) -> Payment:
        """Process a payment through payment gateway"""
        # Create payment record
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            account_id=account_id,
            payment_method=PaymentMethod(data.get('payment_method', 'card')),
            amount=Decimal(str(data['amount'])),
            currency=data.get('currency', 'USD'),
            status='pending',
            gateway=data.get('gateway', 'stripe'),
            description=data.get('description'),
            metadata=data.get('metadata')
        )
        
        payment = self.payment_repo.create(payment)
        
        try:
            # Process through gateway
            gateway_response = self._process_gateway_payment(payment, data)
            
            payment.gateway_transaction_id = gateway_response.get('transaction_id')
            payment.gateway_response = gateway_response
            
            if gateway_response.get('status') == 'succeeded':
                payment.status = 'completed'
                payment.processed_at = datetime.utcnow()
                
                # Create transaction record
                transaction = self._create_payment_transaction(payment)
            else:
                payment.status = 'failed'
                payment.failure_reason = gateway_response.get('error_message')
            
            payment = self.payment_repo.update(payment)
            
            logger.info(f"Payment processed: {payment.id} status={payment.status}")
            return payment
        except Exception as e:
            payment.status = 'failed'
            payment.failure_reason = str(e)
            self.payment_repo.update(payment)
            logger.error(f"Payment processing failed: {payment.id} error={str(e)}")
            raise
    
    def _process_gateway_payment(self, payment: Payment, data: Dict) -> Dict:
        """Process payment through external gateway"""
        # TODO: Implement actual gateway integration
        # This is a placeholder - should integrate with Stripe, PayPal, etc.
        
        if payment.gateway == 'stripe':
            # TODO: Call Stripe API
            return {
                'status': 'succeeded',
                'transaction_id': f"stripe_{uuid.uuid4().hex}",
                'fee': float(payment.amount) * 0.029 + 0.30  # Stripe fee
            }
        elif payment.gateway == 'paypal':
            # TODO: Call PayPal API
            return {
                'status': 'succeeded',
                'transaction_id': f"paypal_{uuid.uuid4().hex}",
                'fee': float(payment.amount) * 0.034
            }
        else:
            raise ValueError(f"Unsupported gateway: {payment.gateway}")
    
    def _create_payment_transaction(self, payment: Payment) -> Transaction:
        """Create transaction record for completed payment"""
        transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=payment.account_id,
            user_id=payment.user_id,
            transaction_type='deposit',
            amount=payment.amount,
            currency=payment.currency,
            fee=Decimal('0.00'),  # Fee already included in gateway response
            net_amount=payment.amount,
            description=payment.description,
            reference_id=f"PAY-{payment.id}",
            external_reference=payment.gateway_transaction_id,
            payment_id=payment.id,
            status=TransactionStatus.COMPLETED,
            processed_at=datetime.utcnow(),
            metadata=payment.metadata
        )
        
        transaction = self.transaction_repo.create(transaction)
        return transaction
    
    # TODO: Add payment refund
    # TODO: Add payment cancellation
    # TODO: Add webhook handling for gateway callbacks

