"""Local filesystem storage provider."""
import os
import shutil
from typing import Dict, List, Optional, Tuple, Union

from flask import current_app, send_from_directory
from werkzeug.utils import secure_filename

from ..storage.base import StorageProvider


class LocalStorage(StorageProvider):
    """Local filesystem storage provider implementation."""

    def __init__(self, base_path: str):
        """Initialize local storage.

        Args:
            base_path: Base path for local storage
        """
        self.base_path = base_path

    def _get_full_path(self, path: str) -> str:
        """Get full filesystem path.

        Args:
            path: Relative path

        Returns:
            Full filesystem path
        """
        return os.path.join(self.base_path, path)

    def list_items(self, path: str) -> List[Dict[str, Union[str, bool, int]]]:
        """List items in the given path."""
        items = []
        full_path = self._get_full_path(path)

        try:
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                items.append({
                    'name': item,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if not os.path.isdir(item_path) else 0,
                    'path': os.path.join(path, item),
                })
            return items
        except Exception as e:
            current_app.logger.error(f'Error listing local files: {e}')
            return []

    def upload_file(self, file, path: str, filename: str) -> Tuple[bool, Optional[str]]:
        """Upload a file to local storage."""
        try:
            target_dir = self._get_full_path(path)
            os.makedirs(target_dir, exist_ok=True)

            safe_filename = secure_filename(filename)
            file_path = os.path.join(target_dir, safe_filename)
            file.save(file_path)

            return True, None
        except Exception as e:
            error_msg = f'Error uploading file locally: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def delete_file(self, path: str) -> Tuple[bool, Optional[str]]:
        """Delete a file from local storage."""
        try:
            full_path = self._get_full_path(path)
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                os.rmdir(full_path)
            return True, None
        except Exception as e:
            error_msg = f'Error deleting file locally: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def get_file(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get a file from local storage."""
        try:
            directory = os.path.dirname(self._get_full_path(path))
            filename = os.path.basename(path)
            return send_from_directory(directory, filename, as_attachment=True), None
        except Exception as e:
            error_msg = f'Error getting local file: {e}'
            current_app.logger.error(error_msg)
            return None, error_msg

    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        """Create a folder in local storage."""
        try:
            full_path = self._get_full_path(path)
            os.makedirs(full_path, exist_ok=True)
            return True, None
        except Exception as e:
            error_msg = f'Error creating local folder: {e}'
            current_app.logger.error(error_msg)
            return False, error_msg

    def get_storage_usage(self) -> Dict[str, Union[int, float]]:
        """Get storage usage information from local filesystem."""
        try:
            total_size = 0
            for dirpath, _, filenames in os.walk(self.base_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)

            # Get disk usage information
            disk_total, disk_used, disk_free = shutil.disk_usage(self.base_path)

            current_app.logger.debug(
                f'Local storage usage: total_size={total_size}, disk_total={disk_total}'
            )

            # Ensure the values are numbers
            if not isinstance(total_size, (int, float)):
                current_app.logger.warning(f'Local total_size is not a number: {total_size}')
                total_size = 0

            if not isinstance(disk_total, (int, float)):
                current_app.logger.warning(f'Local disk_total is not a number: {disk_total}')
                disk_total = 1  # Avoid division by zero

            return {
                'used': total_size,  # actual usage of upload folder
                'total': disk_total,  # total disk space
                'name': 'Local Storage'
            }
        except Exception as e:
            current_app.logger.error(f'Error getting local storage usage: {e}')
            return {
                'used': 0,
                'total': 1,
                'name': 'Local Storage'
            }
