def test_get_usuarios(client):
    """Prueba que el endpoint /usuarios responde."""
    response = client.get('/usuarios')
    data = response.get_json()
    #print("hola",data)
    assert response.status_code == 200
    assert len(data) > 0

def test_falla_BD(client, monkeypatch):

    def mock_get_db_connection_falla():
        """Función simulada que siempre devuelve None."""
        return None 

    monkeypatch.setattr('app.get_db_connection', mock_get_db_connection_falla)

    response = client.get('/usuarios')
    assert response.status_code == 500
    data = response.get_json()

    assert 'error' in data
    assert data['error'] == "No se pudo conectar a la base de datos"
