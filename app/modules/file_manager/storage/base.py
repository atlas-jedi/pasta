"""Base storage provider interface."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union


class StorageProvider(ABC):
    """Abstract base class for storage providers."""

    @abstractmethod
    def list_items(self, path: str) -> List[Dict[str, Union[str, bool, int]]]:
        """List items in the given path.

        Args:
            path: The path to list items from

        Returns:
            List of items with their properties
        """
        pass

    @abstractmethod
    def upload_file(self, file, path: str, filename: str) -> Tuple[bool, Optional[str]]:
        """Upload a file to storage.

        Args:
            file: The file object to upload
            path: The path to upload to
            filename: The name of the file

        Returns:
            Tuple of (success, error_message)
        """
        pass

    @abstractmethod
    def delete_file(self, path: str) -> Tuple[bool, Optional[str]]:
        """Delete a file from storage.

        Args:
            path: The path of the file to delete

        Returns:
            Tuple of (success, error_message)
        """
        pass

    @abstractmethod
    def get_file(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get a file from storage.

        Args:
            path: The path of the file to get

        Returns:
            Tuple of (file_url, error_message)
        """
        pass

    @abstractmethod
    def create_folder(self, path: str) -> Tuple[bool, Optional[str]]:
        """Create a folder in storage.

        Args:
            path: The path of the folder to create

        Returns:
            Tuple of (success, error_message)
        """
        pass
