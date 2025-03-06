import os

import cloudinary
from flask import Flask

from .config import Config


def create_app(test_config=None):
    # Criar e configurar a aplicação
    app = Flask(__name__, instance_relative_config=True)

    # Carregar configuração padrão
    app.config.from_object(Config)

    if test_config is None:
        # Carregar a configuração da instância, se existir
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Carregar a configuração de teste
        app.config.from_mapping(test_config)

    # Garantir que o diretório de uploads exista
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Configurar Cloudinary
    if all(app.config["CLOUDINARY"].values()):
        cloudinary.config(
            cloud_name=app.config["CLOUDINARY"]["cloud_name"],
            api_key=app.config["CLOUDINARY"]["api_key"],
            api_secret=app.config["CLOUDINARY"]["api_secret"],
        )

    # Registrar blueprints
    from app.modules.file_manager.routes import file_manager_bp
    from app.modules.time_calculator.routes import time_calculator_bp

    app.register_blueprint(file_manager_bp)
    app.register_blueprint(time_calculator_bp)

    return app
