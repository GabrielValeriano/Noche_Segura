import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Components/Login";
import Register from "./Components/Register";
import Dashboard from "./Components/Dashboard";

// --- PASO 1: Importar el nuevo componente ---
// (Asegúrate de haber guardado RecuperarContrasena.jsx dentro de la carpeta /Components/)
import RecuperarContrasena from "./Components/RecuperarContrasena";

function App() {
  return (
    <Router>
      <Routes>
        {/* Rutas existentes */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />

        {/* --- PASO 2: Añadir la nueva ruta --- */}
        {/* Esta es la línea que soluciona el problema de la página en blanco */}
        <Route
          path="/RecuperarContrasena"
          element={<RecuperarContrasena />}
        />
      </Routes>
    </Router>
  );
}

export default App;