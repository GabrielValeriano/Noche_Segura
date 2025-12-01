import json
from werkzeug.security import generate_password_hash

def test_obtener_pregunta_usuario_existente(client, mock_db):
    """
    Verifica que la API devuelva la pregunta de seguridad correcta
    cuando el usuario existe en la base de datos.
    """
    _, mock_cursor = mock_db
    
    # Simulamos que la BD encuentra al usuario y devuelve su pregunta
    mock_cursor.fetchone.return_value = {
        'pregunta_seguridad': '¿Nombre de tu mascota?'
    }
    
    payload = {'identificador': 'test@test.com'}
    response = client.post('/obtener-pregunta', json=payload)
    
    assert response.status_code == 200
    assert json.loads(response.data)['pregunta'] == '¿Nombre de tu mascota?'

def test_obtener_pregunta_usuario_inexistente(client, mock_db):
    """
    Verifica que la API devuelva 404 (Not Found) si el usuario no existe,
    evitando errores internos o respuestas vacías.
    """
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None  # Usuario no encontrado
    
    payload = {'identificador': 'nadie@test.com'}
    response = client.post('/obtener-pregunta', json=payload)
    
    assert response.status_code == 404
    assert "No se encontró" in json.loads(response.data)['error']

def test_restablecer_respuesta_correcta(client, mock_db):
    """
    Simula el flujo exitoso de recuperación:
    1. La BD tiene un hash guardado.
    2. El usuario envía la respuesta correcta en texto plano.
    3. El backend verifica el hash y actualiza la contraseña.
    """
    mock_conn, mock_cursor = mock_db
    
    # TRUCO DE TEST: Generamos un hash real aquí mismo para que
    # la validación del backend (check_password_hash) funcione correctamente.
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
    
    # IMPORTANTE: Verificamos que se hizo commit (guardar cambios)
    # y que realmente se ejecutó el UPDATE en la tabla Usuarios.
    assert mock_conn.commit.called
    args, _ = mock_cursor.execute.call_args
    assert "UPDATE Usuarios SET contraseña_hash" in args[0]

def test_restablecer_respuesta_incorrecta(client, mock_db):
    """
    Verifica seguridad: Si la respuesta enviada no coincide con el hash de la BD,
    debe rechazar el cambio con un error 401 (Unauthorized).
    """
    _, mock_cursor = mock_db
    
    # La BD espera el hash de "Firulais"
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