"""Kafka event producer adapter — production streaming."""

import json
import logging

from backend.events.schemas import DomainEvent
from backend.events.topics import Topic

logger = logging.getLogger("kafka_adapter")


class KafkaEventProducer:
    """Async Kafka producer — activates when aiokafka installed."""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap = bootstrap_servers
        self._producer = None
        self._enabled = False

    async def start(self):
        try:
            from aiokafka import AIOKafkaProducer
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap,
                value_serializer=lambda v: json.dumps(v).encode(),
            )
            await self._producer.start()
            self._enabled = True
            logger.info("Kafka producer connected: %s", self.bootstrap)
        except ImportError:
            logger.warning("aiokafka not installed — Kafka disabled")
        except Exception as e:
            logger.warning("Kafka start failed: %s", e)

    async def publish(self, event: DomainEvent, topic: Topic):
        if not self._enabled or not self._producer:
            return
        try:
            await self._producer.send_and_wait(topic.value, event.to_dict())
        except Exception as e:
            logger.error("Kafka publish error: %s", e)

    async def stop(self):
        if self._producer:
            await self._producer.stop()
