"""File manager routes module."""

import os

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename

from .storage.factory import get_storage_provider

file_manager_bp = Blueprint(
    'file_manager', __name__, template_folder='templates', static_folder='static', url_prefix='/'
)


@file_manager_bp.route('/')
def index():
    """List files and directories at the given path."""
    path = request.args.get('path', '')

    # Get the current storage
    storage = get_storage_provider()
    items = storage.list_items(path)

    # List to store information from all storages
    all_storages = []

    # Get information from the current storage
    try:
        storage_usage = storage.get_storage_usage()

        # Check if the values are nested dictionaries or direct values
        used = storage_usage.get('used', 0)
        total = storage_usage.get('total', 1)
        name = storage_usage.get('name', 'Storage')

        # If 'used' or 'total' are dictionaries, try to extract numeric values
        if isinstance(used, dict):
            current_app.logger.debug(f'"used" is a dictionary: {used}')
            used = 0  # safe default value

        if isinstance(total, dict):
            current_app.logger.debug(f'"total" is a dictionary: {total}')
            total = 1  # safe default value

        # Ensure the values are numbers
        current_storage = {
            'used': float(used),
            'total': max(float(total), 1),  # Avoid division by zero
            'name': str(name),
            'is_active': True,  # Indicates this is the current storage
        }

        all_storages.append(current_storage)

    except Exception as e:
        current_app.logger.error(f'Error getting storage usage: {e}')
        current_storage = {'used': 0, 'total': 1, 'name': 'Error Storage', 'is_active': True}
        all_storages.append(current_storage)

    # In the future, you can add other storages to the all_storages list here
    # Example:
    # try:
    #     other_storage = get_other_storage_provider()
    #     other_storage_usage = other_storage.get_storage_usage()
    #     all_storages.append({
    #         'used': float(other_storage_usage.get('used', 0)),
    #         'total': max(float(other_storage_usage.get('total', 1)), 1),
    #         'name': str(other_storage_usage.get('name', 'Other Storage')),
    #         'is_active': False
    #     })
    # except Exception as e:
    #     current_app.logger.error(f'Error getting other storage usage: {e}')

    # Get Cloudinary status from storage if it's CloudinaryStorage
    cloudinary_status = getattr(storage, 'status_checker', None)
    if cloudinary_status:
        cloudinary_status = cloudinary_status.check_status()
    else:
        cloudinary_status = {'configured': False, 'online': False, 'error': False}

    return render_template(
        'index.html',
        items=items,
        current_path=path,
        cloudinary_status=cloudinary_status,
        storage_usage=current_storage,  # Maintains compatibility with the current template
        all_storages=all_storages,  # New variable for multiple storages
    )


@file_manager_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    path = request.form.get('path', '')

    if 'file' not in request.files:
        return redirect(url_for('file_manager.index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('file_manager.index'))

    filename = secure_filename(file.filename)
    storage = get_storage_provider()

    success, error = storage.upload_file(file, path, filename)
    if not success:
        current_app.logger.error(f'Upload failed: {error}')
        # You might want to flash the error message here

    return redirect(url_for('file_manager.index', path=path))


@file_manager_bp.route('/delete/<path:filename>')
def delete_file(filename):
    """Delete a file."""
    storage = get_storage_provider()
    success, error = storage.delete_file(filename)

    if not success:
        current_app.logger.error(f'Delete failed: {error}')
        # You might want to flash the error message here

    return redirect(url_for('file_manager.index', path=os.path.dirname(filename)))


@file_manager_bp.route('/download/<path:filename>')
def download_file(filename):
    """Download a file."""
    storage = get_storage_provider()
    file_url, error = storage.get_file(filename)

    if error:
        current_app.logger.error(f'Download failed: {error}')
        return redirect(url_for('file_manager.index', path=os.path.dirname(filename)))

    return redirect(file_url) if file_url else redirect(url_for('file_manager.index'))


@file_manager_bp.route('/mkdir', methods=['POST'])
def mkdir():
    """Create a new directory."""
    path = request.form.get('path', '')
    dirname = secure_filename(request.form['dirname'])

    storage = get_storage_provider()
    folder_path = os.path.join(path, dirname) if path else dirname

    success, error = storage.create_folder(folder_path)
    if not success:
        current_app.logger.error(f'Create folder failed: {error}')
        # You might want to flash the error message here

    return redirect(url_for('file_manager.index', path=path))
