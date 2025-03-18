"""Cloudinary storage provider implementation.

This module provides classes for interacting with Cloudinary storage service.
"""

from datetime import datetime
import os
from typing import Dict, List, Optional, Tuple, Union

import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename

from ..constants import ALLOWED_IMAGE_EXTENSIONS
from ..constants import ALLOWED_VIDEO_EXTENSIONS
from ..constants import CLOUDINARY_STATUS_CACHE_TTL
from ..storage.base import StorageProvider


class CloudinaryStatus:
    """Class to check and maintain Cloudinary connection status.

    This class handles checking the connection status to Cloudinary and caching the results.
    """

    def __init__(self):
        """Initialize the status checker with default values."""
        self.status = {
            'configured': False,
            'online': False,
            'error': False,
            'error_message': '',
            'last_check': None,
        }
        self.check_status()

    def should_refresh(self) -> bool:
        """Check if status should be refreshed based on cache TTL.

        Returns:
            bool: True if status needs refresh, False otherwise.
        """
        if not self.status['last_check']:
            return True

        elapsed = datetime.now() - self.status['last_check']
        return elapsed.total_seconds() > CLOUDINARY_STATUS_CACHE_TTL

    def check_status(self) -> Dict[str, Union[bool, str]]:
        """Check Cloudinary connection status.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary containing status information.
        """
        self.status['configured'] = all(current_app.config['CLOUDINARY'].values())
        self.status['online'] = False
        self.status['error'] = False
        self.status['error_message'] = ''
        self.status['last_check'] = datetime.now()

        if self.status['configured']:
            try:
                cloudinary.api.ping()
                self.status['online'] = True
            except Exception as e:
                self.status['error'] = True
                self.status['error_message'] = str(e)
                current_app.logger.error(f'Cloudinary connection error: {e}')

        return self.status


class CloudinaryStorage(StorageProvider):
    """Cloudinary storage provider implementation.

    This class implements the StorageProvider interface for Cloudinary storage service.
    """

    def __init__(self):
        """Initialize Cloudinary storage provider with status checker."""
        self.status_checker = CloudinaryStatus()

    def get_resource_type(self, filename: str) -> str:
        """Get Cloudinary resource type based on file extension.

        Args:
            filename (str): Name of the file.

        Returns:
            str: Resource type ('image', 'video', or 'raw').
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext in ALLOWED_IMAGE_EXTENSIONS:
            return 'image'
        elif ext in ALLOWED_VIDEO_EXTENSIONS:
            return 'video'
        return 'raw'

    def list_items(self, path: str) -> List[Dict[str, Union[str, bool, int]]]:
        """List items from Cloudinary storage.

        Args:
            path (str): Path to list items from.

        Returns:
            List[Dict[str, Union[str, bool, int]]]: List of items with their properties.
        """
        items = []
        status = self.status_checker.check_status()

        if not status['configured'] or not status['online']:
            return items

        try:
            # List folders
            folders_result = cloudinary.api.subfolders(path if path and path.strip() else '')

            for folder in folders_result.get('folders', []):
                folder_name = os.path.basename(folder['path'])
                items.append(
                    {
                        'name': folder_name,
                        'is_dir': True,
                        'size': 0,
                        'path': folder['path'],
                    }
                )

            # List files
            result = cloudinary.api.resources(
                # TODO: return all files that match the allowed extensions
                resource_type='raw',
                prefix=path if path else None,
                max_results=500,
            )

            for resource in result.get('resources', []):
                filename = os.path.basename(resource['public_id'])
                items.append(
                    {
                        'name': filename,
                        'is_dir': False,
                        'size': resource.get('bytes', 0),
                        'path': resource['public_id'],
                    }
                )

        except Exception as e:
            current_app.logger.error(f'Error listing Cloudinary items: {e}')
            self.status_checker.status['error'] = True
            self.status_checker.status['error_message'] = str(e)

        return items

    def upload_file(self, file, path: str, filename: str) -> Tuple[bool, Optional[str]]:
        """Upload file to Cloudinary.

        Args:
            file: File object to upload.
            path (str): Path where to upload the file.
            filename (str): Name of the file.

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any.
        """
        try:
            safe_filename = secure_filename(filename)
            upload_path = os.path.join(path, safe_filename) if path else safe_filename
            resource_type = self.get_resource_type(safe_filename)

            result = cloudinary.uploader.upload(
                file, public_id=upload_path, resource_type=resource_type
            )

            current_app.logger.info(f"File uploaded to Cloudinary: {result['url']}")
            return True, None

        except Exception as e:
            error_msg = f'Error uploading to Cloudinary: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def delete_file(self, path: str) -> Tuple[bool, Optional[str]]:
        """Delete file from Cloudinary.

        Args:
            path (str): Path of the file to delete.

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any.
        """
        try:
            resource_type = self.get_resource_type(path)
            cloudinary.uploader.destroy(path, resource_type=resource_type)
            return True, None
        except Exception as e:
            error_msg = f'Error deleting from Cloudinary: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def get_file(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get file URL from Cloudinary.

        Args:
            path (str): Path of the file to retrieve.

        Returns:
            Tuple[Optional[str], Optional[str]]: File URL and error message if any.
        """
        try:
            resource = cloudinary.api.resource(path)
            return resource['url'], None
        except Exception as e:
            error_msg = f'Error getting Cloudinary file: {e}'
            current_app.logger.error(error_msg)
            return None, error_msg

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        """Create a new folder in Cloudinary.

        Args:
            path (str): Path of the folder to create.

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any.
        """
        try:
            cloudinary.api.create_folder(path)
            return True, None
        except Exception as e:
            error_msg = f'Error creating Cloudinary folder: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def get_storage_usage(self) -> Dict[str, Union[int, float]]:
        """Get storage usage information from Cloudinary.

        Returns:
            Dict[str, Union[int, float]]: Dictionary containing storage usage information.
        """
        try:
            usage = cloudinary.api.usage()
            current_app.logger.debug(f'Cloudinary usage response: {usage}')

            # Extract numeric values from nested dictionaries
            storage_used = 0
            storage_limit = 0

            # Get storage usage (in bytes)
            has_storage = (
                'storage' in usage
                and isinstance(usage['storage'], dict)
                and 'usage' in usage['storage']
            )
            if has_storage:
                storage_used = usage['storage']['usage']

            # Get storage limit
            # In the free plan, the limit is based on credits
            if 'credits' in usage and isinstance(usage['credits'], dict):
                if 'limit' in usage['credits']:
                    # Convert credits to bytes (approximately 1 credit = 1GB)
                    storage_limit = usage['credits']['limit'] * 1024 * 1024 * 1024

            # Verify if the values are numbers
            if not isinstance(storage_used, (int, float)):
                msg = f'Cloudinary storage_used is not a number: {storage_used}'
                current_app.logger.warning(msg)
                storage_used = 0

            if not isinstance(storage_limit, (int, float)) or storage_limit <= 0:
                msg = f'Cloudinary storage_limit invalid: {storage_limit}'
                current_app.logger.warning(msg)
                # Set a default value for the free plan (25GB)
                storage_limit = 25 * 1024 * 1024 * 1024

            return {
                'used': storage_used,  # in bytes
                'total': storage_limit,  # in bytes
                'name': 'Cloudinary',
            }
        except Exception as e:
            current_app.logger.error(f'Error getting Cloudinary usage: {e}')
            return {'used': 0, 'total': 1, 'name': 'Cloudinary'}
