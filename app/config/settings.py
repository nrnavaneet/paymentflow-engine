import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Payment processing
    MAX_TRANSACTION_AMOUNT = float(os.environ.get('MAX_TRANSACTION_AMOUNT', '1000000'))
    MIN_TRANSACTION_AMOUNT = float(os.environ.get('MIN_TRANSACTION_AMOUNT', '0.01'))
    DEFAULT_CURRENCY = os.environ.get('DEFAULT_CURRENCY', 'USD')
    SUPPORTED_CURRENCIES = os.environ.get('SUPPORTED_CURRENCIES', 'USD,EUR,GBP,JPY').split(',')
    
    # Fraud detection
    FRAUD_DETECTION_ENABLED = os.environ.get('FRAUD_DETECTION_ENABLED', 'true').lower() == 'true'
    FRAUD_RISK_THRESHOLD = float(os.environ.get('FRAUD_RISK_THRESHOLD', '0.7'))
    
    # Compliance
    AML_CHECK_ENABLED = os.environ.get('AML_CHECK_ENABLED', 'true').lower() == 'true'
    KYC_REQUIRED_AMOUNT = float(os.environ.get('KYC_REQUIRED_AMOUNT', '10000'))
    
    # Settlement
    SETTLEMENT_BATCH_SIZE = int(os.environ.get('SETTLEMENT_BATCH_SIZE', '100'))
    SETTLEMENT_INTERVAL_HOURS = int(os.environ.get('SETTLEMENT_INTERVAL_HOURS', '24'))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:pass@localhost/paymentflow_dev'
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:pass@localhost/paymentflow'
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


