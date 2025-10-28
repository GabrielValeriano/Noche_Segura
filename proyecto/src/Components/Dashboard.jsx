import { useState, useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "./Dashboard.css";

// URL base de tu backend Flask
const FLASK_API_BASE_URL = "http://localhost:5000";

// Icono para las paradas
const iconoParada = L.icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/201/201818.png",
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -25],
});

export default function Dashboard() {
  const [paradas, setParadas] = useState([]);
  const [zonasDisponibles, setZonasDisponibles] = useState({});
  const [zonasNivelesDB, setZonasNivelesDB] = useState(null);
  const [zonaSeleccionada, setZonaSeleccionada] = useState(null);
  const [zonaData, setZonaData] = useState(null);
  const [caminosData, setCaminosData] = useState(null);
  const [caminosVisibles, setCaminosVisibles] = useState({});
}

  // -----------------------------
  // 1️⃣ Cargar paradas
  // -----------------------------
  useEffect(() => {
    fetch(`${FLASK_API_BASE_URL}/paradas`)
      .then(res => res.json())
      .then(data => setParadas(data))
      .catch(err => console.error("Error cargando paradas:", err));
  }, []);

// ----------------------------------------------------
// Mapeo de Niveles de Seguridad a Estilos (Colores)
// ----------------------------------------------------
const estilosPorNivel = {
  // Nivel 1: BAJO (Rojo/Alto riesgo)
  1: {
    color: "#dc3545", // Borde Rojo
    fillColor: "#dc3545", // Relleno Rojo
    fillOpacity: 0.5,
    weight: 2,
  },
  // Nivel 2: MEDIO (Amarillo/Medio riesgo)
  2: {
    color: "#ffc107", // Borde Amarillo
    fillColor: "#ffc107", // Relleno Amarillo
    fillOpacity: 0.4,
    weight: 2,
  },
  // Nivel 3: ALTO (Verde/Bajo riesgo)
  3: {
    color: "#28a745", // Borde Verde
    fillColor: "#28a745", // Relleno Verde
    fillOpacity: 0.4,
    weight: 2,
  },
};

