from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="nocheSegu",
            password="noche1234",
            database="nocheSegura"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

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

    try:
        cursor = connection.cursor()
        sql = "INSERT INTO Usuarios (nombre_usuario, email, contraseña_hash) VALUES (%s, %s, %s)"
        val = (nombre_usuario, email, contraseña_hash)
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
        return jsonify({"error": f"Error al crear usuario: {err}"}), 500

# POST: ruta para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ('usuario_o_email', 'contrasena')):
        return jsonify({"error": "Faltan datos"}), 400

    identificador = data['usuario_o_email']
    contrasena_enviada = data['contrasena']

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        sql = "SELECT * FROM Usuarios WHERE nombre_usuario = %s OR email = %s"
        val = (identificador, identificador)
        cursor.execute(sql, val)
        usuario = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if usuario is None or not check_password_hash(usuario['contraseña_hash'], contrasena_enviada):
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
        
        return jsonify({
            "usuario_id": usuario['usuario_id'],
            "nombre_usuario": usuario['nombre_usuario'],
            "email": usuario['email']
        }), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error de autenticación: {err}"}), 500


# -------------------------
# Ejecutar la app
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)