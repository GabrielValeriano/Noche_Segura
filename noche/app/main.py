from app import create_app

# Creamos la app usando la fábrica
app = create_app()

#Ejecutar la app
if __name__ == '__main__':
    # Usamos host='0.0.0.0' para que sea accesible desde el frontend de React
    app.run(debug=True, host='0.0.0.0', port=5000)