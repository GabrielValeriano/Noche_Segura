import React, { useState } from "react";
import "./Menu.css";

const Menu = ({ onLogout, user }) => {
  const [showWelcome, setShowWelcome] = useState(true);

  const opciones = ["Mapa del Delito", "Reportes", "Configuración"];

  return (
    <div className="menu-container">
      {showWelcome ? (
        <div className="welcome-card">
          <h2>¡Bienvenido, {user?.nombre || "Usuario"}!</h2>
          <p>Tu ID de usuario es: {user?.id}</p>
          <p>Último inicio de sesión: {new Date().toLocaleString()}</p>
          <button onClick={() => setShowWelcome(false)}>Entrar al Menú</button>
        </div>
      ) : (
        <div>
          <header className="menu-header">
            <h2>Menú Principal</h2>
          </header>
          <ul>
            {opciones.map((op, i) => (
              <li key={i}>
                <button>{op}</button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Menu;
