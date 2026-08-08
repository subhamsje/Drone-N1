/**
 * Centralized EventBus for cross-panel event orchestration & telemetry signals.
 */

type EventHandler<T = any> = (event: T) => void;

class EventBus {
  private handlers: Map<string, Set<EventHandler>> = new Map();

  public on<T = any>(eventName: string, handler: EventHandler<T>): () => void {
    if (!this.handlers.has(eventName)) {
      this.handlers.set(eventName, new Set());
    }
    this.handlers.get(eventName)!.add(handler);
    return () => {
      this.handlers.get(eventName)?.delete(handler);
    };
  }

  public emit<T = any>(eventName: string, event: T) {
    this.handlers.get(eventName)?.forEach((h) => {
      try {
        h(event);
      } catch (err) {
        console.error(`[EventBus] Error handling event ${eventName}:`, err);
      }
    });
  }
}

export const eventBus = new EventBus();
