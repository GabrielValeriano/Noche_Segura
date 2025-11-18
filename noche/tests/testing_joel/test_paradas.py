import json

def test_get_paradas_agrupadas(client, mock_db):
    _, mock_cursor = mock_db

    # Simulamos datos de la BD.
    # Fíjate: La parada 1 aparece dos veces porque pasan dos líneas (101 y 102)
    mock_datos = [
        {
            'parada_id': 1, 'latitud': -34.1, 'longitud': -58.1, 
            'nombre_calle': 'Av. Siempreviva', 'nivel_id': 1, 'numero_linea': 101
        },
        {
            'parada_id': 1, 'latitud': -34.1, 'longitud': -58.1, 
            'nombre_calle': 'Av. Siempreviva', 'nivel_id': 1, 'numero_linea': 102
        },
        {
            'parada_id': 2, 'latitud': -34.2, 'longitud': -58.2, 
            'nombre_calle': 'Calle Falsa', 'nivel_id': 2, 'numero_linea': 60
        }
    ]
    mock_cursor.fetchall.return_value = mock_datos

    response = client.get('/paradas')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert len(data) == 2  # Deberían ser solo 2 paradas únicas, no 3 objetos

    # Verificar parada 1 y sus líneas agrupadas
    parada_1 = next(p for p in data if p['parada_id'] == 1)
    assert parada_1['nombre_calle'] == 'Av. Siempreviva'
    assert 101 in parada_1['lineas']
    assert 102 in parada_1['lineas']

def test_paradas_vacias(client, mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []

    response = client.get('/paradas')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data == []