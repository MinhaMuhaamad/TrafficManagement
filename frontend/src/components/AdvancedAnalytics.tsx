import React from 'react';
import { LineChart, BarChart } from 'recharts';

export const AdvancedAnalytics: React.FC<{ data: any }> = ({ data }) => {
  return (
    <div className="analytics-dashboard">
      <div className="traffic-trends">
        <h3>Traffic Trends</h3>
        <LineChart data={data.hourlyTrends} />
      </div>
      
      <div className="congestion-analysis">
        <h3>Congestion Analysis</h3>
        <BarChart data={data.congestionLevels} />
      </div>
      
      <div className="performance-metrics">
        <div className="metric-card">
          <h4>Average Travel Time</h4>
          <p>{data.averageTravelTime} minutes</p>
        </div>
        <div className="metric-card">
          <h4>Traffic Flow Rate</h4>
          <p>{data.flowRate} vehicles/hour</p>
        </div>
      </div>
    </div>
  );
};

