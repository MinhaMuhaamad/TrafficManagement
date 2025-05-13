"use client"

import { useState } from "react"
import type React from "react"

interface TrafficLightProps {
  id: string
  state: "green" | "red" | "yellow"
  nextChange: number
  queueLength: number
  controlTrafficLight?: (nodeId: string, state: string) => void
  trafficLightMode?: string
}

export const TrafficLight: React.FC<TrafficLightProps> = ({
  id,
  state,
  nextChange,
  queueLength,
  controlTrafficLight,
  trafficLightMode,
}) => {
  // Calculate time until next change
  const timeUntilChange = Math.max(0, Math.floor((nextChange - Date.now()) / 1000))
  const [selectedState, setSelectedState] = useState<string>(state)

  const handleStateChange = (newState: string) => {
    setSelectedState(newState)
    if (controlTrafficLight) {
      controlTrafficLight(id, newState)
    }
  }

  return (
    <div className="traffic-light-popup">
      <h3>Traffic Light {id}</h3>

      <div className="light-status">
        <div className={`light-indicator ${state}`} />
        <span>Current state: {state.toUpperCase()}</span>
      </div>

      <p>Changes in: {timeUntilChange} seconds</p>
      <p>Queue length: {queueLength} vehicles</p>

      {controlTrafficLight && trafficLightMode === "manual" && (
        <div className="traffic-light-controls">
          <h4>Manual Control</h4>
          <div className="light-control-buttons">
            <button
              className={`light-button red ${selectedState === "red" ? "active" : ""}`}
              onClick={() => handleStateChange("red")}
            >
              Red
            </button>
            <button
              className={`light-button yellow ${selectedState === "yellow" ? "active" : ""}`}
              onClick={() => handleStateChange("yellow")}
            >
              Yellow
            </button>
            <button
              className={`light-button green ${selectedState === "green" ? "active" : ""}`}
              onClick={() => handleStateChange("green")}
            >
              Green
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
