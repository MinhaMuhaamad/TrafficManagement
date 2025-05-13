"use client"

import { useEffect, useState } from "react"
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import "./App.css"
import { io } from "socket.io-client"
import L from "leaflet"
import { TrafficLight } from "./components/TrafficLight"
import { VehicleRouting } from "./components/VehicleRouting"
import { TrafficDashboard } from "./components/TrafficDashboard"
import { Sidebar } from "./components/Sidebar"

// Fix Leaflet icon issue - using type assertion to avoid TypeScript error
;(L.Icon.Default.prototype as any)._getIconUrl = function () {}
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
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

const vehicleIcon = new L.Icon({
  iconUrl: "/vehicle.svg",
  iconSize: [20, 20],
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

  useEffect(() => {
    // Connect to WebSocket server
    const socket = io("http://localhost:8000", {
      transports: ["websocket", "polling"],
      path: "/ws/socket.io",
      withCredentials: false,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      autoConnect: true,
      forceNew: true,
      timeout: 120000,
      extraHeaders: {
        'ping-timeout': '120000'  // Set ping timeout as a header
      }
    })

    socket.on("connect", () => {
      console.log("Connected to WebSocket server")
      setIsConnected(true)
    })

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket server")
      setIsConnected(false)
    })

    socket.on("connect_error", (error) => {
      console.log("Connection error:", error)
    })

    socket.on("reconnect", (attemptNumber) => {
      console.log("Reconnected on attempt:", attemptNumber)
    })

    socket.on("reconnect_error", (error) => {
      console.log("Reconnection error:", error)
    })

    socket.on("city_graph", (data) => {
      console.log("Received city graph:", data)
      setCityGraph(data)

      // Set map center to the first node in the graph
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

    // Clean up on component unmount
    return () => {
      socket.disconnect()
    }
  }, [])

  const startSimulation = () => {
    fetch("http://localhost:8000/simulation/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ city: cityName }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Simulation started:", data)
        setSimulationRunning(true)
      })
      .catch((error) => console.error("Error starting simulation:", error))
  }

  const stopSimulation = () => {
    fetch("http://localhost:8000/simulation/stop", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Simulation stopped:", data)
        setSimulationRunning(false)
      })
      .catch((error) => console.error("Error stopping simulation:", error))
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
      .then((data) => console.log("Incident added:", data))
      .catch((error) => console.error("Error adding incident:", error))
  }

  const changeCity = (city: string) => {
    setCityName(city)
    // Reset simulation if running
    if (simulationRunning) {
      stopSimulation()
    }
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
      />

      <div className="main-content">
        <TrafficDashboard
          trafficLights={trafficLights}
          vehicles={vehicles}
          incidents={incidents}
          congestionLevels={congestionLevels}
        />

        <div className="map-container">
          <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: "100%", width: "100%" }}>
            <MapUpdater center={mapCenter} zoom={mapZoom} />
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Render city graph */}
            {cityGraph &&
              cityGraph.edges &&
              cityGraph.edges.map((edge: any, index: number) => {
                const congestion = congestionLevels[edge.id] || 0
                // Color based on congestion level (green to red)
                const color = congestion < 0.3 ? "green" : congestion < 0.6 ? "orange" : "red"
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
                  />
                )
              })}

            {/* Render traffic lights */}
            {trafficLights.map((light, index) => (
              <Marker
                key={`light-${index}`}
                position={[light.lat, light.lon]}
                icon={light.state === "green" ? greenLightIcon : redLightIcon}
              >
                <Popup>
                  <TrafficLight
                    id={light.id}
                    state={light.state}
                    nextChange={light.next_change}
                    queueLength={light.queue_length}
                  />
                </Popup>
              </Marker>
            ))}

            {/* Render vehicles */}
            {vehicles.map((vehicle, index) => (
              <Marker key={`vehicle-${index}`} position={[vehicle.lat, vehicle.lon]} icon={vehicleIcon}>
                <Popup>
                  <VehicleRouting
                    id={vehicle.id}
                    origin={vehicle.origin}
                    destination={vehicle.destination}
                    currentRoute={vehicle.current_route}
                    eta={vehicle.eta}
                  />
                </Popup>
              </Marker>
            ))}

            {/* Render selected vehicle route */}
            {selectedVehicle && vehicles.find((v) => v.id === selectedVehicle)?.current_route && (
              <Polyline
                positions={vehicles
                  .find((v) => v.id === selectedVehicle)
                  ?.current_route.map((point: any) => [point.lat, point.lon])}
                color="blue"
                weight={5}
                dashArray="10, 10"
              />
            )}

            {/* Render incidents */}
            {incidents.map((incident, index) => (
              <Circle
                key={`incident-${index}`}
                center={[incident.lat, incident.lon]}
                radius={100}
                color={incident.type === "accident" ? "red" : "orange"}
                fillColor={incident.type === "accident" ? "red" : "orange"}
                fillOpacity={0.5}
              >
                <Popup>
                  <div>
                    <h3>{incident.type.charAt(0).toUpperCase() + incident.type.slice(1)}</h3>
                    <p>Reported at: {new Date(incident.timestamp).toLocaleTimeString()}</p>
                    <p>Expected clearance: {new Date(incident.expected_clearance).toLocaleTimeString()}</p>
                  </div>
                </Popup>
              </Circle>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}

export default App
