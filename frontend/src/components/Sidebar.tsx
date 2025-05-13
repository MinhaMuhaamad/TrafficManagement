"use client"

import type React from "react"
import { useState } from "react"
import { PanelLeft, Play, Square, AlertTriangle, Car } from "lucide-react"

interface SidebarProps {
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
}) => {
  const [isOpen, setIsOpen] = useState(true)
  const [activeTab, setActiveTab] = useState("simulation")
  const [incidentForm, setIncidentForm] = useState({
    lat: "",
    lon: "",
    type: "accident",
  })

  const handleIncidentSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const { lat, lon, type } = incidentForm
    addIncident(Number.parseFloat(lat), Number.parseFloat(lon), type)
    setIncidentForm({ lat: "", lon: "", type: "accident" })
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

          <div className="sidebar-tabs">
            <button className={activeTab === "simulation" ? "active" : ""} onClick={() => setActiveTab("simulation")}>
              Simulation
            </button>
            <button className={activeTab === "vehicles" ? "active" : ""} onClick={() => setActiveTab("vehicles")}>
              Vehicles
            </button>
            <button className={activeTab === "incidents" ? "active" : ""} onClick={() => setActiveTab("incidents")}>
              Incidents
            </button>
          </div>

          {activeTab === "simulation" && (
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
              </div>
            </div>
          )}

          {activeTab === "vehicles" && (
            <div className="tab-content">
              <h3>Active Vehicles</h3>
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
                      <Car size={16} />
                      <div className="vehicle-info">
                        <span>Vehicle {vehicle.id}</span>
                        <small>
                          {vehicle.origin} → {vehicle.destination}
                        </small>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === "incidents" && (
            <div className="tab-content">
              <h3>Report Incident</h3>
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

                <button type="submit" className="report-button">
                  <AlertTriangle size={16} />
                  Report Incident
                </button>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
