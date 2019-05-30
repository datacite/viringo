"""Test fixture configuration"""
import pytest
from viringo import create_app

@pytest.fixture
def app():
    """Create a test version of the application"""
    test_app = create_app({
        'TESTING': True,
    })

    yield test_app

@pytest.fixture
def client(app):
    """Create a test client fixture"""
    return app.test_client()
