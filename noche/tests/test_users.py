# Ejemplo de prueba (puedes adaptar tus pruebas existentes)

def test_get_usuarios(client):
    """Prueba que el endpoint /usuarios responde."""
    response = client.get('/usuarios')
    assert response.status_code == 200
    # Puedes añadir más assertions aquí
    # assert b"email" in response.data