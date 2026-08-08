import React from 'react';
import { EventTimeline, TimelineEvent } from '../../components/composites/EventTimeline';
import { Panel } from '../../components/composites/Panel';

export const EventTimelineView: React.FC = () => {
  const events: TimelineEvent[] = [
    { id: '1', time: '14:32:01', title: 'Autonomous Offboard Takeoff Commenced', description: 'Target Altitude: 50m AGL • Rate: 2.5 m/s', severity: 'INFO' },
    { id: '2', time: '14:33:14', title: 'Corridor Alpha Dubins Spline Locked', description: 'Curvature < 28 deg centrifugal roll limit', severity: 'INFO' },
    { id: '3', time: '14:35:42', title: 'High-power Wind Shear Spike Detected', description: 'Crosswind 16.4 m/s • Groundspeed compensation active', severity: 'WARN' },
    { id: '4', time: '14:38:09', title: 'Zero-Trust ECDSA Signature Validated', description: 'Cryptographic SHA-256 flight block committed', severity: 'INFO' },
  ];

  return (
    <Panel title="Mission Cognitive Event Timeline" badge="REAL-TIME" badgeVariant="info">
      <EventTimeline events={events} />
    </Panel>
  );
};
