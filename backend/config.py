"""Backend platform configuration."""

from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class EventBusConfig:
    backend: str = "memory"  # memory | redis | kafka
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap: str = "localhost:9092"
    consumer_group: str = "altaria-cognitive"


@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    ws_path: str = "/ws/v1/stream"
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    jwt_secret: str = field(default_factory=lambda: os.getenv("ALTARIA_JWT_SECRET", "dev-secret-change-in-prod"))


@dataclass
class MAVLinkConfig:
    connection: str = "udp:127.0.0.1:14550"
    system_id: int = 1
    component_id: int = 1
    firewall_max_cmd_rate_hz: float = 10.0
    signed_commands: bool = False


@dataclass
class StorageConfig:
    postgres_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql://altaria:altaria@localhost:5432/altaria"
        )
    )
    timescale_url: str = field(
        default_factory=lambda: os.getenv(
            "TIMESCALE_URL", "postgresql://altaria:altaria@localhost:5433/altaria_ts"
        )
    )
    redis_url: str = "redis://localhost:6379/1"


@dataclass
class CognitiveConfig:
    loop_ms: int = 200
    simulation_mode: bool = True
    uav_id: str = "Altaria-Alpha"
    fleet_id: str = "swarm-alpha-1"
    edge_device: str = "jetson_orin"
    triton_url: str = field(default_factory=lambda: os.getenv("TRITON_URL", ""))
    enable_os_kernel: bool = True


@dataclass
class BackendConfig:
    events: EventBusConfig = field(default_factory=EventBusConfig)
    api: APIConfig = field(default_factory=APIConfig)
    mavlink: MAVLinkConfig = field(default_factory=MAVLinkConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    cognitive: CognitiveConfig = field(default_factory=CognitiveConfig)
    enable_metrics: bool = True
    enable_cognitive_loop: bool = True


BACKEND_CONFIG = BackendConfig()
