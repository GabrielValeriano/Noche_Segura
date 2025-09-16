import React, { useState } from 'react';


// Componente principal para el login y registro de usuarios.
const Login = () => {
  // Estados para manejar los datos del formulario y el estado de la aplicación.
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userId, setUserId] = useState(null);
  const [lastLogin, setLastLogin] = useState(null);

  // Función para manejar el registro de un nuevo usuario.
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !email || !password) {
      setError('Todos los campos son obligatorios.');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/usuarios', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre_usuario: username,
          email: email,
          contrasena: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al registrar el usuario.');
      }
      
      setError('Registro exitoso. ¡Ahora puedes iniciar sesión!');
      // Limpia los campos del formulario
      setUsername('');
      setEmail('');
      setPassword('');
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  // Función para manejar el inicio de sesión.
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          usuario_o_email: username || email, 
          contrasena: password,
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Usuario o contraseña incorrectos. 😞');
      }

      setIsLoggedIn(true);
      setUserId(data.usuario_id);
      setLastLogin(new Date().toLocaleString());
      setUsername(data.nombre_usuario);
      setEmail(data.email);
      
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  // Función para cerrar la sesión
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserId(null);
    setLastLogin(null);
    setUsername('');
    setEmail('');
    setPassword('');
  };
  
  if (isLoggedIn) {
    return (
      <div className="login-container">
        <h2>¡Bienvenido, {username}!</h2>
        <p className='color'>Tu ID de usuario es: <strong>{userId}</strong></p>
        <p className='color'>Último inicio de sesión: <strong>{lastLogin}</strong></p>
        <button onClick={handleLogout}>Cerrar Sesión</button>
      </div>
    );
  }

  return (
    <div className="login-container">
      <h2>Iniciar Sesión o Registrarse</h2>
      <form>
        <div className="form-group">
          <label htmlFor="username">Usuario</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Contraseña</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <div className="button-group">
          <button type="button" onClick={handleRegister}>Registrarse</button>
          <button type="button" onClick={handleLogin}>Entrar</button>
        </div>
      </form>
    </div>
  );
};

export default Login;