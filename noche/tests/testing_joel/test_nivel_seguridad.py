import json
from unittest.mock import MagicMock

def test_get_niveles_seguridad_exitoso(client, mock_db):
    #busca que no solo tenga los datos si no que los reformatee para el frontend
    mock_conn, mock_cursor = mock_db
    
    # Simulamos que la base de datos devuelve dos zonas
    # El cursor en tu app usa dictionary=True, así que simulamos diccionarios
    mock_cursor.fetchall.return_value = [
        {'nombre': 'Palermo', 'nivel_id': 1},
        {'nombre': 'Villa Soldati', 'nivel_id': 3}
    ]

    response = client.get('/niveles_seguridad_zonas')
    data = json.loads(response.data)

    assert response.status_code == 200
    # Verificamos que transformó la lista en un diccionario mapa {nombre: nivel}
    assert data['Palermo'] == 1
    assert data['Villa Soldati'] == 3

def test_get_niveles_error_bd(client, mock_db):
    #Prueba qué pasa si el servidor no puede conectarse a la base de datos(si sql se cae)
    mock_conn, mock_cursor = mock_db
    
    # Simulamos que la conexión falla (retorna None)
    # Debemos hacer patch del get_db_connection para que devuelva None específicamente aquí
    with list(mock_db)[0] as _: # Consumimos el mock existente
        pass
        
    # Forzamos error de conexión simulando que get_db_connection devuelve None
    from app import get_db_connection
    with list(mock_db)[0]: # Hack simple, mejor modificamos el comportamiento del mock existente
        pass
    
    # Una forma más limpia con el fixture existente:
    from unittest.mock import patch
    with patch('app.get_db_connection', return_value=None):
        response = client.get('/niveles_seguridad_zonas')
        assert response.status_code == 500
        assert "error" in json.loads(response.data)