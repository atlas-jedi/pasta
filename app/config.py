import os


class Config:
    """Configuration class for the application."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Feature flags
    ENABLE_FILE_MANAGER = os.environ.get('ENABLE_FILE_MANAGER', 'true').lower() == 'true'

    # Environment settings
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')
    IS_HOMOLOGATION = ENVIRONMENT == 'homologation'

    # If we're in homologation environment, disable file manager by default
    if IS_HOMOLOGATION:
        ENABLE_FILE_MANAGER = os.environ.get('ENABLE_FILE_MANAGER', 'false').lower() == 'true'

    # Cloudinary configuration
    CLOUDINARY = {
        'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.environ.get('CLOUDINARY_API_KEY'),
        'api_secret': os.environ.get('CLOUDINARY_API_SECRET'),
    }
