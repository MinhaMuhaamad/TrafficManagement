"use client"

import type React from "react"
import { useMemo } from "react"
import { Car, AlertTriangle, Clock, TrendingUp, TrendingDown, BarChart3 } from "lucide-react"

export interface TrafficDashboardProps {
  trafficLights: any[]
  vehicles: any[]
  incidents: any[]
  congestionLevels: Record<string, number>
  analyticsData: any  // Added this prop
}
export const TrafficDashboard: React.FC<TrafficDashboardProps> = ({
  trafficLights,
  vehicles,
  incidents,
  congestionLevels,
  analyticsData,
}) => {
  // Calculate statistics
  const stats = useMemo(() => {
    // Count green and red lights
    const greenLights = trafficLights.filter((light) => light.state === "green").length
    const redLights = trafficLights.filter((light) => light.state === "red").length
    const yellowLights = trafficLights.filter((light) => light.state === "yellow").length

    // Calculate average congestion
    const avgCongestion =
      Object.values(congestionLevels).length > 0
        ? Object.values(congestionLevels).reduce((sum: any, val: any) => sum + val, 0) /
          Object.values(congestionLevels).length
        : 0

    // Count incidents by type
    const accidentCount = incidents.filter((inc) => inc.type === "accident").length
    const congestionCount = incidents.filter((inc) => inc.type === "congestion").length
    const constructionCount = incidents.filter((inc) => inc.type === "construction").length

    // Count vehicles by type
    const carCount = vehicles.filter((v) => v.type === "car" || !v.type).length
    const busCount = vehicles.filter((v) => v.type === "bus").length
    const truckCount = vehicles.filter((v) => v.type === "truck").length

    // Calculate average speed
    const avgSpeed = vehicles.length > 0 ? vehicles.reduce((sum, v) => sum + (v.speed || 0), 0) / vehicles.length : 0

    return {
      greenLights,
      redLights,
      yellowLights,
      vehicleCount: vehicles.length,
      carCount,
      busCount,
      truckCount,
      avgCongestion: (avgCongestion * 100).toFixed(1),
      accidentCount,
      congestionCount,
      constructionCount,
      avgSpeed: avgSpeed.toFixed(1),
      trafficEfficiency: analyticsData?.trafficLightEfficiency || 0,
      congestionTrend: analyticsData?.congestionTrend || [],
    }
  }, [trafficLights, vehicles, incidents, congestionLevels, analyticsData])

  // Determine congestion trend
  const congestionTrend = useMemo(() => {
    if (stats.congestionTrend.length < 2) return "stable"
    const lastTwo = stats.congestionTrend.slice(-2)
    if (lastTwo[1] > lastTwo[0] + 0.05) return "up"
    if (lastTwo[1] < lastTwo[0] - 0.05) return "down"
    return "stable"
  }, [stats.congestionTrend])

  return (
    <div className="traffic-dashboard">
      <div className="dashboard-header">
        <h2>Traffic Management Dashboard</h2>
        <span className="dashboard-time">{new Date().toLocaleTimeString()}</span>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <Car size={20} />
          </div>
          <div className="stat-content">
            <h3>Vehicles</h3>
            <div className="stat-value">{stats.vehicleCount}</div>
            <div className="stat-details">
              <span>{stats.carCount} cars</span>
              <span>{stats.busCount} buses</span>
              <span>{stats.truckCount} trucks</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Clock size={20} />
          </div>
          <div className="stat-content">
            <h3>Traffic Lights</h3>
            <div className="stat-value">
              <span className="green-count">{stats.greenLights} green</span> /
              <span className="yellow-count">{stats.yellowLights} yellow</span> /
              <span className="red-count">{stats.redLights} red</span>
            </div>
            <div className="stat-details">
              <span>Efficiency: {(stats.trafficEfficiency * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            {congestionTrend === "up" ? (
              <TrendingUp size={20} className="trend-up" />
            ) : congestionTrend === "down" ? (
              <TrendingDown size={20} className="trend-down" />
            ) : (
              <BarChart3 size={20} />
            )}
          </div>
          <div className="stat-content">
            <h3>Congestion</h3>
            <div className="stat-value">{stats.avgCongestion}%</div>
            <div className="stat-details">
              <span>Avg. Speed: {stats.avgSpeed} km/h</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>
          <div className="stat-content">
            <h3>Incidents</h3>
            <div className="stat-value">
              <span className="accident-count">{stats.accidentCount} accidents</span>
            </div>
            <div className="stat-details">
              <span className="congestion-count">{stats.congestionCount} jams</span>
              <span className="construction-count">{stats.constructionCount} construction</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
export {}
