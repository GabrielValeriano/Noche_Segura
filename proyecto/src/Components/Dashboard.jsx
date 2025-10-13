// src/pages/Dashboard.jsx
import { useState, useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./Dashboard.css";

export default function Dashboard() {
  const [geoData, setGeoData] = useState(null); // Caminos peatonales
  const [zonaData, setZonaData] = useState(null); // Zona seleccionada
  const [zonaSeleccionada, setZonaSeleccionada] = useState(null);

  // Cargar caminos peatonales
  useEffect(() => {
    fetch("/data/caminos-parquedelaCiudad.geojson")
      .then((response) => response.json())
      .then((data) => setGeoData(data))
      .catch((err) => console.error("Error cargando GeoJSON de caminos:", err));
  }, []);

  // Cargar zonas disponibles (ejemplo: comuna 8)
  const zonasDisponibles = {
    "Comuna 8": "/data2/comuna8.geojson",
    Caballito: "/data2/caballito.geojson",
  };

  const manejarSeleccionZona = (nombreZona) => {
    setZonaSeleccionada(nombreZona);
    fetch(zonasDisponibles[nombreZona])
      .then((response) => response.json())
      .then((data) => setZonaData(data))
      .catch((err) => console.error("Error cargando GeoJSON de zona:", err));
  };

  // Estilo de caminos
  const estiloCaminos = {
    color: "orange",
    weight: 3,
    dashArray: "4.5, 4.5", // punteado
  };

  // Estilo de zona
  const estiloZona = {
    color: "#853ba7ff",
    fillColor: "#4c0d5cff",
    fillOpacity: 0.3,
    weight: 2,
  };

  return (
    <div className="dashboard">
      {/* Panel lateral de selección */}
      <div className="sidebar">
        <h3>Zonas disponibles</h3>
        {Object.keys(zonasDisponibles).map((nombre) => (
          <button
            key={nombre}
            className={`zona-btn ${
              zonaSeleccionada === nombre ? "active" : ""
            }`}
            onClick={() => manejarSeleccionZona(nombre)}
          >
            {nombre}
          </button>
        ))}
      </div>

      {/* Mapa principal */}
      <MapContainer
        center={[-34.68, -58.46]} // Parque de la Ciudad
        zoom={14}
        className="map"
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        />

        {/* Caminos peatonales */}
        {geoData && <GeoJSON data={geoData} style={estiloCaminos} />}

        {/* Zona seleccionada */}
        {zonaData && <GeoJSON data={zonaData} style={estiloZona} />}
      </MapContainer>
    </div>
  );
}
