#!/usr/bin/env python3
"""
Application runner for BOM Comparison Tool
"""

from app import app
from config import Config

if __name__ == '__main__':
    # Initialize configuration
    Config.init_app(app)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    ) 