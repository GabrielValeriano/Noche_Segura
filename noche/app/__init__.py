from flask import Blueprint, jsonify
import mysql.connector
import json
from app.db import get_db_connection # Importamos la conexión

# Creamos el Blueprint para el mapa
map_bp = Blueprint('map', __name__)

# ===============================================
# RUTAS DE MAPA (Zonas, Rutas, Paradas)
# ===============================================
@map_bp.route('/niveles_seguridad_zonas', methods=['GET'])
def get_niveles_seguridad_zonas():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    zonas_de_interes = ["Villa Soldati", "Caballito", "Puerto Madero", "Palermo", "Parque Patricios"]
    try:
        placeholders = ', '.join(['%s'] * len(zonas_de_interes))
        sql = f"SELECT nombre, nivel_id FROM ZonasDeSeguridad WHERE nombre IN ({placeholders})"
        cursor.execute(sql, tuple(zonas_de_interes))
        zonas_niveles = cursor.fetchall()
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({"error": f"Error al consultar niveles. Verifique la tabla 'ZonasDeSeguridad'. Detalle: {err}"}), 500
    cursor.close()
    connection.close()
    niveles_map = {zona['nombre']: zona['nivel_id'] for zona in zonas_niveles}
    return jsonify(niveles_map)

@map_bp.route('/zona/<nombre_zona>', methods=['GET'])
def get_zona_data(nombre_zona):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    try:
        sql = "SELECT zona_id, nombre, descripcion, nivel_id, poligono_geografico FROM ZonasDeSeguridad WHERE nombre = %s"
        cursor.execute(sql, (nombre_zona,))
        zona_data = cursor.fetchone()
        if not zona_data:
            return jsonify({"error": "Zona no encontrada"}), 404
        if zona_data['poligono_geografico']:
            zona_data['poligrafo_geojson'] = json.loads(zona_data['poligono_geografico'])
        else:
            zona_data['poligrafo_geojson'] = None
        del zona_data['poligono_geografico']
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({"error": f"Error al consultar la zona: {err}"}), 500
    except json.JSONDecodeError:
        cursor.close()
        connection.close()
        return jsonify({"error": "Error al decodificar el GeoJSON de la base de datos"}), 500
    cursor.close()
    connection.close()
    return jsonify(zona_data)

@map_bp.route('/ruta/<nombre_ruta>', methods=['GET'])
def get_ruta_data(nombre_ruta):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    try:
        sql = "SELECT ruta_id, nombre_ruta, nivel_id, caminos_poligonos_geograficos FROM RutasDeSeguridad WHERE nombre_ruta = %s"
        cursor.execute(sql, (nombre_ruta,))
        ruta_data = cursor.fetchone()
        if not ruta_data:
            return jsonify({"error": "Ruta no encontrada"}), 404
        if ruta_data['caminos_poligonos_geograficos']:
            ruta_data['caminos_geojson'] = json.loads(ruta_data['caminos_poligonos_geograficos'])
        else:
            ruta_data['caminos_geojson'] = None
        del ruta_data['caminos_poligonos_geograficos']
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({"error": f"Error al consultar la ruta. Detalle: {err}"}), 500
    except json.JSONDecodeError:
        cursor.close()
        connection.close()
        return jsonify({"error": "Error al decodificar el GeoJSON de caminos de la base de datos"}), 500
    cursor.close()
    connection.close()
    return jsonify(ruta_data)

@map_bp.route('/paradas', methods=['GET'])
def get_paradas_con_lineas():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            p.parada_id, p.latitud, p.longitud, p.nombre_calle, p.nivel_id, 
            l.numero_linea 
        FROM ParadasDeColectivo p
        LEFT JOIN Parada_Linea pl ON p.parada_id = pl.parada_id
        LEFT JOIN LineasDeColectivo l ON pl.linea_id = l.linea_id
        ORDER BY p.parada_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()
    paradas = {}
    for row in rows:
        pid = row['parada_id']
        if pid not in paradas:
            paradas[pid] = {
                "parada_id": pid, "latitud": row['latitud'], "longitud": row['longitud'],
                "nombre_calle": row['nombre_calle'], "nivel_id": row['nivel_id'], "lineas": []
            }
        if row['numero_linea']:
            paradas[pid]["lineas"].append(row['numero_linea'])
    return jsonify(list(paradas.values()))