import os

import pytest
from dotenv import load_dotenv

from app import create_app


@pytest.fixture
def app():
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    # Criar app com configuração de teste
    app = create_app(
        {
            "TESTING": True,
            "UPLOAD_FOLDER": "test_uploads",
            "CLOUDINARY": {
                "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
                "api_key": os.getenv("CLOUDINARY_API_KEY"),
                "api_secret": os.getenv("CLOUDINARY_API_SECRET"),
            },
        }
    )

    # Criar diretório de uploads para teste
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    yield app

    # Limpar diretório de uploads após os testes
    for root, dirs, files in os.walk(app.config["UPLOAD_FOLDER"], topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(app.config["UPLOAD_FOLDER"])


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
