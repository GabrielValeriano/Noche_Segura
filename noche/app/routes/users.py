from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app.db import get_db_connection # Importamos la conexión desde app/db.py

# Creamos el Blueprint para usuarios
users_bp = Blueprint('users', __name__)

# ===============================================
# RUTAS DE USUARIOS (Login y CRUD)
# ===============================================

# GET Da todos los usuarios
@users_bp.route('/usuarios', methods=['GET'])
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


# POST: crear un usuario (MODIFICADO para Preguntas de Seguridad)
@users_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    # AHORA PEDIMOS LOS 5 CAMPOS
    if not all(k in data for k in ("nombre_usuario", "email", "contrasena", "pregunta_seguridad", "respuesta_seguridad")):
        return jsonify({"error": "Faltan datos (se requieren 5 campos)"}), 400

    nombre_usuario = data['nombre_usuario']
    email = data['email']
    contraseña_hash = generate_password_hash(data['contrasena'])
    
    # Hasheamos la respuesta de seguridad, igual que la contraseña
    pregunta = data['pregunta_seguridad']
    respuesta_hash = generate_password_hash(data['respuesta_seguridad'])

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

    sql = """
        INSERT INTO Usuarios (nombre_usuario, email, contraseña_hash, pregunta_seguridad, respuesta_seguridad_hash) 
        VALUES (%s, %s, %s, %s, %s)
    """
    val = (nombre_usuario, email, contraseña_hash, pregunta, respuesta_hash)

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
@users_bp.route('/usuarios/<int:id>', methods=['PUT'])
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
@users_bp.route('/usuarios/<int:id>', methods=['DELETE'])
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
@users_bp.route('/login', methods=['POST'])
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

# ===============================================
# --- NUEVAS RUTAS DE RECUPERACIÓN (Versión simple) ---
# ===============================================

@users_bp.route('/obtener-pregunta', methods=['POST'])
def obtener_pregunta():
    data = request.get_json()
    identificador = data.get('identificador')
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
        return jsonify({"error": "No se encontró un usuario con ese identificador o no tiene pregunta de seguridad."}), 404
    
    return jsonify({"pregunta": user['pregunta_seguridad']}), 200


@users_bp.route('/restablecer-por-pregunta', methods=['POST'])
def restablecer_por_pregunta():
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
    
    sql_find = "SELECT usuario_id, respuesta_seguridad_hash FROM Usuarios WHERE email = %s OR nombre_usuario = %s"
    cursor.execute(sql_find, (identificador, identificador))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        connection.close()
        return jsonify({"error": "Identificador incorrecto"}), 401
    
    if not check_password_hash(user['respuesta_seguridad_hash'], respuesta):
        cursor.close()
        connection.close()
        return jsonify({"error": "Respuesta de seguridad incorrecta"}), 401

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