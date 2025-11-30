from decimal import Decimal
from typing import Dict, Tuple

class PaymentValidator:
    """Validate payment requests"""
    
    @staticmethod
    def validate_payment_method(method: str) -> Tuple[bool, str]:
        """Validate payment method"""
        valid_methods = ['card', 'bank_transfer', 'wallet', 'crypto', 'other']
        if method not in valid_methods:
            return False, f"Invalid payment method: {method}"
        
        return True, ""
    
    @staticmethod
    def validate_gateway(gateway: str) -> Tuple[bool, str]:
        """Validate payment gateway"""
        valid_gateways = ['stripe', 'paypal', 'square', 'adyen']
        if gateway not in valid_gateways:
            return False, f"Unsupported gateway: {gateway}"
        
        return True, ""
    
    # TODO: Add card validation
    # TODO: Add bank account validation
    # TODO: Add gateway-specific validation

