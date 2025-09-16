import React, { useState, useEffect } from 'react';


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
  
  // Estado que actúa como nuestra "base de datos" de usuarios en localStorage.
  const [usersDb, setUsersDb] = useState({});

  // Efecto que se ejecuta una vez al inicio del componente para cargar datos del navegador.
  useEffect(() => {
    // Carga los usuarios y el estado de la sesión si ya existen en localStorage.
    const storedUsers = localStorage.getItem('usersDb');
    if (storedUsers) {
      setUsersDb(JSON.parse(storedUsers));
    }
    const storedUserId = localStorage.getItem('userId');
    const storedLastLogin = localStorage.getItem('lastLogin');

    if (storedUserId) {
      setIsLoggedIn(true);
      setUserId(storedUserId);
      setLastLogin(storedLastLogin);
    }
  }, []);

  // Función para manejar el registro de un nuevo usuario.
  const handleRegister = (e) => {
    e.preventDefault();
    setError('');

    // Validaciones para campos vacíos, nombre de usuario y email duplicados.
    if (!username || !email || !password) {
      setError('Todos los campos son obligatorios.');
      return;
    }
    if (usersDb[username]) {
      setError('Este nombre de usuario ya existe. Elige otro.');
      return;
    }
    const emailExists = Object.values(usersDb).some(user => user.email === email);
    if (emailExists) {
      setError('Este correo electrónico ya está registrado.');
      return;
    }

    // Genera un ID numérico simple y único basado en la cantidad de usuarios.
    const newUserId = Object.keys(usersDb).length + 1;
    const newUser = {
      id: newUserId.toString(),
      email: email,
      password: password,
      lastLogin: null,
    };

    // Actualiza la base de datos de usuarios y la guarda en localStorage.
    const updatedUsersDb = { ...usersDb, [username]: newUser };
    setUsersDb(updatedUsersDb);
    localStorage.setItem('usersDb', JSON.stringify(updatedUsersDb));
    setError('Registro exitoso. ¡Ahora puedes iniciar sesión!');
  };

  // Función para manejar el inicio de sesión.
  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    
    // Busca al usuario por nombre de usuario o por email.
    let user = usersDb[username];
    if (!user) {
      user = Object.values(usersDb).find(u => u.email === email);
    }

    // Si el usuario existe y la contraseña es correcta, inicia la sesión.
    if (user && user.password === password) {
      setIsLoggedIn(true);
      setUserId(user.id);
      
      // Guarda la fecha y hora de inicio de sesión.
      const now = new Date();
      const formattedTime = now.toLocaleString();
      setLastLogin(formattedTime);
      localStorage.setItem('userId', user.id);
      localStorage.setItem('lastLogin', formattedTime);
    } else {
      setError('Usuario, correo o contraseña incorrectos. 😞');
    }
  };

  // Función para cerrar la sesión y limpiar los datos de localStorage.
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserId(null);
    setLastLogin(null);
    localStorage.removeItem('userId');
    localStorage.removeItem('lastLogin');
  };

  // Renderizado condicional: muestra la pantalla de bienvenida o el formulario.
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
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
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