import pytest
from app import create_app # Importamos la fábrica

@pytest.fixture(scope='module')
def app():
    """Instancia de la aplicación Flask para pruebas."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Aquí puedes sobreescribir configuraciones, ej. una DB de prueba
    })

    yield app

@pytest.fixture(scope='module')
def client(app):
    """Un cliente de pruebas para la app."""
    return app.test_client()