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
};

// ----------------------------------------------------
// Componente para ajustar la vista del mapa (Zoom)
// ----------------------------------------------------
function MapZoomer({ zonaData, caminosData, zonaSeleccionada }) {
  const map = useMap();

  useEffect(() => {
    // 🚨 1. SOLUCIÓN ESPECÍFICA PARA CAMINOS DE RESERVA ECOLÓGICA (Puerto Madero)
    if (zonaSeleccionada === "Puerto Madero" && caminosData) {
      console.log(
        "Detectados caminos de 'Reserva Ecologica'. Aplicando zoom fijo."
      );
      // Coordenadas aproximadas del centro de la Reserva Ecológica (Zoom 15 para más detalle)
      map.flyTo([-34.607044, -58.35225], 14.7);
      return;
    }

    // 3. Comportamiento normal (para Caballito, o si los GeoJSON de zona/caminos son correctos)
    const dataToUse = caminosData || zonaData;

    if (dataToUse) {
      const geoJsonLayer = L.geoJson(dataToUse);
      const bounds = geoJsonLayer.getBounds();

      if (bounds.isValid()) {
        // Para las zonas buenas, ajusta el zoom al límite del GeoJSON
        map.fitBounds(bounds, { padding: [40, 40] });
      }
    }
  }, [zonaData, caminosData, zonaSeleccionada, map]);

  return null;
}
// ----------------------------------------------------

export default function Dashboard() {
  // ESTADOS MOVIDOS DENTRO DE LA FUNCIÓN
  const [paradas, setParadas] = useState([]);
  const [zonasDisponibles, setZonasDisponibles] = useState({});
  const [zonasNivelesDB, setZonasNivelesDB] = useState(null);
  const [zonaSeleccionada, setZonaSeleccionada] = useState(null);
  const [zonaData, setZonaData] = useState(null);
  const [caminosData, setCaminosData] = useState(null);
  const [caminosVisibles, setCaminosVisibles] = useState({});
  const [estiloZonaSeleccionada, setEstiloZonaSeleccionada] = useState(null);

  // -----------------------------
  // 1️⃣ Cargar paradas (MOVIDO Y CORREGIDO)
  // -----------------------------
  useEffect(() => {
    fetch(`${FLASK_API_BASE_URL}/paradas`)
      .then((res) => res.json())
      .then((data) => setParadas(data))
      .catch((err) => console.error("Error cargando paradas:", err));
  }, []);

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

      // RESTAURAR LA ZONA: Vuelve a cargar la geometría de la zona para que MapZoomer la enfoque.
      // Puedes reutilizar la lógica de carga de zona o, más simple, cargar la data que ya tienes.
      // Para este ejemplo, llamaremos a la función de selección de zona para restaurar la vista.
      manejarSeleccionZona(nombreZona); // Llama al manejador de zona para recargar/enfocar la zona
    } else {
      // Caso 2: MOSTRAR CAMINOS (y ocultar la zona)

      // 🚨 Paso 1: OCULTAR ZONA MARCADA
      setZonaData(null); // Esto hace que el GeoJSON de la zona deje de renderizarse
      setEstiloZonaSeleccionada(null); // Opcional, pero buena práctica

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

            // MapZoomer reaccionará a 'caminosData' para hacer zoom.
            // Para esto, necesitamos que MapZoomer pueda escuchar tanto 'zonaData' como 'caminosData'.

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

  // Estilo de caminos
  const estiloCaminos = {
    color: "orange",
    weight: 3,
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
        {/* Paradas */}
        {paradas.map((parada) => (
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
        ))}{" "}
        {/* Cierre corregido: )) } */}
      </MapContainer>
    </div>
  );
}
