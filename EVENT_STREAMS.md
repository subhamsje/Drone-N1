# Altaria OS — Event Stream Specification

## Primary WebSocket: `ws://localhost:8080/ws/v1/stream`

### Channel: `operating_state`
High-frequency broadcast containing the unified system state.

#### Data Structure (JSON):
```typescript
interface OperatingState {
  ts: number;
  uav_id: string;
  aircraft: {
    geo: { lat: number; lon: number };
    altitude_m: number;
    heading_deg: number;
    velocity_mps: number;
    battery_pct: number;
    flight_mode: string;
    gps_fix: string;
    rssi: number;
  };
  cognition: {
    composite_survivability: number;
    action: string;
    reasoning_chain: string[];
  };
  survivability: {
    crash_probability: number;
    strategy: string;
    landing_zone?: { lat: number; lon: number };
  };
  world: {
    forecast: { nodes: Array<{ state: string; prob: number }> };
  };
}
```

### Channel: `fleet`
Real-time swarm synchronization and collaborative mesh state.

### Channel: `hardware`
Hardware twin telemetry including motor stress, ESC temperatures, and battery health.
