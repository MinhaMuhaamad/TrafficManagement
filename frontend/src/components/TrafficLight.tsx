import type React from "react"

interface TrafficLightProps {
  id: string
  state: "green" | "red" | "yellow"
  nextChange: number
  queueLength: number
}

export const TrafficLight: React.FC<TrafficLightProps> = ({ id, state, nextChange, queueLength }) => {
  // Calculate time until next change
  const timeUntilChange = Math.max(0, Math.floor((nextChange - Date.now()) / 1000))

  return (
    <div className="traffic-light-popup">
      <h3>Traffic Light {id}</h3>
      <div className="light-status">
        <div className={`light-indicator ${state}`} />
        <span>Current state: {state.toUpperCase()}</span>
      </div>
      <p>Changes in: {timeUntilChange} seconds</p>
      <p>Queue length: {queueLength} vehicles</p>
    </div>
  )
}
