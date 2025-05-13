import type React from "react"

interface VehicleRoutingProps {
  id: string
  origin: string
  destination: string
  currentRoute: any[]
  eta: number
}

export const VehicleRouting: React.FC<VehicleRoutingProps> = ({ id, origin, destination, currentRoute, eta }) => {
  // Calculate ETA in minutes
  const etaMinutes = Math.max(0, Math.floor((eta - Date.now()) / 60000))

  return (
    <div className="vehicle-popup">
      <h3>Vehicle {id}</h3>
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
        <strong>Route length:</strong> {currentRoute?.length || 0} segments
      </p>
    </div>
  )
}
