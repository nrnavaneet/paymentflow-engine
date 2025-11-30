from typing import Dict, Tuple

class ComplianceValidator:
    """Validate compliance-related data"""
    
    @staticmethod
    def validate_kyc_document(document_type: str) -> Tuple[bool, str]:
        """Validate KYC document type"""
        valid_types = ['passport', 'id_card', 'driver_license', 'utility_bill']
        if document_type not in valid_types:
            return False, f"Invalid document type: {document_type}"
        
        return True, ""
    
    # TODO: Add document number validation
    # TODO: Add document image validation
    # TODO: Add selfie validation


