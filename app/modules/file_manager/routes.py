"""File manager routes module."""
import os

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from .storage.factory import get_storage_provider

file_manager_bp = Blueprint(
    'file_manager', __name__, template_folder='templates', static_folder='static', url_prefix='/'
)


@file_manager_bp.route('/')
def index():
    """List files and directories at the given path."""
    path = request.args.get('path', '')

    storage = get_storage_provider()
    items = storage.list_items(path)

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
        cloudinary_status=cloudinary_status
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
