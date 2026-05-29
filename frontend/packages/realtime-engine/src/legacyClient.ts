/** @deprecated Use CognitionStreamEngine — kept for compatibility */
import { BehaviorSubject, Subject } from 'rxjs';
import type { CognitionEnvelope, StreamMessage } from '@altaria/cognition-sdk';

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

const COGNITION_CHANNELS = [
  'all', 'cognition', 'survival', 'world_model', 'swarm', 'trust',
  'hardware', 'adversarial', 'airspace', 'certification',
] as const;

export class CognitionStreamClient {
  readonly envelope$ = new BehaviorSubject<CognitionEnvelope | null>(null);
  readonly channel$ = new Subject<StreamMessage>();
  readonly connection$ = new BehaviorSubject<ConnectionState>('disconnected');
  readonly latency$ = new BehaviorSubject<number>(0);
  private ws: WebSocket | null = null;

  constructor(private url: string) {}

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this.connection$.next('connecting');
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      this.connection$.next('connected');
      this.ws?.send(JSON.stringify({ subscribe: [...COGNITION_CHANNELS] }));
    };
    this.ws.onmessage = (ev) => {
      const t0 = performance.now();
      try {
        const msg = JSON.parse(ev.data as string) as StreamMessage;
        this.channel$.next(msg);
        if ((msg.channel === 'cognition' || msg.channel === 'all') && (msg.data as CognitionEnvelope)?.cognition) {
          this.envelope$.next(msg.data as CognitionEnvelope);
        }
        this.latency$.next(performance.now() - t0);
      } catch { /* ignore */ }
    };
    this.ws.onclose = () => this.connection$.next('disconnected');
    this.ws.onerror = () => this.connection$.next('error');
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
    this.connection$.next('disconnected');
  }
}
