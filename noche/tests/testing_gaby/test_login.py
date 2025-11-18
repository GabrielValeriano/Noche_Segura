import json
from werkzeug.security import generate_password_hash 

def test_faltan_datos_login(client):

    datos_incompletos = {
        "email": "test@ejemplo.com", 
    }
    
    response = client.post('/login',data=json.dumps(datos_incompletos),content_type='application/json')
    
    assert response.status_code == 400, "Debe devolver 400 si faltan campos."
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Faltan datos"

def test_crear_usuario_falla_conexion_db(client, monkeypatch):

    datos_completos = {
        "email": "mauro@mail.com",
        "contrasena": "password123",
    }
    
    def mock_get_db_connection_falla():
        """Función simulada que siempre devuelve None."""
        return None 

    # Reemplaza la función real por la función simulada, usamos monkeypatch y setattr
    monkeypatch.setattr('app.get_db_connection', mock_get_db_connection_falla)

    response = client.post('/login',data=json.dumps(datos_completos),content_type='application/json')

    assert response.status_code == 500
    data = response.get_json()

    assert 'error' in data
    assert data['error'] == "No se pudo conectar a la base de datos"

def test_usuario_no_registrado(client):
    datos_usuario = {
        "email": "miguelito@mail.com",
        "contrasena": "password123",
    }

    response = client.post('/login',data=json.dumps(datos_usuario),content_type='application/json')
    
    # Assertions
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "El correo no está registrado"



def test_contraseña_incorrecta(client):
    
    # Generamos un hash de una contraseña que NO coincide con "password123"
    datos_usuario = {
        "email": "miguelito@mail.com",
        "contrasena": "password123", # Contraseña enviada que fallará
    }

    # 3. Ejecutar la solicitud
    response = client.post('/login',data=json.dumps(datos_usuario),content_type='application/json')
    
    # 4. Assertions
    # El hash no coincide con "password123", por lo tanto, debe fallar con 401
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Contraseña incorrecta"

def test_login(client):
    datos_usuario = {
        "email": "miguelito@mail.com",
        "contrasena": "123456",
    }

    response = client.post('/login',data=json.dumps(datos_usuario),content_type='application/json')
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data['error'] ==

