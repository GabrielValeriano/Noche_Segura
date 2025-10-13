// src/pages/Dashboard.jsx
import { useState, useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet"; 
import "leaflet/dist/leaflet.css";
import L from 'leaflet'; // Necesario para L.geoJson() y getBounds()
import "./Dashboard.css";

// ----------------------------------------------------
// Componente para ajustar la vista del mapa (Zoom)
// ----------------------------------------------------
function MapZoomer({ zonaData }) {
  const map = useMap(); 

  useEffect(() => {
    if (zonaData) {
      const geoJsonLayer = L.geoJson(zonaData);
      const bounds = geoJsonLayer.getBounds();
      
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] }); 
      }
    }
  }, [zonaData, map]); 

  return null; 
}
// ----------------------------------------------------


export default function Dashboard() {
  const [geoData, setGeoData] = useState(null); // Caminos peatonales (Datos GeoJSON)
  const [zonaData, setZonaData] = useState(null); // Zona seleccionada (Datos GeoJSON)
  const [zonaSeleccionada, setZonaSeleccionada] = useState(null); // Nombre de la zona (Estado del botón)
  // NUEVO ESTADO: Para controlar si los caminos peatonales deben mostrarse
  const [caminosVisibles, setCaminosVisibles] = useState(true); 

  // Cargar caminos peatonales (Fijo)
  useEffect(() => {
    fetch("/data/caminos-parquedelaCiudad.geojson")
      .then((response) => response.json())
      .then((data) => setGeoData(data))
      .catch((err) => console.error("Error cargando GeoJSON de caminos:", err));
  }, []);

  // Zonas disponibles
  const zonasDisponibles = {
    "Comuna 8": "/data2/comuna8.geojson",
    Caballito: "/data2/caballito.geojson",
    "Puerto Madero": "/data2/PuertoMadero.geojson",

  };

  // Lógica principal: Cargar / Borrar / Cambiar
  const manejarSeleccionZona = (nombreZona) => {
    if (zonaSeleccionada === nombreZona) {
      // Si el botón ya está activo, lo desactiva, borra la capa y ESCONDE los caminos.
      setZonaSeleccionada(null); 
      setZonaData(null); 
      setCaminosVisibles(true); // Opcional: Puedes decidir si los caminos se mantienen visibles o se esconden por defecto
    } else {
      // Si es un botón nuevo, borra la anterior, marca el nuevo y carga la nueva zona.
      setZonaData(null); 
      setZonaSeleccionada(nombreZona); 
      setCaminosVisibles(true); // Se activa la visibilidad de los caminos por defecto al seleccionar una zona

      fetch(zonasDisponibles[nombreZona])
        .then((response) => {
             if (!response.ok) {
                 throw new Error('Error al cargar la zona: ' + response.statusText);
             }
             return response.json();
        })
        .then((data) => setZonaData(data)) 
        .catch((err) => {
            console.error("Error cargando GeoJSON de zona:", err);
            if (zonaSeleccionada === nombreZona) {
                 setZonaSeleccionada(null);
            }
        });
    }
  };
  
  // Función para alternar la visibilidad de los caminos
  const manejarVisibilidadCaminos = () => {
      setCaminosVisibles(prev => !prev);
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
          <div key={nombre}>
            <button
              className={`zona-btn ${
                zonaSeleccionada === nombre ? "active" : ""
              }`}
              onClick={() => manejarSeleccionZona(nombre)}
            >
              {nombre}
            </button>
            {/* NUEVO BOTÓN: Se muestra SÓLO si esta zona está seleccionada */}
            {zonaSeleccionada === nombre && (
              <button
                className="caminos-btn"
                onClick={manejarVisibilidadCaminos}
              >
                {/* Texto dinámico: "Ocultar" si están visibles, "Mostrar" si están ocultos */}
                {caminosVisibles ? "Ocultar Caminos" : "Mostrar Caminos"}
              </button>
            )}
          </div>
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

        <MapZoomer zonaData={zonaData} />

        {/* Caminos peatonales: AHORA SE MUESTRAN SÓLO si caminosVisibles es true */}
        {geoData && caminosVisibles && <GeoJSON data={geoData} style={estiloCaminos} />}

        {/* Zona seleccionada */}
        {zonaData && <GeoJSON data={zonaData} style={estiloZona} />}
      </MapContainer>
    </div>
  );
}