from app.repositories.fraud_repository import FraudRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.models.fraud import FraudCheck, RiskScore
from app.models.transaction import Transaction
from app import db
from typing import Dict, Optional
from app.utils.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

class FraudService:
    def __init__(self):
        self.fraud_repo = FraudRepository()
        self.transaction_repo = TransactionRepository()
        self.user_repo = UserRepository()
    
    def check_transaction(self, transaction: Transaction, request_data: Dict) -> FraudCheck:
        """Perform comprehensive fraud check on transaction"""
        # Calculate risk score
        risk_score = self._calculate_risk_score(transaction, request_data)
        risk_level = self._determine_risk_level(risk_score)
        
        # Check fraud rules
        rules_triggered = self._check_fraud_rules(transaction, request_data)
        
        fraud_check = FraudCheck(
            id=str(uuid.uuid4()),
            transaction_id=transaction.id,
            user_id=transaction.user_id,
            risk_score=risk_score,
            risk_level=risk_level,
            rules_triggered=rules_triggered,
            device_fingerprint=request_data.get('device_fingerprint'),
            ip_address=request_data.get('ip_address'),
            user_agent=request_data.get('user_agent'),
            geolocation=request_data.get('geolocation'),
            velocity_checks=self._check_velocity(transaction),
            pattern_analysis=self._analyze_patterns(transaction),
            status='pending' if risk_level in ['high', 'critical'] else 'approved'
        )
        
        fraud_check = self.fraud_repo.create(fraud_check)
        
        # Update user risk score
        self._update_user_risk_score(transaction.user_id)
        
        logger.info(f"Fraud check completed: {fraud_check.id} risk={risk_score}")
        return fraud_check
    
    def _calculate_risk_score(self, transaction: Transaction, request_data: Dict) -> float:
        """Calculate overall risk score (0.0 to 1.0)"""
        scores = []
        
        # Account age score
        user = self.user_repo.get_by_id(transaction.user_id)
        if user:
            account_age_days = (datetime.utcnow() - user.created_at).days
            age_score = min(account_age_days / 365, 1.0)  # Normalize to 0-1
            scores.append(1.0 - age_score)  # Older accounts = lower risk
        
        # Transaction history score
        summary = self.transaction_repo.get_user_transaction_summary(transaction.user_id, 30)
        history_score = min(summary['total_count'] / 100, 1.0)  # More history = lower risk
        scores.append(1.0 - history_score)
        
        # Amount score
        amount_score = min(float(transaction.amount) / 10000, 1.0)  # Larger amounts = higher risk
        scores.append(amount_score)
        
        # Velocity score
        velocity_data = self._check_velocity(transaction)
        velocity_score = velocity_data.get('risk_score', 0.5)
        scores.append(velocity_score)
        
        # Device score (if available)
        device_score = 0.5  # Default
        if request_data.get('device_fingerprint'):
            # TODO: Check device reputation
            device_score = 0.3
        scores.append(device_score)
        
        # Location score
        location_score = 0.5  # Default
        if request_data.get('geolocation'):
            # TODO: Check location against user history
            location_score = 0.4
        scores.append(location_score)
        
        # KYC score
        kyc_score = 0.8  # Default (no KYC = high risk)
        if user and user.kyc_status == 'verified':
            kyc_score = 0.1
        scores.append(kyc_score)
        
        # Weighted average
        weights = [0.1, 0.15, 0.2, 0.2, 0.1, 0.1, 0.15]
        weighted_score = sum(s * w for s, w in zip(scores, weights))
        
        return min(weighted_score, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        from app.config.settings import config
        threshold = config.FRAUD_RISK_THRESHOLD
        
        if risk_score >= threshold:
            return 'critical'
        elif risk_score >= threshold * 0.7:
            return 'high'
        elif risk_score >= threshold * 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _check_fraud_rules(self, transaction: Transaction, request_data: Dict) -> list:
        """Check transaction against fraud rules"""
        rules_triggered = []
        
        # Rule 1: Large amount
        if float(transaction.amount) > 10000:
            rules_triggered.append('large_amount')
        
        # Rule 2: Unusual time
        hour = datetime.utcnow().hour
        if hour < 6 or hour > 22:
            rules_triggered.append('unusual_time')
        
        # Rule 3: New device
        if not request_data.get('device_fingerprint'):
            rules_triggered.append('new_device')
        
        # Rule 4: Velocity check
        velocity = self._check_velocity(transaction)
        if velocity.get('exceeds_limit', False):
            rules_triggered.append('high_velocity')
        
        # TODO: Add more fraud rules
        # TODO: Make rules configurable
        
        return rules_triggered
    
    def _check_velocity(self, transaction: Transaction) -> Dict:
        """Check transaction velocity (frequency and amount)"""
        summary = self.transaction_repo.get_user_transaction_summary(transaction.user_id, 1)  # Last 24 hours
        
        velocity_risk = 0.0
        exceeds_limit = False
        
        if summary['total_count'] > 10:
            velocity_risk = 0.8
            exceeds_limit = True
        elif summary['total_count'] > 5:
            velocity_risk = 0.5
        
        return {
            'transaction_count_24h': summary['total_count'],
            'total_amount_24h': summary['total_amount'],
            'risk_score': velocity_risk,
            'exceeds_limit': exceeds_limit
        }
    
    def _analyze_patterns(self, transaction: Transaction) -> Dict:
        """Analyze behavioral patterns"""
        # TODO: Implement pattern analysis
        # - Compare to user's typical transaction patterns
        # - Check for anomalies
        return {
            'pattern_match': 0.7,
            'anomalies': []
        }
    
    def _update_user_risk_score(self, user_id: str):
        """Update user's overall risk score"""
        # TODO: Implement comprehensive risk score calculation
        # TODO: Store in RiskScore table
        pass
    
    # TODO: Add machine learning-based fraud detection
    # TODO: Add real-time fraud rule updates
    # TODO: Add fraud pattern learning


