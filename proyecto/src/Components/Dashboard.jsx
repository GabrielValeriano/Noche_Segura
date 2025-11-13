import { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  useMap,
  Marker,
  Popup,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "./Dashboard.css";
import * as turf from "@turf/turf"; 

// URL base de tu backend Flask (Ajusta el puerto si usas PHP)
const FLASK_API_BASE_URL = "http://localhost:5000";

// Icono para las paradas
const iconoParada = L.icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/201/201818.png",
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -25],
});

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
  "Villa Soldati": {
    caminosNombre: "Parque de la Ciudad",
  },
  Caballito: {
    caminosNombre: "Parque Centenario",
  },
  "Puerto Madero": {
    caminosNombre: "Reserva Ecologica",
  },
  Palermo: {
    caminosNombre: "Paseo El Rosedal",
  },
  "Parque Patricios": {
    caminosNombre: "Parque Florentino",
  },
};

// ----------------------------------------------------
// Componente para ajustar la vista del mapa (Zoom)
// ----------------------------------------------------
function MapZoomer({ zonaData, caminosData, zonaSeleccionada }) {
  const map = useMap();

  useEffect(() => {
    // Si no hay datos de zona ni de caminos, no hacemos zoom.
    if (!zonaData && !caminosData) {
        return;
    }

    // El código específico de Puerto Madero solo se ejecuta si hay caminosData, 
    // así que no afecta la zona.

    // 🚨 Esta es la parte crucial que maneja ZONAS y CAMINOS
    const dataToUse = caminosData || zonaData; 

    if (dataToUse) {
      // 1. Creamos una capa GeoJSON temporal SÓLO con los datos de zona/caminos.
      const geoJsonLayer = L.geoJson(dataToUse); 
      
      // 2. Obtenemos los límites SÓLO de esa capa temporal.
      const bounds = geoJsonLayer.getBounds(); 

      if (bounds.isValid()) {
        // 3. Forzamos el mapa a ajustarse SÓLO a estos límites.
        map.fitBounds(bounds, { padding: [10, 10] });
      } else {
        console.error("Límites de GeoJSON no válidos.");
      }
    }
  }, [zonaData, caminosData, zonaSeleccionada, map]); // Dependencias

  return null;
}
// ----------------------------------------------------

