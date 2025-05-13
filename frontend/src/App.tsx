"use client"
import { useEffect, useState, useCallback } from "react"
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap, LayerGroup, Tooltip } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import "./App.css"
import { io } from "socket.io-client"
import L from "leaflet"
import { TrafficLight } from "./components/TrafficLight"
import { VehicleRouting } from "./components/VehicleRouting"
import { TrafficDashboard } from "./components/TrafficDashboard"
import { Sidebar } from "./components/Sidebar"
import { ControlPanel } from "./components/ControlPanel"
import { Analytics } from "./components/Analytics"
import { Toast } from "./components/Toast"

// Fix Leaflet icon issue
L.Icon.Default.imagePath = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/"

L.Icon.Default.mergeOptions({
  iconRetinaUrl: `${L.Icon.Default.imagePath}/marker-icon-2x.png`,
  iconUrl: `${L.Icon.Default.imagePath}/marker-icon.png`,
  shadowUrl: `${L.Icon.Default.imagePath}/marker-shadow.png`,
})

// Custom icons for traffic lights
const greenLightIcon = new L.Icon({
  iconUrl: "/green-light.svg",
  iconSize: [25, 25],
})

const redLightIcon = new L.Icon({
  iconUrl: "/red-light.svg",
  iconSize: [25, 25],
})

const yellowLightIcon = new L.Icon({
  iconUrl: "/yellow-light.svg",
  iconSize: [25, 25],
})

// Custom vehicle icon
const vehicleIcon = new L.Icon({
  iconUrl: "/vehicle.svg",
  iconSize: [20, 20],
})

// Custom vehicle icons based on type
const carIcon = new L.Icon({
  iconUrl: "/car.svg",
  iconSize: [24, 24],
})

const busIcon = new L.Icon({
  iconUrl: "/bus.svg",
  iconSize: [28, 28],
})

const truckIcon = new L.Icon({
  iconUrl: "/truck.svg",
  iconSize: [30, 30],
})

