import json
from werkzeug.security import generate_password_hash
import mysql.connector

# --- PRUEBAS PARA /obtener-pregunta ---

def test_obtener_pregunta_falla_conexion(client, monkeypatch):
    """Prueba de fallo de conexión (500) con monkeypatch"""
    monkeypatch.setattr('app.get_db_connection', lambda: None)

    response = client.post('/obtener-pregunta', json={'identificador': 'a'})
    assert response.status_code == 500
    assert "No se pudo conectar" in response.get_json()['error']

def test_obtener_pregunta_usuario_inexistente(client, mock_db):
    """Prueba de usuario no encontrado (404)"""
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None 
    
    response = client.post('/obtener-pregunta', json={'identificador': 'nadie@test.com'})
    assert response.status_code == 404
    assert "No se encontró" in response.get_json()['error']

def test_obtener_pregunta_exitoso(client, mock_db):
    """Prueba exitosa (200)"""
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {'pregunta_seguridad': '¿Mascota?'}
    
    response = client.post('/obtener-pregunta', json={'identificador': 'ok@test.com'})
    assert response.status_code == 200
    assert response.get_json()['pregunta'] == '¿Mascota?'

# --- PRUEBAS PARA /restablecer-por-pregunta ---

def test_restablecer_falla_conexion(client, monkeypatch):
    monkeypatch.setattr('app.get_db_connection', lambda: None)
    
    response = client.post('/restablecer-por-pregunta', json={})
    assert response.status_code == 500
    assert "No se pudo conectar" in response.get_json()['error']

def test_restablecer_respuesta_incorrecta(client, mock_db):
    """Prueba de seguridad (401)"""
    _, mock_cursor = mock_db
    hash_real = generate_password_hash("Correcto")
    mock_cursor.fetchone.return_value = {'usuario_id': 1, 'respuesta_seguridad_hash': hash_real}
    
    payload = {'identificador': 'test', 'respuesta_seguridad': 'Incorrecto', 'nueva_contrasena': '123'}
    response = client.post('/restablecer-por-pregunta', json=payload)
    
    assert response.status_code == 401
    assert "incorrecta" in response.get_json()['error']

def test_restablecer_falla_update_sql(client, mock_db):
    """Prueba de fallo de ejecución SQL (500)"""
    _, mock_cursor = mock_db
    
    # 1. Encuentra usuario (SELECT ok)
    hash_real = generate_password_hash("Correcto")
    mock_cursor.fetchone.return_value = {'usuario_id': 1, 'respuesta_seguridad_hash': hash_real}
    
    # 2. Falla al actualizar (UPDATE error)
    # El primer execute es el SELECT (pasa), el segundo es el UPDATE (falla)
    mock_cursor.execute.side_effect = [None, mysql.connector.Error("DB Error")]
    
    payload = {'identificador': 'test', 'respuesta_seguridad': 'Correcto', 'nueva_contrasena': '123'}
    response = client.post('/restablecer-por-pregunta', json=payload)
    
    assert response.status_code == 500
    assert "Error al restablecer" in response.get_json()['error']

def test_restablecer_exitoso(client, mock_db):
    _, mock_cursor = mock_db
    hash_real = generate_password_hash("Correcto")
    mock_cursor.fetchone.return_value = {'usuario_id': 1, 'respuesta_seguridad_hash': hash_real}
    # Reseteamos side_effect por si acaso
    mock_cursor.execute.side_effect = None 
    
    payload = {'identificador': 'test', 'respuesta_seguridad': 'Correcto', 'nueva_contrasena': 'nueva123'}
    response = client.post('/restablecer-por-pregunta', json=payload)
    
    assert response.status_code == 200
    assert "actualizada con éxito" in response.get_json()['mensaje']