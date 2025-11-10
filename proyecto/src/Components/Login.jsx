import React, { useState } from "react";
import "./Login.css"; // importamos los estilos

const Login = () => {
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [usuario, setUsuario] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, contrasena }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Error al iniciar sesión");
        return;
      }

    localStorage.setItem("usuario", JSON.stringify(data));
    window.location.href = "/Dashboard"; // redirige al dashboard

    } catch (err) {
      setError("Error de conexión con el servidor");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("usuario");
    setUsuario(null);
  };

  if (usuario) {
    return (
      <div className="login-container2">
        <h2>Bienvenido {usuario.nombre_usuario}</h2>
        <p className="color">Correo: {usuario.email}</p>
        <button onClick={handleLogout}>Cerrar sesión</button>
      </div>
    );
  }

  return (
    <div className="login-container">
      <h2>Iniciar Sesión</h2>
      <form onSubmit={handleLogin}>
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

        {/* --- NUEVO ENLACE DE RECUPERAR CONTRASEÑA --- */}
        <div className="forgot-password-link">
          {/* Este enlace debe apuntar a la ruta de tu componente de recuperación */}
          <a href="/RecuperarContrasena">¿Olvidaste tu contraseña?</a>
        </div>

        {/* TEXTO Y LINK DE REGISTRO EXACTAMENTE COMO ESTABA */}
        <div>
          <h4>¿No tiene cuenta?</h4>
          <a href="/Register">Registrate</a>
        </div>
        <div className="button-group">
          <button type="submit">Ingresar</button>
        </div>
        {error && <p className="error-message">{error}</p>}

      </form>
    </div>
  );
};

export default Login;