import React, { useState } from "react";
// Reutilizamos los mismos estilos del Register para no duplicar CSS
import "./Register.css"; 

const RecuperarContrasena = () => {
  // --- Estados ---
  const [paso, setPaso] = useState(1); // 1: Buscar user, 2: Responder pregunta
  
  // Paso 1
  const [identificador, setIdentificador] = useState("");
  
  // Paso 2
  const [pregunta, setPregunta] = useState("");
  const [respuesta, setRespuesta] = useState("");
  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [confirmarContrasena, setConfirmarContrasena] = useState("");

  // Mensajes
  const [error, setError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  // --- Lógica del Paso 1: Buscar la pregunta ---
  const handleBuscarPregunta = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:5000/obtener-pregunta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identificador }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "No se pudo encontrar al usuario.");
        return;
      }

      // Éxito: guardamos la pregunta y avanzamos al paso 2
      setPregunta(data.pregunta);
      setPaso(2);

    } catch (err) {
      setError("Error de conexión con el servidor.");
    }
  };

  // --- Lógica del Paso 2: Restablecer la contraseña ---
  const handleRestablecer = async (e) => {
    e.preventDefault();
    setError("");
    setMensajeExito("");

    // 1. Validar contraseñas en el frontend
    if (nuevaContrasena !== confirmarContrasena) {
      setError("Las nuevas contraseñas no coinciden.");
      return;
    }
    if (nuevaContrasena.length < 6) {
        setError("La nueva contraseña debe tener al menos 6 caracteres.");
        return;
    }

    // 2. Enviar todo al backend
    try {
        const response = await fetch("http://localhost:5000/restablecer-por-pregunta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                identificador: identificador,
                respuesta_seguridad: respuesta,
                nueva_contrasena: nuevaContrasena
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            setError(data.error || "No se pudo restablecer la contraseña.");
            return;
        }

        // Éxito final
        setMensajeExito("¡Contraseña actualizada! Redirigiendo al Login...");
        setTimeout(() => {
            window.location.href = "/"; // Volvemos al Login
        }, 3000);

    } catch (err) {
        setError("Error de conexión con el servidor.");
    }
  };

  return (
    // Usamos 'register-container' para reciclar el CSS
    <div className="register-container">
      <h2>Recuperar Contraseña</h2>

      {/* --- FORMULARIO DEL PASO 1 --- */}
      {paso === 1 && (
        <form onSubmit={handleBuscarPregunta}>
          <p style={{color: '#555', fontSize: '14px', textAlign: 'center'}}>
            Ingresa tu email o nombre de usuario para buscar tu pregunta de seguridad.
          </p>
          <div>
            <input
              type="text"
              value={identificador}
              placeholder="Email o Nombre de usuario"
              onChange={(e) => setIdentificador(e.target.value)}
              required
            />
          </div>
          
          {error && <p className="error-message">{error}</p>}

          <div className="button-group">
            <button type="submit">Buscar</button>
          </div>
        </form>
      )}

      {/* --- FORMULARIO DEL PASO 2 --- */}
      {paso === 2 && (
        <form onSubmit={handleRestablecer}>
          <div className="pregunta-container">
            <label style={{color: '#555', fontSize: '14px'}}>Tu pregunta de seguridad:</label>
            <p style={{fontWeight: 600, color: '#333', marginTop: '5px'}}>"{pregunta}"</p>
          </div>
          
          <div>
            <input
              type="text"
              value={respuesta}
              placeholder="Tu respuesta secreta"
              onChange={(e) => setRespuesta(e.target.value)}
              required
            />
          </div>
          <div>
            <input
              type="password"
              value={nuevaContrasena}
              placeholder="Nueva contraseña (mín. 6 caracteres)"
              onChange={(e) => setNuevaContrasena(e.target.value)}
              required
            />
          </div>
          <div>
            <input
              type="password"
              value={confirmarContrasena}
              placeholder="Confirmar nueva contraseña"
              onChange={(e) => setConfirmarContrasena(e.target.value)}
              required
            />
          </div>

          {error && <p className="error-message">{error}</p>}
          {mensajeExito && <p className="success-message">{mensajeExito}</p>}

          <div className="button-group">
            <button type="submit">Restablecer Contraseña</button>
          </div>
        </form>
      )}

      {/* Enlace para volver */}
      <div>
        <h4>¿Recordaste tu contraseña?</h4>
        <a href="/">Inicia Sesión</a>
      </div>
    </div>
  );
};

export default RecuperarContrasena;