// src/pages/Dashboard.jsx
import { useState, useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./Dashboard.css";

export default function Dashboard() {
  const [geoData, setGeoData] = useState(null);

  // Cargar el archivo GeoJSON desde /public/data/
  useEffect(() => {
    fetch("/data/caminos-reserva.geojson")
      .then((response) => response.json())
      .then((data) => setGeoData(data))
      .catch((err) => console.error("Error cargando GeoJSON:", err));
  }, []);

  // Estilo para los caminos
  const estiloCaminos = {
    color: "orange",
    weight: 3,
    dashArray: "4.5, 4.5", // punteado
  };

  return (
    <div className="dashboard">
      <MapContainer
        center={[-34.67975, -58.458611]} // Reserva Costanera Norte
        zoom={15}
        className="map"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        />

        {/* Renderizar GeoJSON cuando esté cargado */}
        {geoData && <GeoJSON data={geoData} style={estiloCaminos} />}
      </MapContainer>
    </div>
  );
}
