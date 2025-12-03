import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from app import app as flask_app, get_db_connection 
from app import app

# --- TRUCO PARA QUE ENCUENTRE APP.PY ---
# Esto agrega la carpeta actual (donde está este archivo) al sistema de búsqueda de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

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



POLIGONO_VALIDO = '{"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}'
POLIGONO_INVALIDO = '{"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1]]' # Falta llave de cierre
NOMBRE_ZONA_VALIDA = "Zona_Test_OK_A"
NOMBRE_ZONA_INVALIDA = "Zona_Test_JSON_Fail_B"

@pytest.fixture(scope="function")
def setup_zona_valida():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        sql_insert = """
            INSERT INTO ZonasDeSeguridad (nombre, descripcion, nivel_id, poligono_geografico) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (NOMBRE_ZONA_VALIDA, "Zona OK.", 1, POLIGONO_VALIDO))
        connection.commit()
        
        yield NOMBRE_ZONA_VALIDA
        
    finally:
        if connection:
            try:
                sql_delete = "DELETE FROM ZonasDeSeguridad WHERE nombre = %s"
                connection.cursor().execute(sql_delete, (NOMBRE_ZONA_VALIDA,))
                connection.commit()
            finally:
                if connection: connection.close()


@pytest.fixture(scope="function")
def setup_zona_geojson_invalido():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_insert = """
            INSERT INTO ZonasDeSeguridad (nombre, descripcion, nivel_id, poligono_geografico) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (NOMBRE_ZONA_INVALIDA, "GeoJSON corrupto.", 1, POLIGONO_INVALIDO))
        connection.commit()
        
        yield NOMBRE_ZONA_INVALIDA
        
    finally:
        if connection:
            try:
                sql_delete = "DELETE FROM ZonasDeSeguridad WHERE nombre = %s"
                connection.cursor().execute(sql_delete, (NOMBRE_ZONA_INVALIDA,))
                connection.commit()
            finally:
                if connection: connection.close()



# Datos reutilizables para los tests
USUARIO_TEST = ("usuario_temp", "temp@test.com", "pass_temp", "¿Color favorito?", "Azul")

@pytest.fixture(scope="function")
def setup_usuario_id():
    """
    Inserta un usuario en la DB antes de la prueba (Setup) y 
    garantiza su eliminación después (Teardown).
    Devuelve el 'usuario_id' generado.
    """
    usuario_id_creado = None
    connection = None
    cursor = None
    
    try:
        # --- PARTE 1: SETUP (Insertar el Usuario) ---
        connection = get_db_connection()
        cursor = connection.cursor()
        
        sql_insert = """
            INSERT INTO Usuarios(nombre_usuario, email, contraseña_hash, pregunta_seguridad, respuesta_seguridad_hash) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (USUARIO_TEST))
        connection.commit()
        
        # OBTENEMOS el ID generado por la DB
        usuario_id_creado = cursor.lastrowid
        
        # ENTREGAMOS el ID al test que use este fixture
        yield usuario_id_creado 
        
    finally:
        # --- PARTE 2: TEARDOWN (Eliminar el Usuario) ---
        # Se ejecuta después de que el test termina.
        if connection and usuario_id_creado is not None:
            try:
                # Reabrimos un cursor si fuera necesario, o usamos el existente si está abierto
                cursor_delete = connection.cursor() 
                sql_delete = "DELETE FROM Usuarios WHERE usuario_id = %s"
                cursor_delete.execute(sql_delete, (usuario_id_creado,))
                connection.commit()
            except Exception as e:
                # Manejo de errores de limpieza, si falla el test o la DB.
                print(f"Error en la limpieza (Teardown) del usuario ID {usuario_id_creado}: {e}")
            finally:
                if cursor: cursor.close()
                if 'cursor_delete' in locals(): cursor_delete.close()
                if connection: connection.close()