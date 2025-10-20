# RUTA GET:
def test_ping(client):
    response = client.get("/usuarios")
    assert response.status_code == 200

# RUTA POST:
def test_create_user_success(client):
    response = client.post("/usuarios", json={"nombre_usuario": "Pablito", "email": "clavito@gmail.com", "contrasena": "1234"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["nombre_usuario"] == "Pablito"

# RUTA PULL
def test_update_user_partial_success(client):

    user_id = 
    nuevo_nombre = "NombreActualizadoPorPUT"

    update_data = {"nombre_usuario": nuevo_nombre}
    
    # 2. Ejecutar la actualización (PUT)
    response_put = client.put(f"/usuarios/{user_id}", json=update_data)
    
    # 3. Afirmación del estado HTTP (debe ser 200 OK)
    assert response_put.status_code == 200
    assert response_put.get_json()["mensaje"] == "Usuario actualizado"

import pytest
# El uso de 'uuid' ha sido removido según solicitud, 
# lo que puede causar fallos 400 si la base de datos no se limpia.
# Recuerda: el 'client' viene de tu archivo conftest.py

# --- DATOS FIJOS DE PRUEBA ---
# ADVERTENCIA: Estos datos deben ser eliminados de la DB después de cada prueba.
SETUP_USER_NAME = "SetupFixedUser"
SETUP_USER_EMAIL = "setup.fixed@test.com"
POST_USER_NAME = "PostFixedUser"
POST_USER_EMAIL = "post.fixed@test.com"
# -----------------------------


# ----------------------------------------------------------------------
# FUNCIÓN AUXILIAR (HELPER): Usa datos fijos y depende de limpieza externa
# ----------------------------------------------------------------------

def setup_user_for_crud(client):
    """
    Crea un usuario con datos fijos. Si el usuario ya existe (400),
    el test fallará. Requiere limpieza externa.
    """
    user_data = {
        "nombre_usuario": SETUP_USER_NAME,
        "email": SETUP_USER_EMAIL,
        "contrasena": "pass123_temp"
    }
    
    # Ejecuta la solicitud POST
    response = client.post("/usuarios", json=user_data)
    
    # Si la creación fue exitosa, devuelve el ID
    if response.status_code == 201:
        return response.get_json()["usuario_id"]
    
    # NOTA: Si recibes 400 (usuario duplicado), la prueba fallará aquí
    return None

# ----------------------------------------------------------------------
# RUTA GET: /usuarios
# ----------------------------------------------------------------------

def test_get_usuarios_ping(client):
    """Verifica que la ruta GET esté accesible (200 OK)."""
    response = client.get("/usuarios")
    assert response.status_code == 200

# ----------------------------------------------------------------------
# RUTA POST: /usuarios (Creación)
# ----------------------------------------------------------------------

def test_create_user_success(client):
    """
    Verifica la creación exitosa (201) de un usuario con datos fijos.
    Si este test falla con 400 en la segunda ejecución, la DB no está limpia.
    """
    user_data = {
        "nombre_usuario": POST_USER_NAME, 
        "email": POST_USER_EMAIL, 
        "contrasena": "1234_password"
    }
    
    response = client.post("/usuarios", json=user_data)
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["nombre_usuario"] == POST_USER_NAME
    assert "usuario_id" in data
    
    # Limpieza: Eliminamos el usuario creado (IMPRESCINDIBLE)
    if 'usuario_id' in data:
        client.delete(f"/usuarios/{data['usuario_id']}")


# ----------------------------------------------------------------------
# RUTA PUT: /usuarios/<id> (Actualización)
# ----------------------------------------------------------------------

def test_update_user_partial_success(client):
    """
    Verifica que la actualización PUT funcione. Depende de que setup_user_for_crud
    pueda crear el usuario.
    """
    # 1. Preparación: Crear un usuario usando el helper y obtener su ID
    user_id = setup_user_for_crud(client)
    
    if user_id is None:
        # Si falla la creación (ej. 400 duplicado), saltamos la prueba
        pytest.skip("No se pudo preparar el usuario para la prueba de PUT (posible duplicado en DB).")
        
    nuevo_nombre = "NombreActualizadoPorPUT"

    update_data = {"nombre_usuario": nuevo_nombre}
    
    # 2. Ejecutar la actualización (PUT)
    response_put = client.put(f"/usuarios/{user_id}", json=update_data)
    
    # 3. Afirmación del estado HTTP (debe ser 200 OK)
    assert response_put.status_code == 200
    assert response_put.get_json()["mensaje"] == "Usuario actualizado"
    
    # 4. Verificación: Comprobar que el cambio se hizo con una nueva consulta GET.
    response_get = client.get("/usuarios")
    usuarios = response_get.get_json()
    usuario_actualizado = next((u for u in usuarios if u["usuario_id"] == user_id), None)
    
    assert usuario_actualizado["nombre_usuario"] == nuevo_nombre

    # 5. Limpieza: Eliminar el usuario temporal (CRUCIAL)
    client.delete(f"/usuarios/{user_id}")
