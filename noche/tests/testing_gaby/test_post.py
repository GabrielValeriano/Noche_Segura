import json

def test_faltan_datos(client):

    datos_incompletos = {
        "nombre_usuario": "testuser", 
        "email": "test@ejemplo.com", 
        "contrasena": "password123", 
        "pregunta_seguridad": "¿Color favorito?"
        # Falta 'respuesta_seguridad'
    }
    
    response = client.post('/usuarios',data=json.dumps(datos_incompletos),content_type='application/json')
    
    assert response.status_code == 400, "Debe devolver 400 si faltan campos."
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Faltan datos (se requieren 5 campos)"

def test_crear_usuario_existente(client):
    datos_usuario = {
        "nombre_usuario": "Miguel",
        "email": "miguelito@mail.com",
        "contrasena": "password123",
        "pregunta_seguridad": "¿Color?",
        "respuesta_seguridad": "Azul"
    }

    response = client.post('/usuarios',data=json.dumps(datos_usuario),content_type='application/json')
    
    assert response.status_code == 400, "Debe devolver 400 si el usuario o email ya esta registrado"
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "El nombre de usuario o email ya está registrado"


def test_crear_usuario_falla_conexion_db(client, monkeypatch):

    datos_completos = {
        "nombre_usuario": "falla",
        "email": "falla@mail.com",
        "contrasena": "password123",
        "pregunta_seguridad": "¿Animal favorito?",
        "respuesta_seguridad": "Perro"
    }
    
    def mock_get_db_connection_falla():
        """Función simulada que siempre devuelve None."""
        return None 

    # Reemplaza la función real por la función simulada, usamos monkeypatch y setattr
    monkeypatch.setattr('app.get_db_connection', mock_get_db_connection_falla)

    response = client.post('/usuarios',data=json.dumps(datos_completos),content_type='application/json')

    assert response.status_code == 500
    data = response.get_json()

    assert 'error' in data
    assert data['error'] == "No se pudo conectar a la base de datos"



def test_crear(client):

    datos_nuevo_usuario = {
        "nombre_usuario": "Eva",
        "email": "evesita@test.com",
        "contrasena": "123456",
        "pregunta_seguridad": "¿Cuidad donde naciste?",
        "respuesta_seguridad": "Perro"
    }
    usuario_id = None


    print("Iniciando creación de usuario...")
    response_post = client.post(
        '/usuarios',
        data=json.dumps(datos_nuevo_usuario),
        content_type='application/json'
    )

    assert response_post.status_code == 201
    data_post = response_post.get_json()
    usuario_id = data_post.get('usuario_id')
    assert usuario_id is not None, "El endpoint POST debe retornar 'usuario_id'."

    print(f"Borrando usuario con ID: {usuario_id}...")
    response_delete = client.delete(f'/usuarios/{usuario_id}')
    assert response_delete.status_code in [200, 204]
    print(f"Verificando que ID {usuario_id} ya no existe...")
    response_get_check = client.get(f'/usuarios/{usuario_id}')
    assert response_get_check.status_code == 405
    print("Procedimiento Crear y Borrar completado exitosamente.")



