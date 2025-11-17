def test_get_usuarios(client):
    """Prueba que el endpoint /usuarios responde."""
    response = client.get('/usuarios')
    data = response.get_json()
    #print("hola",data)
    assert response.status_code == 200
    assert len(data) > 0