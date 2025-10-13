import pytest
# IMPORTANTE: Importamos la instancia de Flask 'app' desde el módulo 'app.py'
from app import app as flask_app 

@pytest.fixture
def app():
    """
    Fixture que proporciona la aplicación Flask configurada para testing.
    """
    app = flask_app
    
    # Habilitamos el modo de TESTING. Esto es crucial.
    app.config.update({
        "TESTING": True,
    })

    # Configuramos para que no falle la conexión a la DB durante el setup,
    # aunque para tests reales, se debe simular la conexión (mocking).
    yield app

@pytest.fixture
def client(app):
    """
    Fixture que proporciona el cliente de prueba de Flask. 
    Se utiliza para simular peticiones (GET, POST, etc.).
    """
    return app.test_client()

# NOTA IMPORTANTE: Para tests robustos, se recomienda encarecidamente 
# simular (mockear) la función get_db_connection() para que no dependa 
# de un servidor MySQL real.