export default function Dashboard() {
  // ESTADOS EXISTENTES
  const [paradas, setParadas] = useState([]);
  const [zonasDisponibles, setZonasDisponibles] = useState({});
  const [zonasNivelesDB, setZonasNivelesDB] = useState(null);
  const [zonaSeleccionada, setZonaSeleccionada] = useState(null);
  const [zonaData, setZonaData] = useState(null);
  const [caminosData, setCaminosData] = useState(null);
  const [caminosVisibles, setCaminosVisibles] = useState({});
  const [estiloZonaSeleccionada, setEstiloZonaSeleccionada] = useState(null);

  // 🚌 NUEVOS ESTADOS PARA LÍNEAS DE COLECTIVO
  const [lineasDisponibles, setLineasDisponibles] = useState([]); // Lista de líneas (ej: ['55', '103', '7'])
  const [lineasVisibles, setLineasVisibles] = useState({}); // Estado de visibilidad (ej: { '55': true, '103': false })
  const [lineasGeoJSON, setLineasGeoJSON] = useState({}); // GeoJSON de las rutas (ej: { '55': {type: 'FeatureCollection', ...} })
  const [paradasFiltradas, setParadasFiltradas] = useState([]);
  // -----------------------------
  // 1️⃣ Cargar paradas
  // -----------------------------
  useEffect(() => {
    fetch(`${FLASK_API_BASE_URL}/paradas`)
      .then((res) => res.json())
      .then((data) => setParadas(data))
      .catch((err) => console.error("Error cargando paradas:", err));
  }, []);

  // -----------------------------
  // 🚌 NUEVO EFECTO: Cargar lista de líneas
  // -----------------------------
  useEffect(() => {
    async function fetchLineas() {
      try {
        const response = await fetch(`${FLASK_API_BASE_URL}/lineas`);
        if (!response.ok) {
          throw new Error("Error al obtener la lista de líneas del backend");
        }
        const data = await response.json();
        // Asume que tu Flask devuelve {'lineas': ['55', '103', '7', ...]}
        setLineasDisponibles(data.lineas || []);
      } catch (error) {
        console.error(
          "Fallo la carga de la lista de líneas desde Flask:",
          error
        );
        setLineasDisponibles([]);
      }
    }
    fetchLineas();
  }, []);

  useEffect(() => {
    if (zonaData && paradas.length > 0) {
      try {
        // Asegúrate de que el GeoJSON de la zona sea un Polígono (o MultiPolígono)
        const zonaPolygon = zonaData; 
        
        const filtered = paradas.filter(parada => {
          // Crea un punto turf a partir de las coordenadas de la parada
          // Nota: Leaflet/GeoJSON usa [lng, lat], pero turf.point a menudo requiere [lng, lat] también.
          // Revisar el orden de tus datos: si son [lat, lng], podrías necesitar [parada.longitud, parada.latitud]
          const punto = turf.point([parada.longitud, parada.latitud]); 

          // Comprueba si el punto está dentro del polígono de la zona
          const estaDentro = turf.booleanPointInPolygon(punto, zonaPolygon);
          
          return estaDentro;
        });

        setParadasFiltradas(filtered);

      } catch (error) {
        console.error("Error al filtrar paradas con Turf:", error);
        setParadasFiltradas([]); // Si hay un error, limpia el filtro
      }
    } else {
      // Limpia las paradas filtradas cuando no hay zona seleccionada
      setParadasFiltradas([]);
    }
  }, [zonaData, paradas]); // Dependencias: se ejecuta con cada nueva zona o carga inicial de paradas


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
    const nombreRuta = zonasDisponibles[nombreZona].caminosNombre;

    if (isVisible) {
      // Caso 1: OCULTAR CAMINOS (y volver a mostrar la zona)
      setCaminosVisibles((prev) => ({ ...prev, [nombreZona]: false }));
      setCaminosData(null);

      // RESTAURAR LA ZONA: Llama al manejador de zona para recargar/enfocar la zona
      manejarSeleccionZona(nombreZona);
    } else {
      // Caso 2: MOSTRAR CAMINOS (y ocultar la zona)

      // 🚨 Paso 1: OCULTAR ZONA MARCADA
      setZonaData(null);
      setEstiloZonaSeleccionada(null);

      const apiUrl = `${FLASK_API_BASE_URL}/ruta/${nombreRuta}`;

      fetch(apiUrl)
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              "Error al cargar la ruta desde Flask: " + response.statusText
            );
          }
          return response.json();
        })
        .then((data) => {
          if (data && data.caminos_geojson) {
            // 🚨 Paso 2: CARGAR CAMINOS Y USAR SU GEOMETRÍA PARA EL ZOOM
            setCaminosData(data.caminos_geojson);

            setCaminosVisibles((prev) => ({ ...prev, [nombreZona]: true }));
          } else {
            console.error(
              "Error: El backend no devolvió la geometría (caminos_geojson) para la ruta."
            );
          }
        })
        .catch((err) =>
          console.error("Error cargando GeoJSON de caminos:", err)
        );
    }
  };

  // 🚌 NUEVA FUNCIÓN: Alternar visibilidad de la línea de colectivo
  const toggleLinea = async (numeroLinea) => {
    // 1. Invierte el estado de visibilidad
    const isVisible = !lineasVisibles[numeroLinea];

    // 2. Actualiza el estado de visibilidad inmediatamente
    setLineasVisibles((prev) => ({
      ...prev,
      [numeroLinea]: isVisible,
    }));

    if (isVisible) {
      // Si se va a mostrar, y no tengo el GeoJSON, lo cargo
      if (!lineasGeoJSON[numeroLinea]) {
        try {
          // 🚨 Asume que tu backend tiene una ruta para el GeoJSON de la línea (ej: /linea/55/ruta)
          const response = await fetch(
            `${FLASK_API_BASE_URL}/linea/${numeroLinea}/ruta`
          );
          if (!response.ok) {
            throw new Error(
              `Error al cargar la ruta de la línea ${numeroLinea}`
            );
          }
          const data = await response.json();

          // 3. Guarda el GeoJSON cargado
          setLineasGeoJSON((prev) => ({
            ...prev,
            [numeroLinea]: data.ruta_geojson,
          }));
        } catch (error) {
          console.error(
            `Error cargando GeoJSON de la línea ${numeroLinea}:`,
            error
          );
          // Si falla, asegúrate de que el botón se desactive para evitar confusión
          setLineasVisibles((prev) => ({ ...prev, [numeroLinea]: false }));
        }
      }
    }
    // Si se va a ocultar, solo se encarga la función de renderizado.
  };

  // Estilo de caminos
  const estiloCaminos = {
    color: "orange",
    weight: 3,
  };

  // 🚌 Estilo para las rutas de colectivo
  const estiloLineaColectivo = {
    color: "#6f42c1", // Un color distintivo, como púrpura
    weight: 4,
    opacity: 0.7,
  };

  const zonasArray = Object.keys(zonasDisponibles);

  return (
    <div className="dashboard">
      {/* Panel lateral de selección */}
      <div className="sidebar">
        {/* Sección de ZONAS */}
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

 

        {/* -------------------------------------------------- */}
      </div>
      <div className="bannerbuscardor">
          <div className="overlay-content">
              {/* 🚨 Usa la variable importada aquí */}
              <img 
                  src= "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2F170x%2F64%2F20%2F4d%2F64204d1c91aef3c9fd37dc00eab1e60e.jpg&f=1&nofb=1&ipt=8b9f3e56a167cff53389a91f2e2f3803c710fcb59d27a7bb06d8dda76de79580"
                  alt="Logo del Sistema" 
                  className="overlay-image"
              />
              <h1 className="overlay-title">Noche Segura</h1>
          </div>
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
        <MapZoomer
          zonaData={zonaData}
          caminosData={caminosData}
          zonaSeleccionada={zonaSeleccionada}
        />

        {/* Caminos peatonales */}
        {caminosData && <GeoJSON data={caminosData} style={estiloCaminos} />}

        {/* Zona seleccionada: Ahora solo se renderiza si zonaData tiene algo */}
        {zonaData && estiloZonaSeleccionada && (
          <GeoJSON data={zonaData} style={estiloZonaSeleccionada} />
        )}

        {/* 🚌 Rutas de Colectivo */}
        {Object.keys(lineasVisibles).map((linea) => {
          const isVisible = lineasVisibles[linea];
          const geoJson = lineasGeoJSON[linea];

          // Renderiza el GeoJSON si está visible Y se cargó la data
          if (isVisible && geoJson) {
            return (
              <GeoJSON
                key={`linea-${linea}`}
                data={geoJson}
                style={estiloLineaColectivo}
              />
            );
          }
          return null;
        })}

        {/* Paradas */}
        {zonaSeleccionada && (
          // Paradas
          paradas.map((parada) => (
            <Marker
              key={parada.parada_id}
              position={[parada.latitud, parada.longitud]}
              icon={iconoParada}
            >
              <Popup>
                <strong>{parada.nombre_calle}</strong>
                <br />
                Líneas:{" "}
                {parada.lineas?.length
                  ? parada.lineas.join(", ")
                  : "No registradas"}
              </Popup>
            </Marker>
          ))
          )}
      </MapContainer>
    </div>
  );
}
