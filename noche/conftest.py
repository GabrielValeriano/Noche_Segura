import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# --- TRUCO PARA QUE ENCUENTRE APP.PY ---
# Esto agrega la carpeta actual (donde está este archivo) al sistema de búsqueda de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import app

@pytest.fixture
def client():
    """Configura el cliente de pruebas de Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    """
    Simula la conexión a la base de datos.
    Devuelve el objeto 'mock_connection' y 'mock_cursor'.
    Evita que los tests intenten conectarse a la IP real 10.9.120.5.
    """
    with patch('app.get_db_connection') as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Configuración para que al llamar a get_db_connection() devuelva nuestro mock
        mock_get_db.return_value = mock_conn
        
        # Configuración para que al crear un cursor, devuelva nuestro cursor falso
        mock_conn.cursor.return_value = mock_cursor
        
        yield mock_conn, mock_cursor