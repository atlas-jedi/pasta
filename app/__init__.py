import os

import cloudinary
from flask import Flask

from .config import Config


def create_app(test_config=None):
    """Create and configure the Flask application instance.

    Args:
        test_config: Configuration dictionary for testing (optional).

    Returns:
        Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Load default configuration
    app.config.from_object(Config)

    if test_config is None:
        # Load instance configuration, if exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test configuration
        app.config.from_mapping(test_config)

    # Ensure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Configure Cloudinary
    if all(app.config['CLOUDINARY'].values()):
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY']['cloud_name'],
            api_key=app.config['CLOUDINARY']['api_key'],
            api_secret=app.config['CLOUDINARY']['api_secret'],
        )

    # Register blueprints
    from app.modules.file_manager.routes import file_manager_bp
    from app.modules.time_calculator.routes import time_calculator_bp

    app.register_blueprint(file_manager_bp)
    app.register_blueprint(time_calculator_bp)

    return app
