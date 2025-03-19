import os

from dotenv import load_dotenv
import pytest

from app import create_app


def pytest_configure(config):
    """Configure pytest before test execution."""
    # Define um marcador para testes que dependem do Cloudinary
    config.addinivalue_line(
        'markers', 'cloudinary: mark a test that requires Cloudinary connection'
    )


def detect_homologation_environment():
    """Detecta se estamos no ambiente de homologação."""
    # Verificar se FLASK_ENV está definido como homologation
    flask_env = os.environ.get('FLASK_ENV')
    if flask_env == 'homologation':
        return True

    # Verificar se o arquivo .env.homologation está sendo usado
    if os.path.exists('.env.homologation'):
        with open('.env.homologation', 'r') as f:
            for line in f:
                if 'FLASK_ENV=homologation' in line:
                    # Verifica se este é o arquivo de ambiente atual
                    if os.path.exists('.env'):
                        with open('.env', 'r') as env_file:
                            if env_file.read() == f.read():
                                return True

    # Verifica se foi passado um parâmetro de linha de comando
    import sys

    if len(sys.argv) > 1 and 'homologation' in sys.argv:
        return True

    return False


@pytest.fixture(scope='session', autouse=True)
def skip_cloudinary_tests():
    """Skip cloudinary tests in homologation environment."""
    if detect_homologation_environment():
        # Se estiver em ambiente de homologação, configurar para pular testes com o marcador
        pytest.skip(
            'Cloudinary tests are disabled in homologation environment', allow_module_level=True
        )


@pytest.fixture
def app():
    """Create and configure a test Flask application instance.

    Returns:
        Flask: A Flask application instance configured for testing.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create app with test configuration
    app = create_app(
        {
            'TESTING': True,
            'UPLOAD_FOLDER': 'test_uploads',
            'CLOUDINARY': {
                'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
                'api_key': os.getenv('CLOUDINARY_API_KEY'),
                'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
            },
        }
    )

    # Create test uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    yield app

    # Clean up uploads directory after tests
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER'], topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(app.config['UPLOAD_FOLDER'])


@pytest.fixture
def client(app):
    """Get a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Get a test CLI runner for the Flask application."""
    return app.test_cli_runner()
