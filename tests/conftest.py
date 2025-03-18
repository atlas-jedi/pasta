import os

from dotenv import load_dotenv
import pytest

from app import create_app


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
