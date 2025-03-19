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

    # Add custom Jinja2 functions to handle modules that might be disabled
    @app.context_processor
    def inject_utility_functions():
        """Add utility functions to Jinja2 context."""
        def url_for_if_exists(endpoint, **values):
            from flask import url_for
            from werkzeug.routing.exceptions import BuildError
            try:
                return url_for(endpoint, **values)
            except BuildError:
                # If the endpoint doesn't exist, return '#' to avoid breaking the template
                app.logger.warning(
                    f'Attempted to generate URL for non-existent endpoint: {endpoint}'
                )
                return '#'
        
        return dict(
            url_for_if_exists=url_for_if_exists,
            is_module_enabled=lambda module: app.config.get(f'ENABLE_{module.upper()}', True)
        )

    # Register blueprints
    from app.modules.time_calculator.routes import time_calculator_bp

    app.register_blueprint(time_calculator_bp)

    # Register file manager blueprint only if enabled
    if app.config.get('ENABLE_FILE_MANAGER', True):
        from app.modules.file_manager.routes import file_manager_bp

        app.register_blueprint(file_manager_bp)
    else:
        app.logger.info('File manager module is disabled for this environment')

    return app
