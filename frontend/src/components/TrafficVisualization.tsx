import React from 'react';
import { LayerGroup } from 'react-leaflet';
import { TrafficFlowLines } from './TrafficFlowLines';
import { IncidentMarkers } from './IncidentMarkers';

interface TrafficVisualizationProps {
  congestionData: any;
  incidents: Array<{
    id: string;
    type: string;
    location: [number, number];
    description: string;
  }>;
  trafficFlow: any;
}
export const TrafficVisualization: React.FC<TrafficVisualizationProps> = ({
  congestionData,
  incidents,
  trafficFlow
}) => {
  return (
    <LayerGroup>
      <TrafficFlowLines data={trafficFlow} />
      <IncidentMarkers incidents={incidents} />
    </LayerGroup>
  );
};