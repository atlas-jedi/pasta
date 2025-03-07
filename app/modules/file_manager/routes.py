import os

import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

file_manager_bp = Blueprint(
    'file_manager', __name__, template_folder='templates', static_folder='static', url_prefix='/'
)


def get_cloudinary_resource_type(filename):
    """Determines the Cloudinary resource type based on the file extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    video_extensions = {'.mp4', '.mov', '.avi', '.webm'}
    ext = os.path.splitext(filename)[1].lower()

    if ext in image_extensions:
        return 'image'
    elif ext in video_extensions:
        return 'video'
    return 'raw'


def check_cloudinary_status():
    """Check Cloudinary configuration and connection status."""
    status = {
        'configured': all(current_app.config['CLOUDINARY'].values()),
        'online': False,
        'error': False,
        'error_message': ''
    }

    if status['configured']:
        try:
            cloudinary.api.resources(max_results=1)
            status['online'] = True
        except Exception as e:
            current_app.logger.error(f'Cloudinary connection error: {e}')
            status['error'] = True
            status['error_message'] = str(e)

    return status


def list_cloudinary_items(path, cloudinary_status):
    """List items from Cloudinary storage."""
    items = []

    try:
        # List files
        result = cloudinary.api.resources(
            type='upload', prefix=path if path else None, max_results=500
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
        folders_result = cloudinary.api.subfolders(path if path and path.strip() else '')
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
        cloudinary_status['error'] = True
        cloudinary_status['error_message'] = str(e)

    return items


def list_local_items(full_path, path):
    """List items from local filesystem."""
    items = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        items.append({
            'name': item,
            'is_dir': os.path.isdir(item_path),
            'size': os.path.getsize(item_path) if not os.path.isdir(item_path) else 0,
            'path': os.path.join(path, item),
        })
    return items


@file_manager_bp.route('/')
def index():
    """List files and directories at the given path."""
    path = request.args.get('path', '')
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], path)

    cloudinary_status = check_cloudinary_status()
    items = []

    if cloudinary_status['configured'] and cloudinary_status['online']:
        items = list_cloudinary_items(path, cloudinary_status)

    use_local = (
        not cloudinary_status['configured']
        or not cloudinary_status['online']
        or cloudinary_status['error']
    )

    if use_local:
        items = list_local_items(full_path, path)

    return render_template(
        'index.html',
        items=items,
        current_path=path,
        cloudinary_status=cloudinary_status
    )


@file_manager_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload to either Cloudinary or local filesystem."""
    path = request.form.get('path', '')

    if 'file' not in request.files:
        return redirect(url_for('file_manager.index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('file_manager.index'))

    filename = secure_filename(file.filename)

    # If Cloudinary is configured, upload there
    if all(current_app.config['CLOUDINARY'].values()):
        try:
            resource_type = get_cloudinary_resource_type(filename)
            upload_path = os.path.join(path, filename) if path else filename

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file, public_id=upload_path, resource_type=resource_type
            )
            current_app.logger.info(f'File uploaded to Cloudinary: {result["url"]}')
        except Exception as e:
            current_app.logger.error(f'Error uploading to Cloudinary: {e}')

    # Otherwise, save locally
    else:
        target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], path)
        file.save(os.path.join(target_dir, filename))

    return redirect(url_for('file_manager.index', path=path))


@file_manager_bp.route('/delete/<path:filename>')
def delete_file(filename):
    """Delete a file from either Cloudinary or local filesystem."""
    # If Cloudinary is configured, delete from there
    if all(current_app.config['CLOUDINARY'].values()):
        try:
            resource_type = get_cloudinary_resource_type(filename)
            cloudinary.uploader.destroy(filename, resource_type=resource_type)
        except Exception as e:
            current_app.logger.error(f'Error deleting file from Cloudinary: {e}')

    # Otherwise, delete locally
    else:
        target = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(target):
            os.remove(target)
        elif os.path.isdir(target):
            os.rmdir(target)

    return redirect(url_for('file_manager.index', path=os.path.dirname(filename)))


@file_manager_bp.route('/download/<path:filename>')
def download_file(filename):
    """Download a file from either Cloudinary or local filesystem."""
    # If Cloudinary is configured, redirect to file URL
    if all(current_app.config['CLOUDINARY'].values()):
        try:
            resource = cloudinary.api.resource(filename)
            return redirect(resource['url'])
        except Exception as e:
            current_app.logger.error(f'Error getting Cloudinary URL: {e}')

    # Otherwise, send local file
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.dirname(filename))
    return send_from_directory(directory, os.path.basename(filename), as_attachment=True)


@file_manager_bp.route('/mkdir', methods=['POST'])
def mkdir():
    """Create a new directory in Cloudinary or local filesystem."""
    path = request.form.get('path', '')
    dirname = secure_filename(request.form['dirname'])

    # If Cloudinary is configured, create folder there
    if all(current_app.config['CLOUDINARY'].values()):
        try:
            folder_path = os.path.join(path, dirname) if path else dirname
            cloudinary.api.create_folder(folder_path)
        except Exception as e:
            current_app.logger.error(f'Error creating folder in Cloudinary: {e}')

    # Otherwise, create directory locally
    else:
        target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], path, dirname)
        os.makedirs(target_dir, exist_ok=True)

    return redirect(url_for('file_manager.index', path=path))
