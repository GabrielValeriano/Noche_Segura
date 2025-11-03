from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app) # habilita peticiones desde React (http://localhost:5173)


# Conexión a la Base Datos

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
# NUEVA RUTA: Obtener niveles de seguridad por zona
# ===============================================
@app.route('/niveles_seguridad_zonas', methods=['GET'])
def get_niveles_seguridad_zonas():
    """
    Retorna el nivel de seguridad (nivel_id) para las zonas de interés.
    Utiliza la tabla: ZonasDeSeguridad con columnas: nombre y nivel_id.
    Retorna: {"Comuna 8": 1, "Caballito": 3, ...}
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor(dictionary=True)
    
    # Zonas que el frontend espera (React)
    zonas_de_interes = ["Comuna 8", "Caballito", "Puerto Madero"]
    
    try:
        # Construimos la cláusula IN dinámicamente: (%s, %s, %s)
        placeholders = ', '.join(['%s'] * len(zonas_de_interes))
        
        # **AJUSTE DE TABLA Y COLUMNAS:**
        # Se usa ZonasDeSeguridad y las columnas 'nombre' y 'nivel_id'.
        sql = f"SELECT nombre, nivel_id FROM ZonasDeSeguridad WHERE nombre IN ({placeholders})"
        
        cursor.execute(sql, tuple(zonas_de_interes))
        zonas_niveles = cursor.fetchall()
        
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        # Mensaje de error más descriptivo
        return jsonify({"error": f"Error al consultar niveles. Verifique la tabla 'ZonasDeSeguridad' y las columnas 'nombre' y 'nivel_id'. Detalle: {err}"}), 500
    
    cursor.close()
    connection.close()

    # Formatear la respuesta como un diccionario: {nombre_zona: nivel_id}
    # Se usa 'nombre' como clave del diccionario de respuesta
    niveles_map = {zona['nombre']: zona['nivel_id'] for zona in zonas_niveles}
    
    # Si todo va bien, se retorna el mapeo.
    return jsonify(niveles_map)

# ===============================================
# RUTA 2: OBTENER DATA COMPLETA DE ZONA (INCLUYE GEOMETRÍA)
# ===============================================
@app.route('/zona/<nombre_zona>', methods=['GET'])
def get_zona_data(nombre_zona):
    """
    Retorna toda la información de una zona, incluyendo el GeoJSON (poligono_geografico).
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor(dictionary=True)
    
    try:
        # Recuperamos todas las columnas necesarias, incluyendo el polígono como texto
        sql = "SELECT zona_id, nombre, descripcion, nivel_id, poligono_geografico FROM ZonasDeSeguridad WHERE nombre = %s"
        
        cursor.execute(sql, (nombre_zona,))
        zona_data = cursor.fetchone()
        
        if not zona_data:
            return jsonify({"error": "Zona no encontrada"}), 404

        # El campo poligono_geografico es un string (GeoJSON). 
        # Lo convertimos de nuevo a un objeto JSON para incluirlo en la respuesta.
        if zona_data['poligono_geografico']:
            zona_data['poligrafo_geojson'] = json.loads(zona_data['poligono_geografico'])
        else:
            zona_data['poligrafo_geojson'] = None
        
        # Eliminamos el string largo original si ya convertimos el objeto
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

    # Retorna todos los datos, incluido el GeoJSON ya como objeto
    return jsonify(zona_data)

# -----------------------------------------------
# Endpoint de paradas con líneas (¡CORREGIDO!)
# -----------------------------------------------
@app.route('/paradas', methods=['GET'])
def get_paradas_con_lineas():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = connection.cursor(dictionary=True)
    
    # --- INICIO DE CORRECCIÓN ---
    # 1. La consulta ahora une las 3 tablas correctas:
    #    ParadasDeColectivo -> Parada_Linea -> LineasDeColectivo
    # 2. Seleccionamos 'l.numero_linea' para obtener el nombre (ej: "55")
    query = """
        SELECT 
            p.parada_id, p.latitud, p.longitud, p.nombre_calle, p.nivel_id, 
            l.numero_linea 
        FROM 
            ParadasDeColectivo p
        LEFT JOIN 
            Parada_Linea pl ON p.parada_id = pl.parada_id
        LEFT JOIN 
            LineasDeColectivo l ON pl.linea_id = l.linea_id
        ORDER BY 
            p.parada_id
    """
    # --- FIN DE CORRECCIÓN ---
    
    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()

    # Agrupar líneas por parada (Lógica de agrupación en Python)
    paradas = {}
    for row in rows:
        pid = row['parada_id']
        if pid not in paradas:
            paradas[pid] = {
                "parada_id": pid,
                "latitud": row['latitud'],
                "longitud": row['longitud'],
                "nombre_calle": row['nombre_calle'],
                "nivel_id": row['nivel_id'],
                "lineas": []
            }
        
        # --- INICIO DE CORRECCIÓN ---
        # 3. Usamos la columna 'numero_linea' (en lugar de 'linea')
        if row['numero_linea']:
            paradas[pid]["lineas"].append(row['numero_linea'])
        # --- FIN DE CORRECCIÓN ---

    return jsonify(list(paradas.values()))

# Rutas de Usuarios (Sin cambios)

# GET Da todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT usuario_id, nombre_usuario, email, fecha_registro FROM Usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify(usuarios)

# POST: crear un usuario (hash de contraseña)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    if not all(k in data for k in ("nombre_usuario", "email", "contrasena")):
        return jsonify({"error": "Faltan datos"}), 400

    nombre_usuario = data['nombre_usuario']
    email = data['email']
    contraseña_hash = generate_password_hash(data['contrasena'])

    connection = get_db_connection()
    if not connection: 
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor(dictionary=True)

    # ¿ usuario o email duplicado ?
    cursor.execute("SELECT * FROM Usuarios WHERE nombre_usuario = %s OR email = %s", (nombre_usuario, email))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        connection.close()
        return jsonify({"error": "El nombre de usuario o email ya está registrado"}), 400

    #Inserta un nuevo usuario
    sql = "INSERT INTO Usuarios (nombre_usuario, email, contraseña_hash) VALUES (%s, %s, %s)"
    val = (nombre_usuario, email, contraseña_hash)

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
    
# PUT actualizar usuario
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
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

# DELETE elimina los usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
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

# POST login de usuario
@app.route('/login', methods=['POST'])
def login_usuario():
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

#Ejecutar la app

if __name__ == '__main__':
    # Usamos host='0.0.0.0' para que sea accesible desde el frontend de React
    app.run(debug=True, host='0.0.0.0', port=5000) # Aseguramos el puerto 5000