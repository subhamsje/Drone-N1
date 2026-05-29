"""Prometheus metrics for backend observability."""

from typing import Optional

# Optional prometheus_client — graceful fallback
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MetricsRegistry:
    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE
        if not self.enabled:
            self._counters = {}
            self._histograms = {}
            return

        self.telemetry_ingested = Counter(
            "altaria_telemetry_ingested_total", "Telemetry messages ingested", ["uav_id"]
        )
        self.cognitive_cycles = Counter(
            "altaria_cognitive_cycles_total", "Cognitive loop cycles", ["uav_id"]
        )
        self.recovery_triggered = Counter(
            "altaria_recovery_triggered_total", "Recovery workflows started", ["uav_id", "policy"]
        )
        self.anomalies_detected = Counter(
            "altaria_anomalies_total", "Anomalies detected", ["uav_id"]
        )
        self.cycle_latency = Histogram(
            "altaria_cycle_latency_ms", "Cognitive cycle latency ms",
            buckets=[10, 25, 50, 100, 200, 500, 1000],
        )
        self.risk_gauge = Gauge("altaria_risk_value", "Current risk value", ["uav_id"])
        self.fleet_health = Gauge("altaria_fleet_health", "Fleet health score", ["fleet_id"])
        self.events_published = Counter(
            "altaria_events_published_total", "Domain events published", ["event_type"]
        )
        self.inference_latency = Histogram(
            "altaria_inference_latency_ms", "AI inference latency",
            buckets=[5, 10, 25, 50, 80, 150, 300],
        )
        self.survival_triggers = Counter(
            "altaria_survival_triggers_total", "Survival engine activations", ["urgency"]
        )
        self.sensor_trust_gps = Gauge("altaria_gps_confidence", "GPS sensor confidence", ["uav_id"])

    def record_cycle(self, uav_id: str, latency_ms: float, risk: float):
        if not self.enabled:
            return
        self.cognitive_cycles.labels(uav_id=uav_id).inc()
        self.cycle_latency.observe(latency_ms)
        self.risk_gauge.labels(uav_id=uav_id).set(risk)

    def record_ingest(self, uav_id: str):
        if self.enabled:
            self.telemetry_ingested.labels(uav_id=uav_id).inc()

    def record_recovery(self, uav_id: str, policy: str):
        if self.enabled:
            self.recovery_triggered.labels(uav_id=uav_id, policy=policy).inc()

    def record_event(self, event_type: str):
        if self.enabled:
            self.events_published.labels(event_type=event_type).inc()

    def record_inference(self, latency_ms: float):
        if self.enabled:
            self.inference_latency.observe(latency_ms)

    def record_survival(self, urgency: str):
        if self.enabled:
            self.survival_triggers.labels(urgency=urgency).inc()

    def record_sensor_trust(self, uav_id: str, gps_conf: float):
        if self.enabled:
            self.sensor_trust_gps.labels(uav_id=uav_id).set(gps_conf)

    def export(self) -> tuple:
        if self.enabled:
            return generate_latest(), CONTENT_TYPE_LATEST
        return b"# prometheus_client not installed\n", "text/plain"


_metrics: Optional[MetricsRegistry] = None


def get_metrics() -> MetricsRegistry:
    global _metrics
    if _metrics is None:
        _metrics = MetricsRegistry()
    return _metrics
