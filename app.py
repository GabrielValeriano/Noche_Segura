from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/Noche_Seguridad"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# Modelos
# -------------------------
class Usuario(db.Model):
    __tablename__ = "Usuarios"
    usuario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.now())
    contrasena_hash = db.Column(db.String(255), nullable=False)


# -------------------------
# Rutas / Endpoints
# -------------------------

# GET: obtener todos los usuarios (sin el hash)
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    resultado = [
        {
            "usuario_id": u.usuario_id,
            "nombre_usuario": u.nombre_usuario,
            "email": u.email,
            "fecha_registro": u.fecha_registro
        }
        for u in usuarios
    ]
    return jsonify(resultado)


# POST: crear un usuario (hash de contraseña)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    if not all(k in data for k in ("nombre_usuario", "email", "contrasena")):
        return jsonify({"error": "Faltan datos"}), 400

    nuevo_usuario = Usuario(
        nombre_usuario = data['nombre_usuario'],
        email = data['email'],
        contrasena_hash = generate_password_hash(data['contrasena'])
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "usuario_id": nuevo_usuario.usuario_id,
        "nombre_usuario": nuevo_usuario.nombre_usuario,
        "email": nuevo_usuario.email,
        "fecha_registro": nuevo_usuario.fecha_registro
    }), 201


# PUT: actualizar usuario
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json()

    if "nombre_usuario" in data:
        usuario.nombre_usuario = data['nombre_usuario']
    if "email" in data:
        usuario.email = data['email']

    db.session.commit()
    return jsonify({"mensaje": "Usuario actualizado"})


# DELETE: eliminar usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario eliminado"})


# -------------------------
# Ejecutar la app
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # crea las tablas si no existen
    app.run(debug=True)
