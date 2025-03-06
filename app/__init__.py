import os
from flask import Flask

def create_app(test_config=None):
    # Criar e configurar a aplicação
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER='uploads',
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB
    )

    if test_config is None:
        # Carregar a configuração da instância, se existir
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carregar a configuração de teste
        app.config.from_mapping(test_config)

    # Garantir que o diretório de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Registrar blueprints
    from app.modules.file_manager.routes import file_manager_bp
    from app.modules.time_calculator.routes import time_calculator_bp
    
    app.register_blueprint(file_manager_bp)
    app.register_blueprint(time_calculator_bp)

    return app 