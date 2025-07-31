import os
from datetime import timedelta

class Config:
    """Configuration for BOM Comparison Tool"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'data/temp'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    
    # Comparison settings
    MAX_COMPARISON_ROWS = 10000
    TEMP_FILE_RETENTION_HOURS = 24
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create necessary directories
        os.makedirs('data/temp', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('instance', exist_ok=True) 