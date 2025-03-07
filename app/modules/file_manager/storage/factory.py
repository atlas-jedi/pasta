"""Storage provider factory."""
from flask import current_app

from .base import StorageProvider
from .cloudinary_storage import CloudinaryStorage
from .local import LocalStorage


def get_storage_provider() -> StorageProvider:
    """Get appropriate storage provider based on configuration.

    Returns:
        StorageProvider: Configured storage provider instance
    """
    cloudinary_config = current_app.config.get('CLOUDINARY', {})

    # Try Cloudinary first
    if all(cloudinary_config.values()):
        provider = CloudinaryStorage()
        status = provider.status_checker.check_status()

        # If Cloudinary is configured and online, use it
        if status['configured'] and status['online'] and not status['error']:
            return provider

    # Fallback to local storage
    return LocalStorage(current_app.config['UPLOAD_FOLDER'])
