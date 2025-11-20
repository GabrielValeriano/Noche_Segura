import uuid
import json

def test_zona_falla_BD(client, monkeypatch):

   def mock_get_db_connection_falla():
       """Función simulada que siempre devuelve None."""
       return None
   
   monkeypatch.setattr('app.get_db_connection', mock_get_db_connection_falla)

   response = client.get('/zona/<nombre_zona>')
   assert response.status_code == 500
   data = response.get_json()

   assert 'error' in data
   assert data['error'] == "No se pudo conectar a la base de datos"


def test_get_zona_con_poligono_valido(client, setup_zona_valida):

   nombre_zona = setup_zona_valida
  
   response = client.get(f'/zona/{nombre_zona}')
  
   assert response.status_code == 200
   data = response.get_json()
  
 
   assert 'poligono_geografico' not in data
   assert isinstance(data['poligrafo_geojson'], dict)
   assert data['poligrafo_geojson']['type'] == "Polygon"




def test_get_zona_no_encontrada(client):
    
   nombre_zona_no_existe = f"Zona_Inexistente_{uuid.uuid4()}"
  
   response = client.get(f'/zona/{nombre_zona_no_existe}')
  
   assert response.status_code == 404
   data = response.get_json()
   assert data['error'] == "Zona no encontrada"




def test_get_zona_geojson_invalido(client, setup_zona_geojson_invalido):
  
   # El fixture inserta una zona con GeoJSON corrupto y devuelve el nombre
   nombre_zona = setup_zona_geojson_invalido
  
   response = client.get(f'/zona/{nombre_zona}')
  
   assert response.status_code == 500
   data = response.get_json()
   # Verifica que se capturó el error JSONDecodeError
   assert data['error'].startswith("Error al decodificar el GeoJSON")

