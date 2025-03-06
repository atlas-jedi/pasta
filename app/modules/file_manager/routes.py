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
    "file_manager", __name__, template_folder="templates", static_folder="static", url_prefix="/"
)


def get_cloudinary_resource_type(filename):
    """Determina o tipo de recurso do Cloudinary baseado na extensão do arquivo"""
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    video_extensions = {".mp4", ".mov", ".avi", ".webm"}
    ext = os.path.splitext(filename)[1].lower()

    if ext in image_extensions:
        return "image"
    elif ext in video_extensions:
        return "video"
    return "raw"


@file_manager_bp.route("/")
def index():
    path = request.args.get("path", "")
    full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], path)

    items = []

    # Se o Cloudinary está configurado, buscar arquivos de lá
    if all(current_app.config["CLOUDINARY"].values()):
        try:
            # Listar recursos do Cloudinary
            result = cloudinary.api.resources(
                type="upload", prefix=path if path else None, max_results=500
            )

            for resource in result.get("resources", []):
                filename = os.path.basename(resource["public_id"])
                items.append(
                    {
                        "name": filename,
                        "is_dir": False,
                        "size": resource.get("bytes", 0),
                        "path": resource["public_id"],
                    }
                )
        except Exception as e:
            current_app.logger.error(f"Erro ao listar arquivos do Cloudinary: {e}")

    # Caso contrário, usar sistema de arquivos local
    else:
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            items.append(
                {
                    "name": item,
                    "is_dir": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if not os.path.isdir(item_path) else 0,
                    "path": os.path.join(path, item),
                }
            )

    return render_template("index.html", items=items, current_path=path)


@file_manager_bp.route("/upload", methods=["POST"])
def upload_file():
    path = request.form.get("path", "")

    if "file" not in request.files:
        return redirect(url_for("file_manager.index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("file_manager.index"))

    filename = secure_filename(file.filename)

    # Se o Cloudinary está configurado, fazer upload para lá
    if all(current_app.config["CLOUDINARY"].values()):
        try:
            resource_type = get_cloudinary_resource_type(filename)
            upload_path = os.path.join(path, filename) if path else filename

            # Upload para o Cloudinary
            result = cloudinary.uploader.upload(
                file, public_id=upload_path, resource_type=resource_type
            )
            current_app.logger.info(f"Arquivo enviado para Cloudinary: {result['url']}")
        except Exception as e:
            current_app.logger.error(f"Erro ao fazer upload para Cloudinary: {e}")

    # Caso contrário, salvar localmente
    else:
        target_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], path)
        file.save(os.path.join(target_dir, filename))

    return redirect(url_for("file_manager.index", path=path))


@file_manager_bp.route("/delete/<path:filename>")
def delete_file(filename):
    # Se o Cloudinary está configurado, deletar de lá
    if all(current_app.config["CLOUDINARY"].values()):
        try:
            resource_type = get_cloudinary_resource_type(filename)
            cloudinary.uploader.destroy(filename, resource_type=resource_type)
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar arquivo do Cloudinary: {e}")

    # Caso contrário, deletar localmente
    else:
        target = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if os.path.isfile(target):
            os.remove(target)
        elif os.path.isdir(target):
            os.rmdir(target)

    return redirect(url_for("file_manager.index", path=os.path.dirname(filename)))


@file_manager_bp.route("/download/<path:filename>")
def download_file(filename):
    # Se o Cloudinary está configurado, redirecionar para a URL do arquivo
    if all(current_app.config["CLOUDINARY"].values()):
        try:
            resource = cloudinary.api.resource(filename)
            return redirect(resource["url"])
        except Exception as e:
            current_app.logger.error(f"Erro ao obter URL do Cloudinary: {e}")

    # Caso contrário, enviar arquivo local
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], os.path.dirname(filename))
    return send_from_directory(directory, os.path.basename(filename), as_attachment=True)


@file_manager_bp.route("/mkdir", methods=["POST"])
def mkdir():
    path = request.form.get("path", "")
    dirname = secure_filename(request.form["dirname"])

    # Criar diretório apenas localmente
    target_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], path, dirname)
    os.makedirs(target_dir, exist_ok=True)

    return redirect(url_for("file_manager.index", path=path))
