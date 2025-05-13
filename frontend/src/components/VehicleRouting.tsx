import type React from "react"

interface VehicleRoutingProps {
  id: string
  type: string
  origin: string
  destination: string
  currentRoute: any[]
  eta: number
  speed?: number
  status?: string
}

export const VehicleRouting: React.FC<VehicleRoutingProps> = ({
  id,
  type,
  origin,
  destination,
  currentRoute,
  eta,
  speed = 0,
  status = "moving",
}) => {
  // Calculate ETA in minutes
  const etaMinutes = Math.max(0, Math.floor((eta - Date.now()) / 60000))

  // Format speed
  const formattedSpeed = speed.toFixed(1)

  return (
    <div className="vehicle-popup">
      <h3>
        {type.charAt(0).toUpperCase() + type.slice(1)} {id}
      </h3>
      <div className="vehicle-status">
        Status: <span className={`status-${status.toLowerCase()}`}>{status}</span>
      </div>
      <div className="vehicle-details">
        <p>
          <strong>From:</strong> {origin}
        </p>
        <p>
          <strong>To:</strong> {destination}
        </p>
        <p>
          <strong>ETA:</strong> {etaMinutes} minutes
        </p>
        <p>
          <strong>Speed:</strong> {formattedSpeed} km/h
        </p>
        <p>
          <strong>Route length:</strong> {currentRoute?.length || 0} segments
        </p>
      </div>
    </div>
  )
}
