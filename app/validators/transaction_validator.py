from decimal import Decimal
from app.config.settings import config
from typing import Dict, Tuple

class TransactionValidator:
    """Validate transaction requests"""
    
    @staticmethod
    def validate_amount(amount: Decimal) -> Tuple[bool, str]:
        """Validate transaction amount"""
        if amount <= 0:
            return False, "Amount must be greater than zero"
        
        if amount < config.MIN_TRANSACTION_AMOUNT:
            return False, f"Amount must be at least {config.MIN_TRANSACTION_AMOUNT}"
        
        if amount > config.MAX_TRANSACTION_AMOUNT:
            return False, f"Amount exceeds maximum transaction limit of {config.MAX_TRANSACTION_AMOUNT}"
        
        return True, ""
    
    @staticmethod
    def validate_currency(currency: str) -> Tuple[bool, str]:
        """Validate currency code"""
        if currency not in config.SUPPORTED_CURRENCIES:
            return False, f"Currency {currency} is not supported"
        
        return True, ""
    
    @staticmethod
    def validate_transaction_type(transaction_type: str) -> Tuple[bool, str]:
        """Validate transaction type"""
        valid_types = ['deposit', 'withdrawal', 'transfer', 'payment', 'refund']
        if transaction_type not in valid_types:
            return False, f"Invalid transaction type: {transaction_type}"
        
        return True, ""
    
    # TODO: Add more validation rules
    # TODO: Add account balance validation
    # TODO: Add daily transaction limit validation