// Definición inicial estática de zonas (Solo mantenemos URLs de Caminos)
const ZONAS_ESTATICAS = {
  "Comuna 8": {
    // zonaUrl ELIMINADO
    caminosUrl: "/data/caminos-parquedelaCiudad.geojson",
    caminosNombre: "Parque de la Ciudad",
  },
  Caballito: {
    // zonaUrl ELIMINADO
    caminosUrl: "/data/caminos-Caballito.geojson",
    caminosNombre: "Parque Centenario",
  },
  "Puerto Madero": {
    // zonaUrl ELIMINADO
    caminosUrl: "/data/caminos-PuertoMadero.geojson",
    caminosNombre: "Puente de la Mujer",
  },
};

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
  const [caminosData, setCaminosData] = useState(null);
  const [zonaData, setZonaData] = useState(null);
  const [zonaSeleccionada, setZonaSeleccionada] = useState(null);
  const [caminosVisibles, setCaminosVisibles] = useState({});

  // ESTADO para las zonas, que ahora incluirán los estilos y niveles dinámicos
  const [zonasDisponibles, setZonasDisponibles] = useState({});
  // ESTADO para guardar los niveles de seguridad recibidos de Flask
  const [zonasNivelesDB, setZonasNivelesDB] = useState(null);

  // Estado para guardar el estilo FINAL de la zona seleccionada
  const [estiloZonaSeleccionada, setEstiloZonaSeleccionada] = useState(null);

  // -----------------------------------------------------------------
  // EFECTO 1: Carga inicial de niveles de seguridad desde el backend
  // -----------------------------------------------------------------
  useEffect(() => {
    async function fetchNiveles() {
      try {
        const response = await fetch(
          `${FLASK_API_BASE_URL}/niveles_seguridad_zonas`
        );
        if (!response.ok) {
          throw new Error("Error al obtener niveles de seguridad del backend");
        }
        const data = await response.json();
        setZonasNivelesDB(data);
      } catch (error) {
        console.error("Fallo la carga de niveles desde Flask:", error);
        setZonasNivelesDB({});
      }
    }
    fetchNiveles();
  }, []);

  // -----------------------------------------------------------------
  // EFECTO 2: Combina datos estáticos con estilos dinámicos de la BD
  // -----------------------------------------------------------------
  useEffect(() => {
    if (zonasNivelesDB) {
      const zonasConEstilo = {};

      Object.keys(ZONAS_ESTATICAS).forEach((nombre) => {
        const nivelId = zonasNivelesDB[nombre];
        const estilo = nivelId ? estilosPorNivel[nivelId] : null;

        zonasConEstilo[nombre] = {
          ...ZONAS_ESTATICAS[nombre],
          nivel_id: nivelId,
          estilos: estilo || estilosPorNivel[1],
        };
      });

      setZonasDisponibles(zonasConEstilo);
    }
  }, [zonasNivelesDB]);

  // Lógica principal: Cargar / Borrar / Cambiar ZONA
  const manejarSeleccionZona = (nombreZona) => {
    if (zonaSeleccionada === nombreZona) {
      // Desactiva la zona y oculta los caminos
      setZonaSeleccionada(null);
      setZonaData(null);
      setCaminosData(null);
      setEstiloZonaSeleccionada(null);

      setCaminosVisibles((prev) => ({ ...prev, [nombreZona]: false }));
    } else {
      // 1. Pre-limpieza y establecimiento de zona
      setZonaData(null);
      setCaminosData(null);
      setZonaSeleccionada(nombreZona);

      setCaminosVisibles((prev) => ({ ...prev, [nombreZona]: false }));

      // 2. OBTENEMOS EL OBJETO DE ESTILOS YA CREADO POR EL EFECTO
      const zonaInfo = zonasDisponibles[nombreZona];
      setEstiloZonaSeleccionada(zonaInfo.estilos);

      // 3. 💥 Carga los datos de la zona COMPLETA (incluyendo GeoJSON) desde Flask
      fetch(`${FLASK_API_BASE_URL}/zona/${nombreZona}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              "Error al cargar la zona desde Flask: " + response.statusText
            );
          }
          return response.json();
        })
        .then((data) => {
          // data.poligrafo_geojson contiene el GeoJSON que necesita Leaflet
          if (data && data.poligrafo_geojson) {
            setZonaData(data.poligrafo_geojson); // Establece la geometría GeoJSON
          } else {
            console.error(
              "Error: El backend no devolvió la geometría (poligrafo_geojson)."
            );
            setZonaData(null);
            setEstiloZonaSeleccionada(null);
          }
        })
        .catch((err) => {
          console.error("Error cargando GeoJSON de zona desde Flask:", err);
          setEstiloZonaSeleccionada(null);
          if (zonaSeleccionada === nombreZona) {
            setZonaSeleccionada(null);
          }
        });
    }
  };

  // Función para alternar la visibilidad de los caminos de la zona activa
  const manejarVisibilidadCaminos = (nombreZona) => {
    const isVisible = caminosVisibles[nombreZona];
    const caminosUrl = zonasDisponibles[nombreZona].caminosUrl;

    if (isVisible) {
      setCaminosVisibles((prev) => ({ ...prev, [nombreZona]: false }));
      setCaminosData(null);
    } else {
      // NOTA: Los caminos (caminosUrl) siguen apuntando a archivos estáticos locales.
      fetch(caminosUrl)
        .then((response) => response.json())
        .then((data) => {
          setCaminosData(data);
          setCaminosVisibles((prev) => ({ ...prev, [nombreZona]: true }));
        })
        .catch((err) =>
          console.error("Error cargando GeoJSON de caminos:", err)
        );
    }
  };

  // Estilo de caminos 
  const estiloCaminos = {
    color: "orange",
    weight: 3,
    dashArray: "4.5, 4.5", // punteado
  };

  const zonasArray = Object.keys(zonasDisponibles);

  return (
    <div className="dashboard">
      {/* Panel lateral de selección */}
      <div className="sidebar">
        <h3>Zonas disponibles</h3>

        {zonasNivelesDB === null && <p>Cargando niveles de seguridad...</p>}

        {zonasArray.length > 0 &&
          zonasNivelesDB !== null &&
          zonasArray.map((nombre) => (
            <div key={nombre}>
              <button
                className={`zona-btn ${
                  zonaSeleccionada === nombre ? "active" : ""
                }`}
                onClick={() => manejarSeleccionZona(nombre)}
              >
                {/* Texto Zona */}
                {nombre}
                {zonasDisponibles[nombre].nivel_id && ``}
              </button>

              {/* Botón de Caminos */}
              {zonaSeleccionada === nombre && (
                <button
                  className="caminos-btn"
                  onClick={() => manejarVisibilidadCaminos(nombre)}
                >
                  {/* Texto Caminos */}
                  {zonasDisponibles[nombre].caminosNombre}
                </button>
              )}
            </div>
          ))}
      </div>

      {/* Mapa principal */}
      <MapContainer
        center={[-34.68, -58.46]}
        zoom={14}
        className="map"
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        />

        <MapZoomer zonaData={zonaData} />

        {/* Caminos peatonales */}
        {caminosData && <GeoJSON data={caminosData} style={estiloCaminos} />}

        {/* Zona seleccionada: USA EL ESTILO DINÁMICO */}
        {zonaData && estiloZonaSeleccionada && (
          <GeoJSON data={zonaData} style={estiloZonaSeleccionada} />
        )
        {/* Paradas */}
        {paradas.map(parada => (
          <Marker
            key={parada.parada_id}
            position={[parada.latitud, parada.longitud]}
            icon={iconoParada}
          >
            <Popup>
              <strong>{parada.nombre_calle}</strong>
              <br />
              Líneas: {parada.lineas?.length ? parada.lineas.join(", ") : "No registradas"}
            </Popup>
          </Marker>
        }
      </MapContainer>
    </div>
  );
}
