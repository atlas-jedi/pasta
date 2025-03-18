from io import BytesIO

import cloudinary
import cloudinary.api
import cloudinary.uploader
import pytest


def test_cloudinary_config(app):
    """Tests if Cloudinary is configured correctly."""
    assert app.config['CLOUDINARY']['cloud_name'] is not None
    assert app.config['CLOUDINARY']['api_key'] is not None
    assert app.config['CLOUDINARY']['api_secret'] is not None


def test_cloudinary_connection():
    """Tests if it's possible to connect to Cloudinary."""
    try:
        result = cloudinary.api.resources(max_results=1)
        assert isinstance(result, dict)
        assert 'resources' in result
    except Exception as e:
        pytest.fail(f'Failed to connect to Cloudinary: {str(e)}')


def test_upload_file(client):
    """Tests uploading a file to Cloudinary."""
    data = {'file': (BytesIO(b'test file content'), 'test.txt'), 'path': ''}

    # Upload the file
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 302

    # Verify if the file exists in Cloudinary
    try:
        resources = cloudinary.api.resources(resource_type='raw')
        found = any(r['public_id'] == 'test.txt' for r in resources.get('resources', []))
        assert found, 'File not found in Cloudinary'
    finally:
        try:
            cloudinary.uploader.destroy('test.txt', resource_type='raw')
        except cloudinary.api.NotFound:
            pass


def test_create_folder():
    """Tests creating a folder in Cloudinary."""
    folder_name = 'test_folder'

    try:
        # Create a folder
        result = cloudinary.api.create_folder(folder_name)
        assert result['success'] is True

        # Verify if the folder exists
        folders = cloudinary.api.root_folders()
        found = any(folder['name'] == folder_name for folder in folders.get('folders', []))
        assert found, 'Folder not found in Cloudinary'
    finally:
        try:
            cloudinary.api.delete_folder(folder_name)
        except Exception:
            pass


# def test_download_file(client, app):
#     """Tests downloading a file from Cloudinary"""
#     # Upload a test file
#     test_content = b'test file content'
#     test_file = BytesIO(test_content)
#     result = cloudinary.uploader.upload(
#         test_file,
#         public_id='test_download.txt',
#         resource_type='raw'
#     )

#     try:
#         # Try to download the file
#         response = client.get(f'/download/test_download.txt')
#         assert response.status_code == 302  # Redirect to Cloudinary URL
#     finally:
#         # Clean up test file
#         try:
#             cloudinary.uploader.destroy('test_download.txt')
#         except:
#             pass
