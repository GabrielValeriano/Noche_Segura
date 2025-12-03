import json
import mysql.connector




def test_delete_falla_conexion_db(client, monkeypatch):
    """
    Simula una falla de conexión a la base de datos durante la ELIMINACIÓN (DELETE).
    """
    # Usamos un ID cualquiera, ya que la conexión fallará antes de buscarlo
    ID_A_BORRAR = 9999 
    delete_url = f'/usuarios/{ID_A_BORRAR}'

    def mock_get_db_connection_falla():
        """Función simulada que siempre devuelve None."""
        return None 

    # Reemplaza la función real por la función simulada
    monkeypatch.setattr('app.get_db_connection', mock_get_db_connection_falla)

    # Ejecutar DELETE
    response = client.delete(delete_url)

    # Verificaciones
    assert response.status_code == 500, f"Se esperaba 500, se obtuvo {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "No se pudo conectar a la base de datos"

    print(f"✅ Prueba de DELETE con falla de conexión a DB (500) completada exitosamente.")




def test_eliminar_usuario_usando_fixture(client, setup_usuario_id):
    # 'setup_usuario_id' ahora contiene el ID que la fixture insertó
    id_a_eliminar = setup_usuario_id 

    # Llamar al endpoint DELETE
    delete_url = f'/usuarios/{id_a_eliminar}'
    response = client.delete(delete_url)
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data['mensaje'] == 'Usuario eliminado'
