import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css"; // importamos los estilos

const Register = () => {
  // Estados para todos los campos del formulario
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [confirmarContrasena, setConfirmarContrasena] = useState(""); // <-- NUEVO
  const [preguntaSeguridad, setPreguntaSeguridad] = useState(""); // <-- NUEVO
  const [respuestaSeguridad, setRespuestaSeguridad] = useState(""); // <-- NUEVO

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate(); // para redirigir al login

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // --- VALIDACIÓN DEL FRONTEND ---
    if (
      !nombreUsuario ||
      !email ||
      !contrasena ||
      !confirmarContrasena ||
      !preguntaSeguridad ||
      !respuestaSeguridad
    ) {
      setError("Todos los campos son obligatorios");
      return;
    }

    if (contrasena !== confirmarContrasena) {
      setError("Las contraseñas no coinciden");
      return;
    }

    if (contrasena.length < 6) {
        setError("La contraseña debe tener al menos 6 caracteres.");
        return;
    }
    // --- FIN VALIDACIÓN ---


    try {
      const response = await fetch("http://localhost:5000/usuarios", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // --- BODY ACTUALIZADO (ENVIANDO LOS 5 CAMPOS) ---
        body: JSON.stringify({
          nombre_usuario: nombreUsuario,
          email: email,
          contrasena: contrasena,
          pregunta_seguridad: preguntaSeguridad, // <-- NUEVO
          respuesta_seguridad: respuestaSeguridad   // <-- NUEVO
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Error al registrarse");
        return;
      }

      setSuccess("¡Registro exitoso! Redirigiendo al login...");

      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        navigate("/");
      }, 2000);

    } catch (err) {
      setError("Error de conexión con el servidor");
    }
  };

  return (
    <div className="register-container">
      <h2>Registrarse</h2>
      <form onSubmit={handleRegister}>
        <div>
          <input
            type="text"
            value={nombreUsuario}
            placeholder="Nombre de usuario"
            onChange={(e) => setNombreUsuario(e.target.value)}
            required
          />
        </div>
        <div>
          <input
            type="email"
            value={email}
            placeholder="Correo electrónico"
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <input
            type="password"
            value={contrasena}
            placeholder="Contraseña (mín. 6 caracteres)"
            onChange={(e) => setContrasena(e.target.value)}
            required
          />
        </div>

        {/* --- CAMPO NUEVO --- */}
        <div>
          <input
            type="password"
            value={confirmarContrasena}
            placeholder="Confirmar contraseña"
            onChange={(e) => setConfirmarContrasena(e.target.value)}
            required
          />
        </div>

        {/* --- CAMPO NUEVO (PREGUNTA) --- */}
        <div>
          {/* El 'value=""' y 'disabled' hacen que "Elige..." no sea una opción seleccionable */}
          <select 
            value={preguntaSeguridad}
            onChange={(e) => setPreguntaSeguridad(e.target.value)}
            required
            // 'invalid' se aplica si el valor es "" (el default)
            // esto ayuda a que el placeholder 'Elige...' se vea grisado
            style={preguntaSeguridad === "" ? { color: '#757575' } : { color: '#333' }}
          >
            <option value="" disabled>Elige una pregunta de seguridad...</option>
            <option value="Nombre de tu primera mascota">¿Nombre de tu primera mascota?</option>
            <option value="Ciudad donde naciste">¿Ciudad donde naciste?</option>
            <option value="Nombre de tu escuela primaria">¿Nombre de tu escuela primaria?</option>
          </select>
        </div>

        {/* --- CAMPO NUEVO (RESPUESTA) --- */}
        <div>
          <input
            type="text"
            value={respuestaSeguridad}
            placeholder="Tu respuesta secreta"
            onChange={(e) => setRespuestaSeguridad(e.target.value)}
            required
          />
        </div>

        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}

        <div className="button-group">
          <button type="submit">Registrarse</button>
        </div>
      </form>

      {/* Texto para redirigir al login */}
      <h4 style={{marginTop: '20px', color: '#555'}}>¿Ya tenés cuenta?</h4>
      <a href="/">Iniciar sesión</a>
    </div>
  );
};

export default Register;