import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css"; // CSS para el banner

const Dashboard = () => {
  const [usuario, setUsuario] = useState(
    JSON.parse(localStorage.getItem("usuario"))
  );

  const handleLogout = () => {
    localStorage.removeItem("usuario");
    window.location.href = "/"; // vuelve al login
  };

  return (
    <div className="dashboard-container">
      {/* BANNER SUPERIOR */}
      <header className="dashboard-banner">
        <div className="banner-left">
          <h3>Bienvenido, {usuario.nombre_usuario}</h3>
        </div>
        <div className="banner-right">
          <Link to="/opcion1">Opción 1</Link>
          <Link to="/opcion2">Opción 2</Link>
          <Link to="/opcion3">Opción 3</Link>
          <button onClick={handleLogout}>Cerrar sesión</button>
        </div>
      </header>

      {/* CONTENIDO PRINCIPAL */}
      <main className="dashboard-content">
        <h2>Panel principal</h2>
        <p>Seleccioná una opción del banner para navegar.</p>
      </main>
    </div>
  );
};

export default Dashboard;
