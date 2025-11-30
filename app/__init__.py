from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    from app.config.settings import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.accounts import accounts_bp
    from app.routes.transactions import transactions_bp
    from app.routes.payments import payments_bp
    from app.routes.settlements import settlements_bp
    from app.routes.reports import reports_bp
    from app.routes.webhooks import webhooks_bp
    from app.routes.compliance import compliance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(accounts_bp, url_prefix='/api/accounts')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(settlements_bp, url_prefix='/api/settlements')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    
    # Register error handlers
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Register middleware
    from app.middleware.logging_middleware import setup_logging
    setup_logging(app)
    
    # Register security middleware
    from app.middleware.security_middleware import setup_security
    setup_security(app)
    
    # Initialize logging
    from app.utils.logger import setup_app_logger
    setup_app_logger(app)
    
    return app

