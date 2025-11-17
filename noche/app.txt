from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app) # habilita peticiones desde React (http://localhost:5173)


# Conexión a la Base Datos (Sin cambios)
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="10.9.120.5",
            port="3306",
            user="nocheSegu",
            password="noche1234",
            database="nocheSegura"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

# ===============================================
# RUTAS DE MAPA (Zonas, Rutas, Paradas) - Sin cambios
# ===============================================
@app.route('/niveles_seguridad_zonas', methods=['GET'])
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

@app.route('/zona/<nombre_zona>', methods=['GET'])
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

@app.route('/ruta/<nombre_ruta>', methods=['GET'])
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

@app.route('/paradas', methods=['GET'])
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

# ===============================================
# RUTAS DE USUARIOS (Login y CRUD)
# ===============================================

# GET Da todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    # ... (Tu código existente, sin cambios) ...
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT usuario_id, nombre_usuario, email, fecha_registro FROM Usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(usuarios)


# POST: crear un usuario (MODIFICADO para Preguntas de Seguridad)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    # AHORA PEDIMOS LOS 5 CAMPOS
    if not all(k in data for k in ("nombre_usuario", "email", "contrasena", "pregunta_seguridad", "respuesta_seguridad")):
        return jsonify({"error": "Faltan datos (se requieren 5 campos)"}), 400

    nombre_usuario = data['nombre_usuario']
    email = data['email']
    contraseña_hash = generate_password_hash(data['contrasena'])
    
    # --- CAMBIO ---
    # Hasheamos la respuesta de seguridad, igual que la contraseña
    pregunta = data['pregunta_seguridad']
    respuesta_hash = generate_password_hash(data['respuesta_seguridad'])
    # --- FIN CAMBIO ---

    connection = get_db_connection()
    if not connection: 
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuarios WHERE nombre_usuario = %s OR email = %s", (nombre_usuario, email))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        connection.close()
        return jsonify({"error": "El nombre de usuario o email ya está registrado"}), 400

    # --- CAMBIO ---
    # Insertamos los 5 campos
    sql = """
        INSERT INTO Usuarios (nombre_usuario, email, contraseña_hash, pregunta_seguridad, respuesta_seguridad_hash) 
        VALUES (%s, %s, %s, %s, %s)
    """
    val = (nombre_usuario, email, contraseña_hash, pregunta, respuesta_hash)
    # --- FIN CAMBIO ---

    try:
        cursor.execute(sql, val)
        connection.commit()
        usuario_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            "usuario_id": usuario_id,
            "nombre_usuario": nombre_usuario,
            "email": email
        }), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({"error": f"Error al crear usuario: {err}"}), 500
    
# PUT actualizar usuario (Sin cambios)
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    # ... (Tu código existente, sin cambios) ...
    data = request.get_json()
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor()
    updates = []
    vals = []
    if "nombre_usuario" in data:
        updates.append("nombre_usuario = %s")
        vals.append(data['nombre_usuario'])
    if "email" in data:
        updates.append("email = %s")
        vals.append(data['email'])
    if not updates:
        return jsonify({"mensaje": "No se proporcionaron datos para actualizar"}), 400
    sql = "UPDATE Usuarios SET " + ", ".join(updates) + " WHERE usuario_id = %s"
    vals.append(id)
    try:
        cursor.execute(sql, tuple(vals))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"mensaje": "Usuario actualizado"})
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al actualizar: {err}"}), 500


# DELETE elimina los usuario (Sin cambios)
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    # ... (Tu código existente, sin cambios) ...
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor()
    sql = "DELETE FROM Usuarios WHERE usuario_id = %s"
    val = (id,)
    try:
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"mensaje": "Usuario eliminado"})
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al eliminar: {err}"}), 500

# POST login de usuario (Sin cambios)
@app.route('/login', methods=['POST'])
def login_usuario():
    # ... (Tu código existente, sin cambios) ...
    data = request.get_json()
    if not all(k in data for k in ("email", "contrasena")):
        return jsonify({"error": "Faltan datos"}), 400
    email = data['email']
    contrasena = data['contrasena']
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT usuario_id, nombre_usuario, email, contraseña_hash FROM Usuarios WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if not user:
        return jsonify({"error": "El correo no está registrado"}), 401
    if not check_password_hash(user['contraseña_hash'], contrasena):
        return jsonify({"error": "Contraseña incorrecta"}), 401
    return jsonify({
        "mensaje": "Login exitoso",
        "usuario_id": user['usuario_id'],
        "nombre_usuario": user['nombre_usuario'],
        "email": user['email']
    }), 200

# ===============================================
# --- NUEVAS RUTAS DE RECUPERACIÓN (Versión simple) ---
# ===============================================

@app.route('/obtener-pregunta', methods=['POST'])
def obtener_pregunta():
    """
    Paso 1: El usuario pone su nombre de usuario o email.
    Devolvemos la pregunta de seguridad que guardó.
    """
    data = request.get_json()
    identificador = data.get('identificador') # Puede ser email o nombre_usuario
    if not identificador:
        return jsonify({"error": "Se requiere email o nombre de usuario"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT pregunta_seguridad FROM Usuarios WHERE email = %s OR nombre_usuario = %s"
    cursor.execute(sql, (identificador, identificador))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not user['pregunta_seguridad']:
        # Ocultamos si el usuario existe o no, por seguridad
        return jsonify({"error": "No se encontró un usuario con ese identificador o no tiene pregunta de seguridad."}), 404
    
    return jsonify({"pregunta": user['pregunta_seguridad']}), 200


@app.route('/restablecer-por-pregunta', methods=['POST'])
def restablecer_por_pregunta():
    """
    Paso 2: El usuario envía su identificador, la respuesta a la pregunta,
    y la nueva contraseña.
    """
    data = request.get_json()
    identificador = data.get('identificador')
    respuesta = data.get('respuesta_seguridad')
    nueva_contrasena = data.get('nueva_contrasena')

    if not all([identificador, respuesta, nueva_contrasena]):
        return jsonify({"error": "Faltan datos"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    # 1. Buscamos al usuario y su RESPUESTA HASHEADA
    sql_find = "SELECT usuario_id, respuesta_seguridad_hash FROM Usuarios WHERE email = %s OR nombre_usuario = %s"
    cursor.execute(sql_find, (identificador, identificador))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        connection.close()
        return jsonify({"error": "Identificador incorrecto"}), 401
    
    # 2. Verificamos que la respuesta sea correcta (usando el hash)
    if not check_password_hash(user['respuesta_seguridad_hash'], respuesta):
        cursor.close()
        connection.close()
        return jsonify({"error": "Respuesta de seguridad incorrecta"}), 401

    # 3. Si la respuesta es correcta, actualizamos la contraseña
    try:
        nueva_contraseña_hash = generate_password_hash(nueva_contrasena)
        sql_update = "UPDATE Usuarios SET contraseña_hash = %s WHERE usuario_id = %s"
        cursor.execute(sql_update, (nueva_contraseña_hash, user['usuario_id']))
        connection.commit()
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({"error": f"Error al actualizar la contraseña: {err}"}), 500
    
    cursor.close()
    connection.close()
    
    return jsonify({"mensaje": "Contraseña actualizada con éxito"}), 200


#Ejecutar la app

if __name__ == '__main__':
    # Usamos host='0.0.0.0' para que sea accesible desde el frontend de React
    app.run(debug=True, host='0.0.0.0', port=5000)