from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
import mysql.connector

app = Flask(__name__)

# Función para conectarse a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="10.9.120.5",
            port=3306,  # Asegúrate de que este es el puerto correcto de tu servidor MySQL
            user="nocheSegu",
            password="noche1234",
            database="nocheSegura"

        )
        return connection
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error de conexión: {err}"}), 500


# -------------------------
# Rutas / Endpoints
# -------------------------

# GET: obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    connection = get_db_connection()
    if not connection: return

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT usuario_id, nombre_usuario, email, fecha_registro FROM Usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # El diccionario=True hace que los datos ya vengan en formato JSON
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
    if not connection: return

    cursor = connection.cursor()
    sql = "INSERT INTO Usuarios (nombre_usuario, email, contraseña_hash) VALUES (%s, %s, %s)"
    val = (nombre_usuario, email, contraseña_hash)
    
    try:
        cursor.execute(sql, val)
        connection.commit()
        
        # Opcional: obtener el ID del usuario recién creado
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


# PUT: actualizar usuario
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.get_json()
    
    connection = get_db_connection()
    if not connection: return

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

# DELETE: eliminar usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    connection = get_db_connection()
    if not connection: return
    
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


# -------------------------
# Ejecutar la app
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)