"use client"

import { useState } from "react"
import type React from "react"
import { BarChart3, TrendingUp, Clock, AlertTriangle, Car, ArrowUpRight, ArrowDownRight, Minus } from "lucide-react"

interface AnalyticsProps {
  analyticsData: any
  vehicles: any[]
  trafficLights: any[]
  incidents: any[]
  congestionLevels: Record<string, number>
}

export const Analytics: React.FC<AnalyticsProps> = ({
  analyticsData,
  vehicles,
  trafficLights,
  incidents,
  congestionLevels,
}) => {
  const [activeTab, setActiveTab] = useState("overview")

  // Calculate trend indicators
  const getTrendIndicator = (current: number, previous: number, isHigherBetter = true) => {
    const diff = current - previous
    const threshold = 0.05 * previous // 5% change threshold

    if (Math.abs(diff) < threshold) {
      return <Minus className="trend-stable" />
    }

    if ((diff > 0 && isHigherBetter) || (diff < 0 && !isHigherBetter)) {
      return <ArrowUpRight className="trend-up" />
    }

    return <ArrowDownRight className="trend-down" />
  }

  // Calculate average congestion
  const avgCongestion =
    Object.values(congestionLevels).length > 0
      ? Object.values(congestionLevels).reduce((sum: any, val: any) => sum + val, 0) /
        Object.values(congestionLevels).length
      : 0

  // Get previous congestion value
  const prevCongestion =
    analyticsData.congestionTrend && analyticsData.congestionTrend.length > 1
      ? analyticsData.congestionTrend[analyticsData.congestionTrend.length - 2]
      : avgCongestion

  // Calculate average speed
  const avgSpeed = vehicles.length > 0 ? vehicles.reduce((sum, v) => sum + (v.speed || 0), 0) / vehicles.length : 0

  // Get previous speed value
  const prevSpeed =
    analyticsData.speedHistory && analyticsData.speedHistory.length > 1
      ? analyticsData.speedHistory[analyticsData.speedHistory.length - 2]
      : avgSpeed

  return (
    <div className="analytics-panel">
      <div className="analytics-header">
        <h2>Traffic Analytics Dashboard</h2>

        <div className="analytics-tabs">
          <button className={activeTab === "overview" ? "active" : ""} onClick={() => setActiveTab("overview")}>
            <BarChart3 size={16} />
            Overview
          </button>
          <button className={activeTab === "traffic" ? "active" : ""} onClick={() => setActiveTab("traffic")}>
            <TrendingUp size={16} />
            Traffic Flow
          </button>
          <button className={activeTab === "incidents" ? "active" : ""} onClick={() => setActiveTab("incidents")}>
            <AlertTriangle size={16} />
            Incidents
          </button>
        </div>
      </div>

      {activeTab === "overview" && (
        <div className="analytics-overview">
          <div className="analytics-cards">
            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Traffic Efficiency</h3>
                {getTrendIndicator(
                  analyticsData.trafficLightEfficiency || 0,
                  analyticsData.previousTrafficLightEfficiency || 0,
                )}
              </div>
              <div className="analytics-value">{((analyticsData.trafficLightEfficiency || 0) * 100).toFixed(1)}%</div>
              <div className="analytics-description">Overall traffic system efficiency</div>
            </div>

            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Average Speed</h3>
                {getTrendIndicator(avgSpeed, prevSpeed)}
              </div>
              <div className="analytics-value">
                {avgSpeed.toFixed(1)} <span className="unit">km/h</span>
              </div>
              <div className="analytics-description">Average vehicle speed across network</div>
            </div>

            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Congestion Level</h3>
                {getTrendIndicator(avgCongestion, prevCongestion, false)}
              </div>
              <div className="analytics-value">{(avgCongestion * 100).toFixed(1)}%</div>
              <div className="analytics-description">Network-wide congestion level</div>
            </div>

            <div className="analytics-card">
              <div className="analytics-card-header">
                <h3>Wait Time</h3>
                {getTrendIndicator(
                  analyticsData.averageWaitTime || 0,
                  analyticsData.previousAverageWaitTime || 0,
                  false,
                )}
              </div>
              <div className="analytics-value">
                {(analyticsData.averageWaitTime || 0).toFixed(1)} <span className="unit">sec</span>
              </div>
              <div className="analytics-description">Average wait time at intersections</div>
            </div>
          </div>

          <div className="analytics-summary">
            <h3>System Summary</h3>
            <div className="summary-stats">
              <div className="summary-stat">
                <Car size={18} />
                <span>{vehicles.length} active vehicles</span>
              </div>
              <div className="summary-stat">
                <Clock size={18} />
                <span>{trafficLights.length} traffic lights</span>
              </div>
              <div className="summary-stat">
                <AlertTriangle size={18} />
                <span>{incidents.length} active incidents</span>
              </div>
            </div>

            <div className="optimization-status">
              <h4>Optimization Status</h4>
              <div className="optimization-metrics">
                <div className="metric">
                  <div className="metric-label">Traffic Light Optimization:</div>
                  <div className="metric-value">{analyticsData.trafficLightOptimizationStatus || "Active"}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Route Optimization:</div>
                  <div className="metric-value">{analyticsData.routeOptimizationStatus || "Active"}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Congestion Management:</div>
                  <div className="metric-value">{analyticsData.congestionManagementStatus || "Active"}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "traffic" && (
        <div className="traffic-analytics">
          <h3>Traffic Flow Analysis</h3>

          <div className="traffic-metrics">
            <div className="metric-group">
              <h4>Vehicle Distribution</h4>
              <div className="vehicle-distribution">
                <div className="vehicle-type">
                  <div className="vehicle-label">Cars</div>
                  <div className="vehicle-bar-container">
                    <div
                      className="vehicle-bar car"
                      style={{
                        width: `${(vehicles.filter((v) => v.type === "car" || !v.type).length / Math.max(1, vehicles.length)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="vehicle-count">{vehicles.filter((v) => v.type === "car" || !v.type).length}</div>
                </div>

                <div className="vehicle-type">
                  <div className="vehicle-label">Buses</div>
                  <div className="vehicle-bar-container">
                    <div
                      className="vehicle-bar bus"
                      style={{
                        width: `${(vehicles.filter((v) => v.type === "bus").length / Math.max(1, vehicles.length)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="vehicle-count">{vehicles.filter((v) => v.type === "bus").length}</div>
                </div>

                <div className="vehicle-type">
                  <div className="vehicle-label">Trucks</div>
                  <div className="vehicle-bar-container">
                    <div
                      className="vehicle-bar truck"
                      style={{
                        width: `${(vehicles.filter((v) => v.type === "truck").length / Math.max(1, vehicles.length)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="vehicle-count">{vehicles.filter((v) => v.type === "truck").length}</div>
                </div>
              </div>
            </div>

            <div className="metric-group">
              <h4>Traffic Light States</h4>
              <div className="light-distribution">
                <div className="light-type">
                  <div className="light-label">Green</div>
                  <div className="light-bar-container">
                    <div
                      className="light-bar green"
                      style={{
                        width: `${(trafficLights.filter((l) => l.state === "green").length / Math.max(1, trafficLights.length)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="light-count">{trafficLights.filter((l) => l.state === "green").length}</div>
                </div>

                <div className="light-type">
                  <div className="light-label">Yellow</div>
                  <div className="light-bar-container">
                    <div
                      className="light-bar yellow"
                      style={{
                        width: `${(trafficLights.filter((l) => l.state === "yellow").length / Math.max(1, trafficLights.length)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="light-count">{trafficLights.filter((l) => l.state === "yellow").length}</div>
                </div>

                <div className="light-type">
                  <div className="light-label">Red</div>
                  <div className="light-bar-container">
                    <div
                      className="light-bar red"
                      style={{
                        width: `${(trafficLights.filter((l) => l.state === "red").length / Math.max(1, trafficLights.length)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="light-count">{trafficLights.filter((l) => l.state === "red").length}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="congestion-analysis">
            <h4>Congestion Hotspots</h4>
            <div className="hotspots-list">
              {Object.entries(congestionLevels)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([edgeId, level]) => (
                  <div key={edgeId} className="hotspot-item">
                    <div className="hotspot-name">Road {edgeId}</div>
                    <div className="hotspot-bar-container">
                      <div
                        className="hotspot-bar"
                        style={{
                          width: `${level * 100}%`,
                          backgroundColor: level < 0.3 ? "#4ade80" : level < 0.6 ? "#fb923c" : "#ef4444",
                        }}
                      />
                    </div>
                    <div className="hotspot-value">{(level * 100).toFixed(0)}%</div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === "incidents" && (
        <div className="incidents-analytics">
          <h3>Incident Analysis</h3>

          <div className="incidents-summary">
            <div className="incident-type-summary">
              <h4>Current Incidents by Type</h4>
              <div className="incident-types">
                <div className="incident-type">
                  <div className="incident-icon accident">
                    <AlertTriangle size={20} />
                  </div>
                  <div className="incident-count">{incidents.filter((i) => i.type === "accident").length}</div>
                  <div className="incident-label">Accidents</div>
                </div>

                <div className="incident-type">
                  <div className="incident-icon congestion">
                    <AlertTriangle size={20} />
                  </div>
                  <div className="incident-count">{incidents.filter((i) => i.type === "congestion").length}</div>
                  <div className="incident-label">Congestion</div>
                </div>

                <div className="incident-type">
                  <div className="incident-icon construction">
                    <AlertTriangle size={20} />
                  </div>
                  <div className="incident-count">{incidents.filter((i) => i.type === "construction").length}</div>
                  <div className="incident-label">Construction</div>
                </div>
              </div>
            </div>

            <div className="incident-history">
              <h4>Recent Incidents</h4>
              <div className="incident-list">
                {incidents.length === 0 ? (
                  <div className="no-incidents">No active incidents</div>
                ) : (
                  incidents.map((incident, index) => (
                    <div key={index} className="incident-item">
                      <div className={`incident-marker ${incident.type}`} />
                      <div className="incident-details">
                        <div className="incident-title">
                          {incident.type.charAt(0).toUpperCase() + incident.type.slice(1)}
                        </div>
                        <div className="incident-time">
                          Reported: {new Date(incident.timestamp * 1000).toLocaleTimeString()}
                        </div>
                      </div>
                      <div className="incident-clearance">
                        Clears in {Math.max(0, Math.floor((incident.expected_clearance - Date.now() / 1000) / 60))} min
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="incident-impact">
            <h4>Incident Impact Analysis</h4>
            <div className="impact-metrics">
              <div className="impact-metric">
                <div className="impact-label">Affected Vehicles:</div>
                <div className="impact-value">{analyticsData.affectedVehicles || 0}</div>
              </div>
              <div className="impact-metric">
                <div className="impact-label">Rerouted Vehicles:</div>
                <div className="impact-value">{analyticsData.reroutedVehicles || 0}</div>
              </div>
              <div className="impact-metric">
                <div className="impact-label">Avg. Delay:</div>
                <div className="impact-value">{analyticsData.averageIncidentDelay || 0} min</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
export{}