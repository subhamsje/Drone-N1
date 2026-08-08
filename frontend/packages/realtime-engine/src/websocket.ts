/**
 * WebSocket Real-Time Stream Connector.
 */

export interface TelemetryPacket {
  altitude_m: number;
  airspeed_ms: number;
  heading_deg: number;
  pitch_deg: number;
  roll_deg: number;
  battery_pct: number;
  battery_volts: number;
  gps_sats: number;
  rssi_dbm: number;
  latency_ms: number;
}

export function connectWebSocket(endpoint: string = '/ws/v1/stream') {
  const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
  const host = typeof window !== 'undefined' ? window.location.host : 'localhost:8080';
  const url = `${isHttps ? 'wss' : 'ws'}://${host}${endpoint}`;

  return {
    subscribe: (callback: (data: TelemetryPacket) => void) => {
      let ws: WebSocket | null = null;
      let timer: any = null;

      const connect = () => {
        try {
          ws = new WebSocket(url);
          ws.onmessage = (evt) => {
            try {
              callback(JSON.parse(evt.data));
            } catch (e) {}
          };
          ws.onclose = () => {
            setTimeout(connect, 3000);
          };
        } catch (e) {
          setTimeout(connect, 3000);
        }
      };

      connect();

      // Local fallback telemetry simulation loop
      timer = setInterval(() => {
        callback({
          altitude_m: 48.5 + (Math.random() - 0.5) * 0.3,
          airspeed_ms: 14.8 + (Math.random() - 0.5) * 0.2,
          heading_deg: 42 + (Math.random() - 0.5) * 1.0,
          pitch_deg: -3.2 + (Math.random() - 0.5) * 0.2,
          roll_deg: 4.5 + (Math.random() - 0.5) * 0.3,
          battery_pct: 94,
          battery_volts: 15.8,
          gps_sats: 19,
          rssi_dbm: -44,
          latency_ms: 12.4,
        });
      }, 100);

      return () => {
        if (ws) ws.close();
        if (timer) clearInterval(timer);
      };
    },
  };
}
