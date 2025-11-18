import json
from werkzeug.security import generate_password_hash

def test_obtener_pregunta_usuario_existente(client, mock_db):
    _, mock_cursor = mock_db
    
    # Simulamos que la BD encuentra al usuario y su pregunta
    mock_cursor.fetchone.return_value = {
        'pregunta_seguridad': '¿Nombre de tu mascota?'
    }
    
    payload = {'identificador': 'test@test.com'}
    response = client.post('/obtener-pregunta', json=payload)
    
    assert response.status_code == 200
    assert json.loads(response.data)['pregunta'] == '¿Nombre de tu mascota?'

def test_obtener_pregunta_usuario_inexistente(client, mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None  # Usuario no encontrado
    
    payload = {'identificador': 'nadie@test.com'}
    response = client.post('/obtener-pregunta', json=payload)
    
    assert response.status_code == 404
    assert "No se encontró" in json.loads(response.data)['error']

def test_restablecer_respuesta_correcta(client, mock_db):
    mock_conn, mock_cursor = mock_db
    
    # 1. Simulamos que la BD devuelve el hash de la respuesta correcta
    # Digamos que la respuesta correcta es "Firulais"
    hash_respuesta = generate_password_hash("Firulais")
    
    mock_cursor.fetchone.return_value = {
        'usuario_id': 99,
        'respuesta_seguridad_hash': hash_respuesta
    }
    
    payload = {
        'identificador': 'test@test.com',
        'respuesta_seguridad': 'Firulais', # Respuesta correcta
        'nueva_contrasena': 'nueva1234'
    }
    
    response = client.post('/restablecer-por-pregunta', json=payload)
    
    assert response.status_code == 200
    assert "actualizada con éxito" in json.loads(response.data)['mensaje']
    
    # Verificamos que se hizo un UPDATE de la contraseña
    assert mock_conn.commit.called
    args, _ = mock_cursor.execute.call_args
    assert "UPDATE Usuarios SET contraseña_hash" in args[0]

def test_restablecer_respuesta_incorrecta(client, mock_db):
    _, mock_cursor = mock_db
    
    # Hash de "Firulais"
    hash_respuesta = generate_password_hash("Firulais")
    
    mock_cursor.fetchone.return_value = {
        'usuario_id': 99,
        'respuesta_seguridad_hash': hash_respuesta
    }
    
    payload = {
        'identificador': 'test@test.com',
        'respuesta_seguridad': 'Michi', # <--- Respuesta INCORRECTA
        'nueva_contrasena': 'nueva1234'
    }
    
    response = client.post('/restablecer-por-pregunta', json=payload)
    
    assert response.status_code == 401
    assert "Respuesta de seguridad incorrecta" in json.loads(response.data)['error']