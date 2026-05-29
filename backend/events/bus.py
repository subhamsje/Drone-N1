"""Event bus abstraction — memory, Redis, Kafka adapters."""

import json
import logging
from collections import defaultdict
from typing import Awaitable, Callable, Dict, List, Optional

from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic

logger = logging.getLogger("event_bus")

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """
    Async pub/sub event bus.
    Production: swap `backend=redis|kafka` in config; memory mode for dev/SITL.
    """

    def __init__(self, backend: str = "memory"):
        self._backend = backend
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._topic_handlers: Dict[Topic, List[EventHandler]] = defaultdict(list)
        self._history: List[DomainEvent] = []
        self._max_history = 10_000
        self._redis = None

    def subscribe(self, event_type: EventType, handler: EventHandler):
        self._handlers[event_type].append(handler)

    def subscribe_topic(self, topic: Topic, handler: EventHandler):
        self._topic_handlers[topic].append(handler)

    async def publish(self, event: DomainEvent, topic: Optional[Topic] = None):
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        if self._backend == "redis":
            await self._publish_redis(event, topic)
        elif self._backend == "kafka":
            await self._publish_kafka(event, topic)

        for h in self._handlers.get(event.event_type, []):
            try:
                await h(event)
            except Exception as e:
                logger.error("Handler error %s: %s", event.event_type, e)

        if topic:
            for h in self._topic_handlers.get(topic, []):
                try:
                    await h(event)
                except Exception as e:
                    logger.error("Topic handler error %s: %s", topic, e)

    async def _publish_redis(self, event: DomainEvent, topic: Optional[Topic]):
        try:
            import redis.asyncio as aioredis
            if self._redis is None:
                from backend.config import BACKEND_CONFIG
                self._redis = aioredis.from_url(BACKEND_CONFIG.events.redis_url)
            channel = (topic or Topic.TELEMETRY_NORMALIZED).value
            await self._redis.publish(channel, json.dumps(event.to_dict()))
        except ImportError:
            logger.debug("redis not installed — memory-only publish")
        except Exception as e:
            logger.warning("Redis publish failed: %s", e)

    async def _publish_kafka(self, event: DomainEvent, topic: Optional[Topic]):
        logger.debug("Kafka publish stub: %s → %s", event.event_type, topic)

    def get_history(
        self,
        uav_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[DomainEvent]:
        out = self._history
        if uav_id:
            out = [e for e in out if e.uav_id == uav_id]
        if event_type:
            out = [e for e in out if e.event_type == event_type]
        return out[-limit:]


# Global singleton for FastAPI lifespan
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        from backend.config import BACKEND_CONFIG
        _event_bus = EventBus(backend=BACKEND_CONFIG.events.backend)
    return _event_bus
