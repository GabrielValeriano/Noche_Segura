import json
import mysql.connector

def test_eliminar_usuario_exitoso(client, mock_db):
    mock_conn, mock_cursor = mock_db
    
    # No necesitamos simular fetchone/all porque DELETE no devuelve filas,
    # solo necesitamos que no falle.
    
    response = client.delete('/usuarios/55')
    
    assert response.status_code == 200
    assert json.loads(response.data)['mensaje'] == "Usuario eliminado"
    
    # Verificar que se llamó al SQL correcto
    args, _ = mock_cursor.execute.call_args
    assert "DELETE FROM Usuarios" in args[0]
    assert 55 in args[1] # El ID pasado
    assert mock_conn.commit.called # Se debe confirmar la transacción

def test_eliminar_usuario_error_bd(client, mock_db):
    mock_conn, mock_cursor = mock_db
    
    # Hacemos que execute lance una excepción
    mock_cursor.execute.side_effect = mysql.connector.Error("Error de integridad FK")
    
    response = client.delete('/usuarios/55')
    
    assert response.status_code == 500
    assert "Error al eliminar" in json.loads(response.data)['error']