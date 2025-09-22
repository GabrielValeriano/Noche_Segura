import React, { useState } from "react";
import "./App.css";
import Login from "./Components/Login";
import Menu from "./Components/Menu/Menu";

function App() {
  const [showMenu, setShowMenu] = useState(false);

  const handleContinue = () => setShowMenu(true);
  const handleLogout = () => setShowMenu(false);

  return (
    <div className="App">
      {!showMenu ? (
        <Login onContinue={handleContinue} />
      ) : (
        <Menu onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
