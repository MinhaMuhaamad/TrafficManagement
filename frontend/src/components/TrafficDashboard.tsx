"use client"

import type React from "react"
import { useMemo } from "react"

interface TrafficDashboardProps {
  trafficLights: any[]
  vehicles: any[]
  incidents: any[]
  congestionLevels: Record<string, number>
}

export const TrafficDashboard: React.FC<TrafficDashboardProps> = ({
  trafficLights,
  vehicles,
  incidents,
  congestionLevels,
}) => {
  // Calculate statistics
  const stats = useMemo(() => {
    // Count green and red lights
    const greenLights = trafficLights.filter((light) => light.state === "green").length
    const redLights = trafficLights.filter((light) => light.state === "red").length

    // Calculate average congestion
    const avgCongestion =
      Object.values(congestionLevels).length > 0
        ? Object.values(congestionLevels).reduce((sum: any, val: any) => sum + val, 0) /
          Object.values(congestionLevels).length
        : 0

    // Count incidents by type
    const accidentCount = incidents.filter((inc) => inc.type === "accident").length
    const congestionCount = incidents.filter((inc) => inc.type === "congestion").length

    return {
      greenLights,
      redLights,
      vehicleCount: vehicles.length,
      avgCongestion: (avgCongestion * 100).toFixed(1),
      accidentCount,
      congestionCount,
    }
  }, [trafficLights, vehicles, incidents, congestionLevels])

  return (
    <div className="traffic-dashboard">
      <div className="dashboard-header">
        <h2>Traffic Management Dashboard</h2>
        <span className="dashboard-time">{new Date().toLocaleTimeString()}</span>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Vehicles</h3>
          <div className="stat-value">{stats.vehicleCount}</div>
        </div>

        <div className="stat-card">
          <h3>Traffic Lights</h3>
          <div className="stat-value">
            <span className="green-count">{stats.greenLights} green</span> /
            <span className="red-count">{stats.redLights} red</span>
          </div>
        </div>

        <div className="stat-card">
          <h3>Congestion</h3>
          <div className="stat-value">{stats.avgCongestion}%</div>
        </div>

        <div className="stat-card">
          <h3>Incidents</h3>
          <div className="stat-value">
            <span className="accident-count">{stats.accidentCount} accidents</span> /
            <span className="congestion-count">{stats.congestionCount} jams</span>
          </div>
        </div>
      </div>
    </div>
  )
}
