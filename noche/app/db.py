import mysql.connector

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