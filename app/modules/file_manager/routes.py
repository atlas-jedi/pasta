import os
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app
from werkzeug.utils import secure_filename

file_manager_bp = Blueprint('file_manager', __name__, 
                          template_folder='templates',
                          static_folder='static',
                          url_prefix='/')

@file_manager_bp.route('/')
def index():
    path = request.args.get('path', '')
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], path)
    
    items = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        items.append({
            'name': item,
            'is_dir': os.path.isdir(item_path),
            'size': os.path.getsize(item_path) if not os.path.isdir(item_path) else 0,
            'path': os.path.join(path, item)
        })
    
    return render_template('index.html', items=items, current_path=path)

@file_manager_bp.route('/upload', methods=['POST'])
def upload_file():
    path = request.form.get('path', '')
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], path)
    
    if 'file' not in request.files:
        return redirect(url_for('file_manager.index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('file_manager.index'))
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(target_dir, filename))
    return redirect(url_for('file_manager.index', path=path))

@file_manager_bp.route('/delete/<path:filename>')
def delete_file(filename):
    target = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.isfile(target):
        os.remove(target)
    elif os.path.isdir(target):
        os.rmdir(target)
        
    return redirect(url_for('file_manager.index', path=os.path.dirname(filename)))

@file_manager_bp.route('/download/<path:filename>')
def download_file(filename):
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.dirname(filename))
    return send_from_directory(directory, os.path.basename(filename), as_attachment=True)

@file_manager_bp.route('/mkdir', methods=['POST'])
def mkdir():
    path = request.form.get('path', '')
    dirname = secure_filename(request.form['dirname'])
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], path, dirname)
    
    os.makedirs(target_dir, exist_ok=True)
    return redirect(url_for('file_manager.index', path=path)) 