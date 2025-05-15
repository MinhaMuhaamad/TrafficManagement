"use client"

import { useState, useEffect } from "react"
import type React from "react"
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, Polyline } from "react-leaflet"
import L from "leaflet"
import { Clock, Navigation, Car, Bus, Truck, AlertTriangle } from "lucide-react"

interface RoutePlannerProps {
  cityGraph: any
  mapCenter: [number, number]
  mapZoom: number
  addVehicle: (origin: string, destination: string, type: string) => void
  showToast: (message: string, type: string) => void
}

export const RoutePlanner: React.FC<RoutePlannerProps> = ({
  cityGraph,
  mapCenter,
  mapZoom,
  addVehicle,
  showToast,
}) => {
  const [originMarker, setOriginMarker] = useState<[number, number] | null>(null)
  const [destinationMarker, setDestinationMarker] = useState<[number, number] | null>(null)
  const [routeMode, setRouteMode] = useState<"origin" | "destination">("origin")
  const [vehicleType, setVehicleType] = useState<"car" | "bus" | "truck">("car")
  const [plannedRoute, setPlannedRoute] = useState<any>(null)
  const [routeDetails, setRouteDetails] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Custom map click handler
  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        const { lat, lng } = e.latlng
        if (routeMode === "origin") {
          setOriginMarker([lat, lng])
          setRouteMode("destination")
          showToast("Origin point set. Now click to set destination.", "info")
        } else {
          setDestinationMarker([lat, lng])
          setRouteMode("origin")
          // Automatically plan route when both points are set
          planRoute(originMarker![0], originMarker![1], lat, lng)
        }
      },
    })
    return null
  }

  // Function to plan a route
  const planRoute = async (originLat: number, originLon: number, destLat: number, destLon: number) => {
    if (!originLat || !originLon || !destLat || !destLon) {
      showToast("Please set both origin and destination points", "error")
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch("http://localhost:8001/route/plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin_lat: originLat,
          origin_lon: originLon,
          destination_lat: destLat,
          destination_lon: destLon,
        }),
      })

      const data = await response.json()
      if (data.status === "success") {
        setPlannedRoute(data.route.route)
        setRouteDetails(data.route)
        showToast("Route planned successfully", "success")
      } else {
        showToast(data.message, "error")
      }
    } catch (error) {
      console.error("Error planning route:", error)
      showToast("Error planning route", "error")
    } finally {
      setIsLoading(false)
    }
  }

  // Function to add a vehicle with the planned route
  const addVehicleWithRoute = async () => {
    if (!originMarker || !destinationMarker || !routeDetails) {
      showToast("Please plan a route first", "error")
      return
    }

    try {
      const response = await fetch("http://localhost:8001/vehicles/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin_lat: originMarker[0],
          origin_lon: originMarker[1],
          destination_lat: destinationMarker[0],
          destination_lon: destinationMarker[1],
          type: vehicleType,
        }),
      })

      const data = await response.json()
      if (data.status === "success") {
        showToast(`New ${vehicleType} added with optimized route`, "success")
        // Reset the route planner
        setOriginMarker(null)
        setDestinationMarker(null)
        setPlannedRoute(null)
        setRouteDetails(null)
      } else {
        showToast(data.message, "error")
      }
    } catch (error) {
      console.error("Error adding vehicle:", error)
      showToast("Error adding vehicle", "error")
    }
  }

  // Reset the route planner
  const resetRoute = () => {
    setOriginMarker(null)
    setDestinationMarker(null)
    setPlannedRoute(null)
    setRouteDetails(null)
    setRouteMode("origin")
    showToast("Route planner reset", "info")
  }

  return (
    <div className="route-planner">
      <div className="route-planner-header">
        <h2>Smart Route Planner</h2>
        <p>Click on the map to set origin and destination points</p>
      </div>

      <div className="route-controls">
        <div className="control-group">
          <label>Vehicle Type:</label>
          <div className="vehicle-type-selector">
            <button
              className={vehicleType === "car" ? "active" : ""}
              onClick={() => setVehicleType("car")}
            >
              <Car size={16} />
              Car
            </button>
            <button
              className={vehicleType === "bus" ? "active" : ""}
              onClick={() => setVehicleType("bus")}
            >
              <Bus size={16} />
              Bus
            </button>
            <button
              className={vehicleType === "truck" ? "active" : ""}
              onClick={() => setVehicleType("truck")}
            >
              <Truck size={16} />
              Truck
            </button>
          </div>
        </div>

        <div className="control-group">
          <label>Mode:</label>
          <div className="mode-indicator">
            {routeMode === "origin" ? (
              <span className="origin-mode">
                <Navigation size={16} />
                Set Origin
              </span>
            ) : (
              <span className="destination-mode">
                <Navigation size={16} />
                Set Destination
              </span>
            )}
          </div>
        </div>

        <div className="action-buttons">
          <button
            className="reset-button"
            onClick={resetRoute}
            disabled={!originMarker && !destinationMarker}
          >
            Reset
          </button>
          <button
            className="add-vehicle-button"
            onClick={addVehicleWithRoute}
            disabled={!plannedRoute || isLoading}
          >
            {isLoading ? "Loading..." : "Add Vehicle"}
          </button>
        </div>
      </div>

      <div className="map-container route-map">
        <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapClickHandler />

          {/* Origin Marker */}
          {originMarker && (
            <Marker position={originMarker}>
              <Popup>
                <div>
                  <strong>Origin</strong>
                  <p>
                    Lat: {originMarker[0].toFixed(6)}, Lon: {originMarker[1].toFixed(6)}
                  </p>
                  {routeDetails && (
                    <p>
                      <strong>Nearest Node:</strong> {routeDetails.origin.node_name}
                    </p>
                  )}
                </div>
              </Popup>
            </Marker>
          )}

          {/* Destination Marker */}
          {destinationMarker && (
            <Marker position={destinationMarker}>
              <Popup>
                <div>
                  <strong>Destination</strong>
                  <p>
                    Lat: {destinationMarker[0].toFixed(6)}, Lon: {destinationMarker[1].toFixed(6)}
                  </p>
                  {routeDetails && (
                    <p>
                      <strong>Nearest Node:</strong> {routeDetails.destination.node_name}
                    </p>
                  )}
                </div>
              </Popup>
            </Marker>
          )}

          {/* Planned Route */}
          {plannedRoute && (
            <Polyline
              positions={plannedRoute.map((point: any) => [point.lat, point.lon])}
              color="#3b82f6"
              weight={5}
              opacity={0.7}
            />
          )}
        </MapContainer>
      </div>

      {/* Route Details */}
      {routeDetails && (
        <div className="route-details">
          <h3>Route Details</h3>
          <div className="detail-item">
            <Clock size={16} />
            <span>Travel Time: {routeDetails.travel_time_minutes.toFixed(1)} minutes</span>
          </div>
          <div className="detail-item">
            <Navigation size={16} />
            <span>Distance: {routeDetails.distance_km.toFixed(2)} km</span>
          </div>
          <div className="detail-item">
            <AlertTriangle size={16} />
            <span>
              Congestion Level:{" "}
              <span
                className={
                  routeDetails.congestion_factor < 0.3
                    ? "low-congestion"
                    : routeDetails.congestion_factor < 0.6
                    ? "medium-congestion"
                    : "high-congestion"
                }
              >
                {(routeDetails.congestion_factor * 100).toFixed(0)}%
              </span>
            </span>
          </div>
          <div className="route-nodes">
            <h4>Route Path:</h4>
            <ol>
              {plannedRoute.map((point: any, index: number) => (
                <li key={index}>{point.name}</li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  )
}
