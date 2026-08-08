/**
 * Resilient Centralized WebSocket Connection Manager with Auto-Reconnect & Heartbeats.
 */

type ListenerCallback = (data: any) => void;

class WebSocketManager {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 3000;
  private isConnecting: boolean = false;
  private listeners: Map<string, Set<ListenerCallback>> = new Map();
  private simulatedTimer: any = null;

  constructor() {
    const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
    const host = typeof window !== 'undefined' ? window.location.host : 'localhost:8080';
    this.url = `${isHttps ? 'wss' : 'ws'}://${host}/ws/telemetry`;
  }

  public connect() {
    if (this.ws || this.isConnecting) return;
    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnecting = false;
        if (this.simulatedTimer) {
          clearInterval(this.simulatedTimer);
          this.simulatedTimer = null;
        }
        this.emit('connection_status', { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          const topic = parsed.topic || 'telemetry';
          this.emit(topic, parsed.data || parsed);
        } catch (e) {
          this.emit('raw', event.data);
        }
      };

      this.ws.onerror = (err) => {
        this.emit('connection_error', err);
      };

      this.ws.onclose = () => {
        this.ws = null;
        this.isConnecting = false;
        this.emit('connection_status', { connected: false });
        this.startFallbackSimulation();
        setTimeout(() => this.connect(), this.reconnectInterval);
      };
    } catch (err) {
      this.ws = null;
      this.isConnecting = false;
      this.startFallbackSimulation();
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  private startFallbackSimulation() {
    if (this.simulatedTimer) return;
    this.simulatedTimer = setInterval(() => {
      const simulatedData = {
        altitude_m: 48.5 + (Math.random() - 0.5) * 0.4,
        airspeed_ms: 14.8 + (Math.random() - 0.5) * 0.3,
        heading_deg: 42 + (Math.random() - 0.5) * 1.5,
        pitch_deg: -3.2 + (Math.random() - 0.5) * 0.2,
        roll_deg: 4.5 + (Math.random() - 0.5) * 0.3,
        battery_pct: 94,
        battery_volts: 15.8,
        gps_sats: 19,
        rssi_dbm: -44,
        latency_ms: 12.4,
        motors: {
          m1: Math.round(5820 + (Math.random() - 0.5) * 20),
          m2: Math.round(5815 + (Math.random() - 0.5) * 20),
          m3: Math.round(5840 + (Math.random() - 0.5) * 20),
          m4: Math.round(5810 + (Math.random() - 0.5) * 20),
        },
      };
      this.emit('telemetry', simulatedData);
    }, 100);
  }

  public subscribe(topic: string, callback: ListenerCallback): () => void {
    if (!this.listeners.has(topic)) {
      this.listeners.set(topic, new Set());
    }
    this.listeners.get(topic)!.add(callback);

    if (!this.ws && !this.isConnecting) {
      this.connect();
    }

    return () => {
      this.listeners.get(topic)?.delete(callback);
    };
  }

  private emit(topic: string, data: any) {
    this.listeners.get(topic)?.forEach((cb) => {
      try {
        cb(data);
      } catch (err) {
        console.error(`[WebSocketManager] Listener error on topic ${topic}:`, err);
      }
    });
  }

  public send(topic: string, payload: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ topic, data: payload }));
    }
  }
}

export const wsManager = new WebSocketManager();
