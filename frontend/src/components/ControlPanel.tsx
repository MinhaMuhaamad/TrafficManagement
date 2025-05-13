"use client"
import { useState, useEffect } from "react"
import type React from "react"
import { Construction as Traffic,  Car, AlertTriangle, Search } from "lucide-react"

interface ControlPanelProps {
  trafficLights: any[]
  vehicles: any[]
  controlTrafficLight: (nodeId: string, state: string) => void
  addVehicle: (origin: string, destination: string, type: string) => void
  cityGraph: any
  trafficLightMode: string
  manualLightControl: any
}
export const ControlPanel: React.FC<ControlPanelProps> = ({
  trafficLights,
  vehicles,
  controlTrafficLight,
  addVehicle,
  cityGraph,
  trafficLightMode,
  manualLightControl,
}) => {
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredLights, setFilteredLights] = useState<any[]>([])
  const [selectedLight, setSelectedLight] = useState<any>(null)
  const [selectedState, setSelectedState] = useState<string>("red")
  const [activeSection, setActiveSection] = useState("traffic-lights")
  const [routeOrigin, setRouteOrigin] = useState("")
  const [routeDestination, setRouteDestination] = useState("")
  const [routeVehicleType, setRouteVehicleType] = useState("car")
  const [availableNodes, setAvailableNodes] = useState<any[]>([])

  useEffect(() => {
    if (cityGraph && cityGraph.nodes) {
      setAvailableNodes(cityGraph.nodes)
    }
  }, [cityGraph])

  useEffect(() => {
    if (trafficLights) {
      setFilteredLights(trafficLights.filter((light) => light.id.toLowerCase().includes(searchTerm.toLowerCase())))
    }
  }, [searchTerm, trafficLights])

  const handleLightSelect = (light: any) => {
    setSelectedLight(light)
    setSelectedState(light.state)
  }

  const handleStateChange = () => {
    if (selectedLight) {
      controlTrafficLight(selectedLight.id, selectedState)
    }
  }

  const handleAddVehicle = () => {
    addVehicle(routeOrigin, routeDestination, routeVehicleType)
    // Don't reset the form to make it easier to add multiple vehicles
  }

  return (
    <div className="control-panel">
      <div className="control-panel-header">
        <h2>Traffic Control Center</h2>
        <div className="control-tabs">
          <button
            className={activeSection === "traffic-lights" ? "active" : ""}
            onClick={() => setActiveSection("traffic-lights")}
          >
            <Traffic size={16} />
            Traffic Lights
          </button>
          <button
            className={activeSection === "vehicle-routing" ? "active" : ""}
            onClick={() => setActiveSection("vehicle-routing")}
          >
            <Car size={16} />
            Vehicle Routing
          </button>
        </div>
      </div>

      {activeSection === "traffic-lights" && (
        <div className="traffic-light-control">
          <div className="control-section-header">
            <h3>Traffic Light Management</h3>
            {trafficLightMode !== "manual" && (
              <div className="mode-warning">
                <AlertTriangle size={16} />
                <span>Switch to Manual mode in Settings to control lights</span>
              </div>
            )}
          </div>

          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search traffic lights..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="traffic-lights-grid">
            {filteredLights.map((light) => (
              <div
                key={light.id}
                className={`traffic-light-card ${selectedLight?.id === light.id ? "selected" : ""}`}
                onClick={() => handleLightSelect(light)}
              >
                <div className="light-header">
                  <h4>Light {light.id}</h4>
                  <div className={`light-indicator ${light.state}`} />
                </div>
                <div className="light-details">
                  <div>Queue: {light.queue_length} vehicles</div>
                  <div>Next change: {Math.max(0, Math.floor((light.next_change - Date.now()) / 1000))}s</div>
                </div>
              </div>
            ))}
          </div>

          {selectedLight && (
            <div className="light-control-panel">
              <h3>Control Light {selectedLight.id}</h3>

              <div className="light-status">
                <div>
                  Current State: <span className={selectedLight.state}>{selectedLight.state.toUpperCase()}</span>
                </div>
                <div>Queue Length: {selectedLight.queue_length} vehicles</div>
              </div>

              <div className="state-selector">
                <h4>Set New State:</h4>
                <div className="light-control-buttons">
                  <button
                    className={`light-button red ${selectedState === "red" ? "active" : ""}`}
                    onClick={() => setSelectedState("red")}
                    disabled={trafficLightMode !== "manual"}
                  >
                    Red
                  </button>
                  <button
                    className={`light-button yellow ${selectedState === "yellow" ? "active" : ""}`}
                    onClick={() => setSelectedState("yellow")}
                    disabled={trafficLightMode !== "manual"}
                  >
                    Yellow
                  </button>
                  <button
                    className={`light-button green ${selectedState === "green" ? "active" : ""}`}
                    onClick={() => setSelectedState("green")}
                    disabled={trafficLightMode !== "manual"}
                  >
                    Green
                  </button>
                </div>

                <button className="apply-button" onClick={handleStateChange} disabled={trafficLightMode !== "manual"}>
                  Apply Changes
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {activeSection === "vehicle-routing" && (
        <div className="vehicle-routing-control">
          <div className="control-section-header">
            <h3>Vehicle Routing Management</h3>
            <div className="active-vehicles">
              <Car size={16} />
              <span>{vehicles.length} active vehicles</span>
            </div>
          </div>

          <div className="routing-form">
            <h4>Add New Vehicle</h4>

            <div className="form-group">
              <label htmlFor="route-origin">Origin Node:</label>
              <input
                id="route-origin"
                type="text"
                value={routeOrigin}
                onChange={(e) => setRouteOrigin(e.target.value)}
                placeholder="Node ID or leave empty for random"
                list="available-nodes"
              />
            </div>

            <div className="form-group">
              <label htmlFor="route-destination">Destination Node:</label>
              <input
                id="route-destination"
                type="text"
                value={routeDestination}
                onChange={(e) => setRouteDestination(e.target.value)}
                placeholder="Node ID or leave empty for random"
                list="available-nodes"
              />

              <datalist id="available-nodes">
                {availableNodes.map((node) => (
                  <option key={node.id} value={node.id} />
                ))}
              </datalist>
            </div>

            <div className="form-group">
              <label htmlFor="vehicle-type">Vehicle Type:</label>
              <select id="vehicle-type" value={routeVehicleType} onChange={(e) => setRouteVehicleType(e.target.value)}>
                <option value="car">Car</option>
                <option value="bus">Bus</option>
                <option value="truck">Truck</option>
              </select>
            </div>

            <button className="add-vehicle-button" onClick={handleAddVehicle}>
              <Car size={16} />
              Add Vehicle
            </button>
          </div>

          <div className="routing-info">
            <h4>Vehicle Distribution</h4>

            <div className="vehicle-stats">
              <div className="vehicle-stat-item">
                <div className="vehicle-icon car">
                  <Car size={20} />
                </div>
                <div className="vehicle-count">{vehicles.filter((v) => v.type === "car" || !v.type).length}</div>
                <div className="vehicle-label">Cars</div>
              </div>

              <div className="vehicle-stat-item">
                <div className="vehicle-icon bus">
                  <Car size={20} />
                </div>
                <div className="vehicle-count">{vehicles.filter((v) => v.type === "bus").length}</div>
                <div className="vehicle-label">Buses</div>
              </div>

              <div className="vehicle-stat-item">
                <div className="vehicle-icon truck">
                  <Car size={20} />
                </div>
                <div className="vehicle-count">{vehicles.filter((v) => v.type === "truck").length}</div>
                <div className="vehicle-label">Trucks</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
export {}
