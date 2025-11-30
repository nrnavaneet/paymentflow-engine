from app.repositories.transaction_repository import TransactionRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.fraud_repository import FraudRepository
from app.repositories.compliance_repository import ComplianceRepository
from app.services.fraud_service import FraudService
from app.services.compliance_service import ComplianceService
from app.models.transaction import Transaction, TransactionStatus
from app.models.audit_log import AuditLog
from app import db
from typing import Optional, Dict
from decimal import Decimal
from app.utils.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.fraud_repo = FraudRepository()
        self.compliance_repo = ComplianceRepository()
        self.fraud_service = FraudService()
        self.compliance_service = ComplianceService()
    
    def create_transaction(self, account_id: str, user_id: str, data: Dict) -> Transaction:
        """Create a new transaction with fraud and compliance checks"""
        # Validate account
        account = self.account_repo.get_by_id(account_id)
        if not account or account.user_id != user_id:
            raise ValueError("Invalid account")
        
        if account.status != 'active':
            raise ValueError("Account is not active")
        
        # Create transaction
        amount = Decimal(str(data['amount']))
        fee = self._calculate_fee(amount, data.get('transaction_type', 'transfer'))
        net_amount = amount - fee
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=account_id,
            user_id=user_id,
            transaction_type=data['transaction_type'],
            amount=amount,
            currency=data.get('currency', 'USD'),
            fee=fee,
            net_amount=net_amount,
            description=data.get('description'),
            reference_id=data.get('reference_id') or f"TXN-{uuid.uuid4().hex[:12].upper()}",
            external_reference=data.get('external_reference'),
            status=TransactionStatus.PENDING,
            metadata=data.get('metadata')
        )
        
        try:
            # Run fraud check
            fraud_check = self._run_fraud_check(transaction)
            if fraud_check:
                transaction.fraud_check_id = fraud_check.id
                if fraud_check.risk_level in ['high', 'critical']:
                    transaction.status = TransactionStatus.PENDING
                    # TODO: Add manual review queue
            
            # Run compliance check
            if self._requires_compliance_check(amount):
                compliance_check = self._run_compliance_check(transaction)
                if compliance_check:
                    transaction.compliance_check_id = compliance_check.id
                    if compliance_check.status == 'failed':
                        transaction.status = TransactionStatus.FAILED
                        transaction.error_message = "Compliance check failed"
            
            # Process transaction if checks pass
            if transaction.status == TransactionStatus.PENDING:
                transaction = self._process_transaction(transaction, data)
            
            transaction = self.transaction_repo.create(transaction)
            
            # Log audit trail
            self._log_audit(user_id, 'create', 'transaction', transaction.id, {
                'amount': float(amount),
                'currency': transaction.currency,
                'type': transaction.transaction_type
            })
            
            logger.info(f"Transaction created: {transaction.id}")
            return transaction
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            db.session.rollback()
            raise
    
    def _process_transaction(self, transaction: Transaction, data: Dict) -> Transaction:
        """Process the actual transaction (balance updates, etc.)"""
        if transaction.transaction_type in ['deposit', 'transfer']:
            # Update wallet balances
            source_wallet_id = data.get('source_wallet_id')
            destination_wallet_id = data.get('destination_wallet_id')
            
            if source_wallet_id:
                source_wallet = self.account_repo.get_wallet(
                    transaction.account_id,
                    'main',
                    transaction.currency
                )
                if source_wallet and source_wallet.available_balance >= transaction.amount:
                    source_wallet.available_balance -= transaction.amount
                    source_wallet.balance -= transaction.amount
                    transaction.source_wallet_id = source_wallet_id
            
            if destination_wallet_id:
                destination_wallet = self.account_repo.get_wallet(
                    data.get('destination_account_id', transaction.account_id),
                    'main',
                    transaction.currency
                )
                if destination_wallet:
                    destination_wallet.available_balance += transaction.net_amount
                    destination_wallet.balance += transaction.net_amount
                    transaction.destination_wallet_id = destination_wallet_id
            
            transaction.status = TransactionStatus.COMPLETED
            transaction.processed_at = datetime.utcnow()
        elif transaction.transaction_type == 'withdrawal':
            # For withdrawals, check balance and freeze amount
            source_wallet = self.account_repo.get_wallet(
                transaction.account_id,
                'main',
                transaction.currency
            )
            if source_wallet and source_wallet.available_balance >= transaction.amount:
                source_wallet.available_balance -= transaction.amount
                source_wallet.frozen_balance += transaction.amount
                transaction.source_wallet_id = source_wallet.id
                transaction.status = TransactionStatus.PROCESSING
            else:
                transaction.status = TransactionStatus.FAILED
                transaction.error_message = "Insufficient balance"
        elif transaction.transaction_type == 'payment':
            # Payments are handled by PaymentService
            transaction.status = TransactionStatus.PROCESSING
        else:
            transaction.status = TransactionStatus.PROCESSING
        
        return transaction
    
    def _calculate_fee(self, amount: Decimal, transaction_type: str) -> Decimal:
        """Calculate transaction fee"""
        # TODO: Implement proper fee calculation based on account type, transaction type, etc.
        if transaction_type == 'transfer':
            return amount * Decimal('0.01')  # 1% fee
        return Decimal('0.00')
    
    def _run_fraud_check(self, transaction: Transaction):
        """Run fraud detection check"""
        try:
            request_data = {
                'ip_address': transaction.metadata.get('ip_address') if transaction.metadata else None,
                'device_fingerprint': transaction.metadata.get('device_fingerprint') if transaction.metadata else None,
                'user_agent': transaction.metadata.get('user_agent') if transaction.metadata else None,
                'geolocation': transaction.metadata.get('geolocation') if transaction.metadata else None
            }
            fraud_check = self.fraud_service.check_transaction(transaction, request_data)
            return fraud_check
        except Exception as e:
            logger.error(f"Fraud check failed: {str(e)}")
            return None
    
    def _run_compliance_check(self, transaction: Transaction):
        """Run compliance check (AML, KYC, etc.)"""
        try:
            compliance_check = self.compliance_service.check_transaction(transaction)
            return compliance_check
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            return None
    
    def _requires_compliance_check(self, amount: Decimal) -> bool:
        """Check if transaction requires compliance review"""
        from app.config.settings import config
        return float(amount) >= config.KYC_REQUIRED_AMOUNT
    
    def _log_audit(self, user_id: str, action: str, entity_type: str, entity_id: str, changes: Dict):
        """Log audit trail"""
        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id
        )
        log.set_changes(changes)
        db.session.add(log)
        db.session.commit()
    
    # TODO: Add transaction reversal
    # TODO: Add transaction refund
    # TODO: Add transaction cancellation


