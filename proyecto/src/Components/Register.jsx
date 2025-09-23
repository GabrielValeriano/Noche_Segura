import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css"; // importamos los estilos

const Register = () => {
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate(); // para redirigir al login

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!nombreUsuario || !email || !contrasena) {
      setError("Todos los campos son obligatorios");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/usuarios", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nombre_usuario: nombreUsuario,
          email: email,
          contrasena: contrasena,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Error al registrarse");
        return;
      }

      setSuccess("Registro exitoso! Ahora podés iniciar sesión.");

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
            placeholder="Contraseña"
            onChange={(e) => setContrasena(e.target.value)}
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
      <h4 className="color2">¿Ya tenés cuenta?</h4>
      <a href="/">Iniciar sesión</a>
    </div>
  );
};

export default Register;
