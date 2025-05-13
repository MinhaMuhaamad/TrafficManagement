import React from 'react';
import { Circle, Popup } from 'react-leaflet';

interface Incident {
  id: string;
  type: string;
  location: [number, number];
  description: string;
}

interface IncidentMarkersProps {
  incidents: Incident[];
}

export const IncidentMarkers: React.FC<IncidentMarkersProps> = ({ incidents }) => {
  return (
    <>
      {incidents.map((incident) => (
        <Circle
          key={incident.id}
          center={incident.location}
          radius={100}
          pathOptions={{
            color: incident.type === 'accident' ? '#f44336' : '#ff9800',
            fillColor: incident.type === 'accident' ? '#f44336' : '#ff9800',
            fillOpacity: 0.5
          }}
        >
          <Popup>
            <div>
              <h3>{incident.type}</h3>
              <p>{incident.description}</p>
            </div>
          </Popup>
        </Circle>
      ))}
    </>
  );
};