// MapUpdater component to handle map updates
function MapUpdater({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap()

  useEffect(() => {
    map.setView(center, zoom)
  }, [center, zoom, map])

  return null
}

function App() {
  const [cityGraph, setCityGraph] = useState<any>(null)
  const [trafficLights, setTrafficLights] = useState<any[]>([])
  const [vehicles, setVehicles] = useState<any[]>([])
  const [incidents, setIncidents] = useState<any[]>([])
  const [congestionLevels, setCongestionLevels] = useState<any>({})
  const [selectedVehicle, setSelectedVehicle] = useState<string | null>(null)
  const [mapCenter, setMapCenter] = useState<[number, number]>([37.7749, -122.4194]) // Default: San Francisco
  const [mapZoom, setMapZoom] = useState(13)
  const [isConnected, setIsConnected] = useState(false)
  const [simulationRunning, setSimulationRunning] = useState(false)
  const [cityName, setCityName] = useState("San Francisco")
  const [availableCities, setAvailableCities] = useState<string[]>([
    "San Francisco",
    "New York",
    "Chicago",
    "Boston",
    "Seattle",
  ])
  const [activeTab, setActiveTab] = useState("map")
  const [toast, setToast] = useState<{ message: string; type: string; visible: boolean }>({
    message: "",
    type: "",
    visible: false,
  })
  const [simulationSpeed, setSimulationSpeed] = useState(1)
  const [trafficLightMode, setTrafficLightMode] = useState("auto")
  const [routingAlgorithm, setRoutingAlgorithm] = useState("a_star")
  const [showCongestion, setShowCongestion] = useState(true)
  const [showVehicles, setShowVehicles] = useState(true)
  const [showTrafficLights, setShowTrafficLights] = useState(true)
  const [showIncidents, setShowIncidents] = useState(true)
  const [analyticsData, setAnalyticsData] = useState<any>({
    averageSpeed: 0,
    averageWaitTime: 0,
    congestionTrend: [],
    trafficLightEfficiency: 0,
    vehicleCountHistory: [],
    incidentHistory: [],
  })
  const [manualLightControl, setManualLightControl] = useState<any>({
    nodeId: null,
    state: "red",
  })

  // Show toast message
  const showToast = useCallback((message: string, type = "info") => {
    setToast({ message, type, visible: true })
    setTimeout(() => {
      setToast((prev) => ({ ...prev, visible: false }))
    }, 3000)
  }, [])

  useEffect(() => {
    // Connect to WebSocket server
    const socket = io("http://localhost:8000", {
      transports: ["websocket"],
      path: "/socket.io", // Match the path with server
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      autoConnect: true,
      withCredentials: false, // Set to false since we're using "*" for CORS
    })

    socket.on("connect", () => {
      console.log("Connected to WebSocket server")
      setIsConnected(true)
      showToast("Connected to server", "success")
    })

    socket.on("connect_error", (error) => {
      console.error("WebSocket connection error:", error)
      setIsConnected(false)
      showToast("Connection error: " + error.message, "error")
    })

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket server")
      setIsConnected(false)
      showToast("Disconnected from server", "error")
    })

    socket.on("message", (data) => {
      console.log("Received message:", data)
    })

    socket.on("city_graph", (data) => {
      console.log("Received city graph:", data)
      setCityGraph(data)
      if (data.nodes && data.nodes.length > 0) {
        setMapCenter([data.nodes[0].lat, data.nodes[0].lon])
      }
    })

    socket.on("traffic_lights", (data) => {
      console.log("Received traffic lights:", data)
      setTrafficLights(data)
    })

    socket.on("vehicles", (data) => {
      console.log("Received vehicles:", data)
      setVehicles(data)
    })

    socket.on("incidents", (data) => {
      console.log("Received incidents:", data)
      setIncidents(data)
    })

    socket.on("congestion", (data) => {
      console.log("Received congestion levels:", data)
      setCongestionLevels(data)
    })

    socket.on("analytics", (data) => {
      console.log("Received analytics data:", data)
      setAnalyticsData(data)
    })

    socket.on("simulation_status", (data) => {
      console.log("Simulation status:", data)
      setSimulationRunning(data.running)
      if (data.message) {
        showToast(data.message, data.status || "info")
      }
    })

    // Clean up on component unmount
    return () => {
      socket.close() // Use close() instead of disconnect()
    }
  }, [showToast])

  const startSimulation = () => {
    fetch("http://localhost:8000/simulation/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        city: cityName,
        speed: simulationSpeed,
        routing_algorithm: routingAlgorithm,
        traffic_light_mode: trafficLightMode,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Simulation started:", data)
        if (data.status === "success") {
          setSimulationRunning(true)
          showToast(data.message, "success")
        } else {
          showToast(data.message, "error")
        }
      })
      .catch((error) => {
        console.error("Error starting simulation:", error)
        showToast("Error starting simulation", "error")
      })
  }

  const stopSimulation = () => {
    fetch("http://localhost:8000/simulation/stop", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Simulation stopped:", data)
        if (data.status === "success") {
          setSimulationRunning(false)
          showToast(data.message, "success")
        } else {
          showToast(data.message, "error")
        }
      })
      .catch((error) => {
        console.error("Error stopping simulation:", error)
        showToast("Error stopping simulation", "error")
      })
  }

  const addIncident = (lat: number, lon: number, type: string) => {
    fetch("http://localhost:8000/incidents/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ lat, lon, type }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Incident added:", data)
        if (data.status === "success") {
          showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} incident reported`, "success")
        } else {
          showToast(data.message, "error")
        }
      })
      .catch((error) => {
        console.error("Error adding incident:", error)
        showToast("Error reporting incident", "error")
      })
  }

  const changeCity = (city: string) => {
    setCityName(city)
    if (simulationRunning) {
      stopSimulation()
    }
    showToast(`City changed to ${city}`, "info")
  }

  const updateSimulationSettings = (settings: any) => {
    fetch("http://localhost:8000/simulation/settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settings),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Settings updated:", data)
        if (data.status === "success") {
          showToast("Simulation settings updated", "success")
          if (settings.speed !== undefined) setSimulationSpeed(settings.speed)
          if (settings.routing_algorithm !== undefined) setRoutingAlgorithm(settings.routing_algorithm)
          if (settings.traffic_light_mode !== undefined) setTrafficLightMode(settings.traffic_light_mode)
        } else {
          showToast(data.message, "error")
        }
      })
      .catch((error) => {
        console.error("Error updating settings:", error)
        showToast("Error updating settings", "error")
      })
  }

  const controlTrafficLight = (nodeId: string, state: string) => {
    fetch("http://localhost:8000/traffic_lights/control", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ node_id: nodeId, state }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Traffic light controlled:", data)
        if (data.status === "success") {
          showToast(`Traffic light ${nodeId} set to ${state}`, "success")
          setManualLightControl({ nodeId, state })
        } else {
          showToast(data.message, "error")
        }
      })
      .catch((error) => {
        console.error("Error controlling traffic light:", error)
        showToast("Error controlling traffic light", "error")
      })
  }

  const addVehicle = (origin: string, destination: string, type = "car") => {
    fetch("http://localhost:8000/vehicles/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ origin, destination, type }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Vehicle added:", data)
        if (data.status === "success") {
          showToast(`New ${type} added to simulation`, "success")
        } else {
          showToast(data.message, "error")
        }
      })
      .catch((error) => {
        console.error("Error adding vehicle:", error)
        showToast("Error adding vehicle", "error")
      })
  }

  const getVehicleIcon = (vehicle: any) => {
    switch (vehicle.type) {
      case "bus":
        return busIcon
      case "truck":
        return truckIcon
      default:
        return carIcon
    }
  }

  const getTrafficLightIcon = (light: any) => {
    switch (light.state) {
      case "green":
        return greenLightIcon
      case "yellow":
        return yellowLightIcon
      default:
        return redLightIcon
    }
  }

  const getCongestionColor = (level: number) => {
    if (level < 0.3) return "#4ade80" // green
    if (level < 0.6) return "#fb923c" // orange
    return "#ef4444" // red
  }

  return (
    <div className="app-container">
      <Sidebar
        isConnected={isConnected}
        simulationRunning={simulationRunning}
        startSimulation={startSimulation}
        stopSimulation={stopSimulation}
        cityName={cityName}
        availableCities={availableCities}
        changeCity={changeCity}
        vehicles={vehicles}
        selectedVehicle={selectedVehicle}
        setSelectedVehicle={setSelectedVehicle}
        addIncident={addIncident}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        simulationSpeed={simulationSpeed}
        trafficLightMode={trafficLightMode}
        routingAlgorithm={routingAlgorithm}
        updateSimulationSettings={updateSimulationSettings}
        addVehicle={addVehicle}
        showCongestion={showCongestion}
        setShowCongestion={setShowCongestion}
        showVehicles={showVehicles}
        setShowVehicles={setShowVehicles}
        showTrafficLights={showTrafficLights}
        setShowTrafficLights={setShowTrafficLights}
        showIncidents={showIncidents}
        setShowIncidents={setShowIncidents}
      />

      <div className="main-content">
        {activeTab === "map" && (
          <>
            <TrafficDashboard
              trafficLights={trafficLights}
              vehicles={vehicles}
              incidents={incidents}
              congestionLevels={congestionLevels}
              analyticsData={analyticsData}
            />

            <div className="map-container">
              <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: "100%", width: "100%" }}>
                <MapUpdater center={mapCenter} zoom={mapZoom} />
                <TileLayer
                  attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Render city graph */}
                {cityGraph && cityGraph.edges && showCongestion && (
                  <LayerGroup>
                    {cityGraph.edges.map((edge: any, index: number) => {
                      const congestion = congestionLevels[edge.id] || 0
                      const color = getCongestionColor(congestion)
                      const weight = 3 + congestion * 5 // Thicker lines for more congestion

                      return (
                        <Polyline
                          key={`edge-${index}`}
                          positions={[
                            [edge.source_lat, edge.source_lon],
                            [edge.target_lat, edge.target_lon],
                          ]}
                          color={color}
                          weight={weight}
                          opacity={0.8}
                        >
                          <Tooltip sticky>
                            <div>
                              <strong>{edge.name || `Road ${edge.id}`}</strong>
                              <div>Congestion: {(congestion * 100).toFixed(0)}%</div>
                              <div>Vehicles: {edge.vehicle_count || 0}</div>
                              <div>Travel time: {Math.round(edge.travel_time)} sec</div>
                            </div>
                          </Tooltip>
                        </Polyline>
                      )
                    })}
                  </LayerGroup>
                )}

                {/* Render traffic lights */}
                {showTrafficLights && (
                  <LayerGroup>
                    {trafficLights.map((light, index) => (
                      <Marker
                        key={`light-${index}`}
                        position={[light.lat, light.lon]}
                        icon={getTrafficLightIcon(light)}
                      >
                        <Popup>
                          <TrafficLight
                            id={light.id}
                            state={light.state}
                            nextChange={light.next_change}
                            queueLength={light.queue_length}
                            controlTrafficLight={controlTrafficLight}
                            trafficLightMode={trafficLightMode}
                          />
                        </Popup>
                      </Marker>
                    ))}
                  </LayerGroup>
                )}

                {/* Render vehicles */}
                {showVehicles && (
                  <LayerGroup>
                    {vehicles.map((vehicle, index) => (
                      <Marker
                        key={`vehicle-${index}`}
                        position={[vehicle.lat, vehicle.lon]}
                        icon={getVehicleIcon(vehicle)}
                        zIndexOffset={selectedVehicle === vehicle.id ? 1000 : 0}
                      >
                        <Popup>
                          <VehicleRouting
                            id={vehicle.id}
                            type={vehicle.type || "car"}
                            origin={vehicle.origin}
                            destination={vehicle.destination}
                            currentRoute={vehicle.current_route}
                            eta={vehicle.eta}
                            speed={vehicle.speed}
                            status={vehicle.status}
                          />
                        </Popup>
                      </Marker>
                    ))}
                  </LayerGroup>
                )}

                {/* Render selected vehicle route */}
                {selectedVehicle && vehicles.find((v) => v.id === selectedVehicle)?.current_route && (
                  <Polyline
                    positions={vehicles
                      .find((v) => v.id === selectedVehicle)
                      ?.current_route.map((point: any) => [point.lat, point.lon])}
                    color="#3b82f6"
                    weight={5}
                    dashArray="10, 10"
                  />
                )}

                {/* Render incidents */}
                {showIncidents && (
                  <LayerGroup>
                    {incidents.map((incident, index) => (
                      <Circle
                        key={`incident-${index}`}
                        center={[incident.lat, incident.lon]}
                        radius={100}
                        color={
                          incident.type === "accident"
                            ? "#ef4444"
                            : incident.type === "construction"
                              ? "#f59e0b"
                              : "#fb923c"
                        }
                        fillColor={
                          incident.type === "accident"
                            ? "#ef4444"
                            : incident.type === "construction"
                              ? "#f59e0b"
                              : "#fb923c"
                        }
                        fillOpacity={0.5}
                      >
                        <Popup>
                          <div className="incident-popup">
                            <h3>{incident.type.charAt(0).toUpperCase() + incident.type.slice(1)}</h3>
                            <p>Reported at: {new Date(incident.timestamp * 1000).toLocaleTimeString()}</p>
                            <p>
                              Expected clearance: {new Date(incident.expected_clearance * 1000).toLocaleTimeString()}
                            </p>
                            <div className="incident-severity">
                              Severity:{" "}
                              <span className={`severity-${incident.severity || "medium"}`}>
                                {incident.severity || "Medium"}
                              </span>
                            </div>
                          </div>
                        </Popup>
                      </Circle>
                    ))}
                  </LayerGroup>
                )}
              </MapContainer>
            </div>
          </>
        )}

        {activeTab === "control" && (
          <ControlPanel
            trafficLights={trafficLights}
            vehicles={vehicles}
            controlTrafficLight={controlTrafficLight}
            addVehicle={addVehicle}
            cityGraph={cityGraph}
            trafficLightMode={trafficLightMode}
            manualLightControl={manualLightControl}
          />
        )}

        {activeTab === "analytics" && (
          <Analytics
            analyticsData={analyticsData}
            vehicles={vehicles}
            trafficLights={trafficLights}
            incidents={incidents}
            congestionLevels={congestionLevels}
          />
        )}
      </div>

      <Toast message={toast.message} type={toast.type} visible={toast.visible} />
    </div>
  )
}

export default App