import React from 'react';
import { Polyline } from 'react-leaflet';

interface TrafficFlowLine {
  id: string;
  flow: number;
  coordinates: [number, number][];
}

interface TrafficFlowLinesProps {
  data: TrafficFlowLine[];
}

export const TrafficFlowLines: React.FC<TrafficFlowLinesProps> = ({ data }) => {
  return (
    <>
      {data.map((line) => (
        <Polyline
          key={line.id}
          positions={line.coordinates}
          pathOptions={{
            color: getFlowColor(line.flow),
            weight: 2,
            opacity: 0.8
          }}
        />
      ))}
    </>
  );
};

function getFlowColor(flow: number): string {
  if (flow <= 0.3) return '#2196f3';
  if (flow <= 0.6) return '#ff9800';
  return '#f44336';
}