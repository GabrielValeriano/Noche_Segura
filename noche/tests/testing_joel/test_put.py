import json

def test_actualizar_usuario_exitoso(client, mock_db):
    mock_conn, mock_cursor = mock_db

    # Datos nuevos
    payload = {
        "nombre_usuario": "nuevo_nombre",
        "email": "nuevo@email.com"
    }

    response = client.put('/usuarios/123', json=payload)
    
    assert response.status_code == 200
    assert json.loads(response.data)['mensaje'] == "Usuario actualizado"
    
    # Verificar que se llamó a execute con los datos correctos
    # Verificamos que se ejecutó el UPDATE
    args, _ = mock_cursor.execute.call_args
    query_ejecutada = args[0]
    parametros = args[1]
    
    assert "UPDATE Usuarios SET" in query_ejecutada
    assert "nuevo_nombre" in parametros
    assert "nuevo@email.com" in parametros
    assert 123 in parametros  # El ID del usuario

def test_actualizar_sin_datos(client, mock_db):
    # Enviamos JSON vacío
    response = client.put('/usuarios/123', json={})
    
    assert response.status_code == 400
    assert "No se proporcionaron datos" in json.loads(response.data)['mensaje']

def test_actualizar_error_bd(client, mock_db):
    mock_conn, mock_cursor = mock_db
    
    # Simulamos que la base de datos falla al hacer commit o execute
    import mysql.connector
    mock_cursor.execute.side_effect = mysql.connector.Error("Fallo update")
    
    payload = {"nombre_usuario": "fail"}
    response = client.put('/usuarios/123', json=payload)
    
    assert response.status_code == 500
    assert "Error al actualizar" in json.loads(response.data)['error']