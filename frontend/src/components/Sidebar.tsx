"use client"

import type React from "react"
import { useState } from "react"
import {
  PanelLeft,
  Play,
  Square,
  AlertTriangle,
  Car,
  Settings,
  Map,
  Sliders,
  BarChart3,
  Eye,
  EyeOff,
  Bus,
  Truck,
} from "lucide-react"

export interface SidebarProps {
  isConnected: boolean
  simulationRunning: boolean
  startSimulation: () => void
  stopSimulation: () => void
  cityName: string
  availableCities: string[]
  changeCity: (city: string) => void
  vehicles: any[]
  selectedVehicle: string | null
  setSelectedVehicle: (id: string | null) => void
  addIncident: (lat: number, lon: number, type: string) => void
  activeTab: string
  setActiveTab: (tab: string) => void
  simulationSpeed: number
  trafficLightMode: string
  routingAlgorithm: string
  updateSimulationSettings: (settings: any) => void
  addVehicle: (origin: string, destination: string, type: string) => void
  showCongestion: boolean
  setShowCongestion: (show: boolean) => void
  showVehicles: boolean
  setShowVehicles: (show: boolean) => void
  showTrafficLights: boolean
  setShowTrafficLights: (show: boolean) => void
  showIncidents: boolean
  setShowIncidents: (show: boolean) => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  isConnected,
  simulationRunning,
  startSimulation,
  stopSimulation,
  cityName,
  availableCities,
  changeCity,
  vehicles,
  selectedVehicle,
  setSelectedVehicle,
  addIncident,
  activeTab,
  setActiveTab,
  simulationSpeed,
  trafficLightMode,
  routingAlgorithm,
  updateSimulationSettings,
  addVehicle,
  showCongestion,
  setShowCongestion,
  showVehicles,
  setShowVehicles,
  showTrafficLights,
  setShowTrafficLights,
  showIncidents,
  setShowIncidents,
}) => {
  const [isOpen, setIsOpen] = useState(true)
  const [sidebarTab, setSidebarTab] = useState("simulation")
  const [incidentForm, setIncidentForm] = useState({
    lat: "",
    lon: "",
    type: "accident",
    severity: "medium",
  })
  const [settingsForm, setSettingsForm] = useState({
    speed: simulationSpeed,
    trafficLightMode: trafficLightMode,
    routingAlgorithm: routingAlgorithm,
  })
  const [vehicleForm, setVehicleForm] = useState({
    origin: "",
    destination: "",
    type: "car",
  })

  const handleIncidentSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const { lat, lon, type } = incidentForm
    addIncident(Number.parseFloat(lat), Number.parseFloat(lon), type)
    setIncidentForm({ ...incidentForm, lat: "", lon: "" })
  }

  const handleSettingsSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateSimulationSettings({
      speed: settingsForm.speed,
      traffic_light_mode: settingsForm.trafficLightMode,
      routing_algorithm: settingsForm.routingAlgorithm,
    })
  }

  const handleVehicleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const { origin, destination, type } = vehicleForm
    addVehicle(origin, destination, type)
    setVehicleForm({ ...vehicleForm, origin: "", destination: "" })
  }

  return (
    <div className={`sidebar ${isOpen ? "open" : "closed"}`}>
      <div className="sidebar-toggle" onClick={() => setIsOpen(!isOpen)}>
        <PanelLeft size={20} />
      </div>

      {isOpen && (
        <div className="sidebar-content">
          <div className="sidebar-header">
            <h2>Smart Traffic Management</h2>
            <div className={`connection-status ${isConnected ? "connected" : "disconnected"}`}>
              {isConnected ? "Connected" : "Disconnected"}
            </div>
          </div>

          <div className="main-tabs">
            <button
              className={activeTab === "map" ? "active" : ""}
              onClick={() => setActiveTab("map")}
              title="Map View"
            >
              <Map size={18} />
              <span>Map</span>
            </button>
            <button
              className={activeTab === "control" ? "active" : ""}
              onClick={() => setActiveTab("control")}
              title="Control Panel"
            >
              <Sliders size={18} />
              <span>Control</span>
            </button>
            <button
              className={activeTab === "analytics" ? "active" : ""}
              onClick={() => setActiveTab("analytics")}
              title="Analytics"
            >
              <BarChart3 size={18} />
              <span>Analytics</span>
            </button>
          </div>

          <div className="sidebar-tabs">
            <button className={sidebarTab === "simulation" ? "active" : ""} onClick={() => setSidebarTab("simulation")}>
              Simulation
            </button>
            <button className={sidebarTab === "vehicles" ? "active" : ""} onClick={() => setSidebarTab("vehicles")}>
              Vehicles
            </button>
            <button className={sidebarTab === "incidents" ? "active" : ""} onClick={() => setSidebarTab("incidents")}>
              Incidents
            </button>
            <button className={sidebarTab === "settings" ? "active" : ""} onClick={() => setSidebarTab("settings")}>
              Settings
            </button>
          </div>

          {sidebarTab === "simulation" && (
            <div className="tab-content">
              <div className="city-selector">
                <label htmlFor="city-select">Select City:</label>
                <select
                  id="city-select"
                  value={cityName}
                  onChange={(e) => changeCity(e.target.value)}
                  disabled={simulationRunning}
                >
                  {availableCities.map((city) => (
                    <option key={city} value={city}>
                      {city}
                    </option>
                  ))}
                </select>
              </div>

              <div className="simulation-controls">
                <button
                  className={`start-button ${simulationRunning ? "disabled" : ""}`}
                  onClick={startSimulation}
                  disabled={simulationRunning || !isConnected}
                >
                  <Play size={16} />
                  Start Simulation
                </button>

                <button
                  className={`stop-button ${!simulationRunning ? "disabled" : ""}`}
                  onClick={stopSimulation}
                  disabled={!simulationRunning || !isConnected}
                >
                  <Square size={16} />
                  Stop Simulation
                </button>
              </div>

              <div className="simulation-info">
                <h3>Simulation Status</h3>
                <p>
                  Status:{" "}
                  <span className={simulationRunning ? "running" : "stopped"}>
                    {simulationRunning ? "Running" : "Stopped"}
                  </span>
                </p>
                <p>City: {cityName}</p>
                <p>Vehicles: {vehicles.length}</p>
                <p>Speed: {simulationSpeed}x</p>
                <p>Traffic Light Mode: {trafficLightMode}</p>
                <p>Routing Algorithm: {routingAlgorithm === "a_star" ? "A*" : "Dijkstra"}</p>
              </div>
            </div>
          )}

          {sidebarTab === "vehicles" && (
            <div className="tab-content">
              <h3>Active Vehicles</h3>

              <div className="vehicle-filter">
                <button
                  className={`toggle-button ${showVehicles ? "active" : ""}`}
                  onClick={() => setShowVehicles(!showVehicles)}
                >
                  {showVehicles ? <Eye size={16} /> : <EyeOff size={16} />}
                  {showVehicles ? "Hide Vehicles" : "Show Vehicles"}
                </button>
              </div>

              <div className="vehicle-list">
                {vehicles.length === 0 ? (
                  <p>No vehicles in simulation</p>
                ) : (
                  vehicles.map((vehicle) => (
                    <div
                      key={vehicle.id}
                      className={`vehicle-item ${selectedVehicle === vehicle.id ? "selected" : ""}`}
                      onClick={() => setSelectedVehicle(vehicle.id === selectedVehicle ? null : vehicle.id)}
                    >
                      {vehicle.type === "bus" ? (
                        <Bus size={16} />
                      ) : vehicle.type === "truck" ? (
                        <Truck size={16} />
                      ) : (
                        <Car size={16} />
                      )}
                      <div className="vehicle-info">
                        <span>
                          {vehicle.type || "Vehicle"} {vehicle.id}
                        </span>
                        <small>
                          {vehicle.origin} → {vehicle.destination}
                        </small>
                        <small className="vehicle-speed">
                          {vehicle.speed ? `${vehicle.speed.toFixed(1)} km/h` : "Stopped"}
                        </small>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="add-vehicle-form">
                <h3>Add Vehicle</h3>
                <form onSubmit={handleVehicleSubmit}>
                  <div className="form-group">
                    <label htmlFor="vehicle-origin">Origin (Node ID):</label>
                    <input
                      id="vehicle-origin"
                      type="text"
                      value={vehicleForm.origin}
                      onChange={(e) => setVehicleForm({ ...vehicleForm, origin: e.target.value })}
                      placeholder="Enter node ID or leave empty for random"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="vehicle-destination">Destination (Node ID):</label>
                    <input
                      id="vehicle-destination"
                      type="text"
                      value={vehicleForm.destination}
                      onChange={(e) => setVehicleForm({ ...vehicleForm, destination: e.target.value })}
                      placeholder="Enter node ID or leave empty for random"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="vehicle-type">Vehicle Type:</label>
                    <select
                      id="vehicle-type"
                      value={vehicleForm.type}
                      onChange={(e) => setVehicleForm({ ...vehicleForm, type: e.target.value })}
                    >
                      <option value="car">Car</option>
                      <option value="bus">Bus</option>
                      <option value="truck">Truck</option>
                    </select>
                  </div>

                  <button type="submit" className="add-button" disabled={!simulationRunning}>
                    <Car size={16} />
                    Add Vehicle
                  </button>
                </form>
              </div>
            </div>
          )}

          {sidebarTab === "incidents" && (
            <div className="tab-content">
              <h3>Report Incident</h3>

              <div className="incident-filter">
                <button
                  className={`toggle-button ${showIncidents ? "active" : ""}`}
                  onClick={() => setShowIncidents(!showIncidents)}
                >
                  {showIncidents ? <Eye size={16} /> : <EyeOff size={16} />}
                  {showIncidents ? "Hide Incidents" : "Show Incidents"}
                </button>
              </div>

              <form onSubmit={handleIncidentSubmit}>
                <div className="form-group">
                  <label htmlFor="incident-lat">Latitude:</label>
                  <input
                    id="incident-lat"
                    type="number"
                    step="0.0001"
                    value={incidentForm.lat}
                    onChange={(e) => setIncidentForm({ ...incidentForm, lat: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="incident-lon">Longitude:</label>
                  <input
                    id="incident-lon"
                    type="number"
                    step="0.0001"
                    value={incidentForm.lon}
                    onChange={(e) => setIncidentForm({ ...incidentForm, lon: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="incident-type">Type:</label>
                  <select
                    id="incident-type"
                    value={incidentForm.type}
                    onChange={(e) => setIncidentForm({ ...incidentForm, type: e.target.value })}
                  >
                    <option value="accident">Accident</option>
                    <option value="congestion">Heavy Congestion</option>
                    <option value="construction">Construction</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="incident-severity">Severity:</label>
                  <select
                    id="incident-severity"
                    value={incidentForm.severity}
                    onChange={(e) => setIncidentForm({ ...incidentForm, severity: e.target.value })}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <button type="submit" className="report-button" disabled={!simulationRunning}>
                  <AlertTriangle size={16} />
                  Report Incident
                </button>
              </form>
            </div>
          )}

          {sidebarTab === "settings" && (
            <div className="tab-content">
              <h3>Simulation Settings</h3>

              <form onSubmit={handleSettingsSubmit}>
                <div className="form-group">
                  <label htmlFor="simulation-speed">Simulation Speed:</label>
                  <select
                    id="simulation-speed"
                    value={settingsForm.speed}
                    onChange={(e) => setSettingsForm({ ...settingsForm, speed: Number(e.target.value) })}
                  >
                    <option value="0.5">0.5x (Slow)</option>
                    <option value="1">1x (Normal)</option>
                    <option value="2">2x (Fast)</option>
                    <option value="5">5x (Very Fast)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="traffic-light-mode">Traffic Light Mode:</label>
                  <select
                    id="traffic-light-mode"
                    value={settingsForm.trafficLightMode}
                    onChange={(e) => setSettingsForm({ ...settingsForm, trafficLightMode: e.target.value })}
                  >
                    <option value="auto">Automatic (Dynamic Programming)</option>
                    <option value="fixed">Fixed Timing</option>
                    <option value="adaptive">Adaptive (Queue-based)</option>
                    <option value="manual">Manual Control</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="routing-algorithm">Routing Algorithm:</label>
                  <select
                    id="routing-algorithm"
                    value={settingsForm.routingAlgorithm}
                    onChange={(e) => setSettingsForm({ ...settingsForm, routingAlgorithm: e.target.value })}
                  >
                    <option value="a_star">A* Algorithm</option>
                    <option value="dijkstra">Dijkstra's Algorithm</option>
                  </select>
                </div>

                <h3>Display Settings</h3>

                <div className="toggle-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={showCongestion}
                      onChange={() => setShowCongestion(!showCongestion)}
                    />
                    Show Road Congestion
                  </label>
                </div>

                <div className="toggle-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={showTrafficLights}
                      onChange={() => setShowTrafficLights(!showTrafficLights)}
                    />
                    Show Traffic Lights
                  </label>
                </div>

                <button type="submit" className="settings-button">
                  <Settings size={16} />
                  Apply Settings
                </button>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
