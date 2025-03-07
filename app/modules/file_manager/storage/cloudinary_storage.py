"""Cloudinary storage provider implementation."""
from datetime import datetime
import os
from typing import Dict, List, Optional, Tuple, Union

import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename

from ..constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    CLOUDINARY_STATUS_CACHE_TTL
)
from ..storage.base import StorageProvider


class CloudinaryStatus:
    """Cloudinary connection status with caching."""
    def __init__(self):
        """Initialize Cloudinary connection status with default values for caching.

        Sets up the initial state of the status dictionary containing:
        - 'configured': False (Cloudinary credentials not verified yet)
        - 'online': False (connection status unknown)
        - 'error': False (no errors initially)
        - 'error_message': Empty string (no error details)
        - 'last_check': None (no previous status check performed)

        The status will be populated with actual values after the first check_status() call.
        """
        self.status = {
            'configured': False,
            'online': False,
            'error': False,
            'error_message': '',
            'last_check': None
        }

    def should_refresh(self) -> bool:
        """Check if status should be refreshed."""
        if not self.status['last_check']:
            return True

        elapsed = datetime.now() - self.status['last_check']
        return elapsed.total_seconds() > CLOUDINARY_STATUS_CACHE_TTL

    def check_status(self) -> Dict[str, Union[bool, str]]:
        """Check Cloudinary connection status with caching."""
        if not self.should_refresh():
            return self.status

        self.status['configured'] = all(current_app.config['CLOUDINARY'].values())
        self.status['online'] = False
        self.status['error'] = False
        self.status['error_message'] = ''
        self.status['last_check'] = datetime.now()

        if self.status['configured']:
            try:
                cloudinary.api.resources(max_results=1)
                self.status['online'] = True
            except Exception as e:
                self.status['error'] = True
                self.status['error_message'] = str(e)
                current_app.logger.error(f'Cloudinary connection error: {e}')

        return self.status


class CloudinaryStorage(StorageProvider):
    """Cloudinary storage provider implementation."""

    def __init__(self):
        """Initialize Cloudinary storage."""
        self.status_checker = CloudinaryStatus()

    def get_resource_type(self, filename: str) -> str:
        """Get Cloudinary resource type based on file extension."""
        ext = os.path.splitext(filename)[1].lower()

        if ext in ALLOWED_IMAGE_EXTENSIONS:
            return 'image'
        elif ext in ALLOWED_VIDEO_EXTENSIONS:
            return 'video'
        return 'raw'

    def list_items(self, path: str) -> List[Dict[str, Union[str, bool, int]]]:
        """List items from Cloudinary storage."""
        items = []
        status = self.status_checker.check_status()

        if not status['configured'] or not status['online']:
            return items

        try:
            # List files
            result = cloudinary.api.resources(
                type='upload',
                prefix=path if path else None,
                max_results=500
            )

            for resource in result.get('resources', []):
                filename = os.path.basename(resource['public_id'])
                items.append({
                    'name': filename,
                    'is_dir': False,
                    'size': resource.get('bytes', 0),
                    'path': resource['public_id'],
                })

            # List folders
            folders_result = cloudinary.api.subfolders(
                path if path and path.strip() else ''
            )

            for folder in folders_result.get('folders', []):
                folder_name = os.path.basename(folder['path'])
                items.append({
                    'name': folder_name,
                    'is_dir': True,
                    'size': 0,
                    'path': folder['path'],
                })

        except Exception as e:
            current_app.logger.error(f'Error listing Cloudinary items: {e}')
            self.status_checker.status['error'] = True
            self.status_checker.status['error_message'] = str(e)

        return items

    def upload_file(self, file, path: str, filename: str) -> Tuple[bool, Optional[str]]:
        """Upload file to Cloudinary."""
        try:
            safe_filename = secure_filename(filename)
            upload_path = os.path.join(path, safe_filename) if path else safe_filename
            resource_type = self.get_resource_type(safe_filename)

            result = cloudinary.uploader.upload(
                file,
                public_id=upload_path,
                resource_type=resource_type
            )

            current_app.logger.info(f'File uploaded to Cloudinary: {result["url"]}')
            return True, None

        except Exception as e:
            error_msg = f'Error uploading to Cloudinary: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def delete_file(self, path: str) -> Tuple[bool, Optional[str]]:
        """Delete file from Cloudinary."""
        try:
            resource_type = self.get_resource_type(path)
            cloudinary.uploader.destroy(path, resource_type=resource_type)
            return True, None
        except Exception as e:
            error_msg = f'Error deleting from Cloudinary: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def get_file(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get file URL from Cloudinary."""
        try:
            resource = cloudinary.api.resource(path)
            return resource['url'], None
        except Exception as e:
            error_msg = f'Error getting Cloudinary file: {e}'
            current_app.logger.error(error_msg)
            return None, error_msg

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        """Create folder in Cloudinary."""
        try:
            cloudinary.api.create_folder(path)
            return True, None
        except Exception as e:
            error_msg = f'Error creating Cloudinary folder: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg
