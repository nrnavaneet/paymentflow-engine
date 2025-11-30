from flask import request, g
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)

def setup_logging(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        logger.info(f"Response: {request.method} {request.path} - {response.status_code} ({duration:.3f}s)")
        return response

