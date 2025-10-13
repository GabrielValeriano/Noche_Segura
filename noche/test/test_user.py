def test_ping(client):
    response = client.get("/usuarios")
    assert response.status_code == 200


def test_create_user_success(client):
    response = client.post("/usuarios", json={"nombre_usuario": "Alice", "email": "alicelita@gmail.com", "contrasena": "1234"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["nombre_usuarios"] == "Alice"

