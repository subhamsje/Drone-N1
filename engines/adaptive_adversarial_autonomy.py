"""Adaptive adversarial autonomy — intent inference, telemetry poisoning, mission hardening."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("adaptive_adversarial")


@dataclass
class AdversarialAutonomyState:
    adversarial_intent: str
    intent_confidence: float
    telemetry_poisoning: bool
    sabotage_indicators: List[str]
    hardened_behaviors: List[str]
    contested_cognition_mode: str

    def to_dict(self) -> Dict:
        return self.__dict__


class AdaptiveAdversarialAutonomyEngine:
    """Contested-environment cognition atop adversarial_operations + cyber_warfare."""

    def __init__(self):
        self._intent_history: List[str] = []
        self._hardening_active = False

    def assess(
        self,
        snapshot: Dict[str, Any],
        adversarial_ops: Dict[str, Any],
        cyber_warfare: Dict[str, Any],
    ) -> AdversarialAutonomyState:
        attacks = cyber_warfare.get("attacks", [])
        deception = adversarial_ops.get("deception_detected", False)
        hardening = adversarial_ops.get("mission_hardening_level", "standard")

        intent = "benign"
        conf = 0.1
        sabotage = []
        hardened = []

        if deception:
            intent = "environmental_deception"
            conf = 0.75
            sabotage.append("gps_telemetry_inconsistency")

        attack_types = [a.get("type", "") for a in attacks if isinstance(a, dict)]
        if "gps_spoof" in str(attack_types) or snapshot.get("cybersecurity", {}).get("is_spoofed"):
            intent = "gps_spoof_campaign"
            conf = max(conf, 0.85)
            hardened.extend(["vio_primary", "gps_rx_isolate"])

        if len(attacks) >= 2:
            intent = "multi_vector_attack"
            conf = 0.9
            sabotage.append("coordinated_rf_mavlink")

        innov = float(snapshot.get("ekf", {}).get("innovation_mag", 0))
        trust_high = float(snapshot.get("sensor_trust", {}).get("composite_trust", 1)) > 0.85
        if innov > 1.5 and trust_high:
            sabotage.append("telemetry_poisoning_suspected")
            intent = "telemetry_poisoning" if conf < 0.7 else intent
            conf = max(conf, 0.65)

        perc_adv = float((snapshot.get("adversarial_perception") or {}).get("adversarial_score", 0))
        if perc_adv > 0.55:
            sabotage.append("adversarial_optical")
            hardened.append("thermal_radar_fallback")

        if hardening in ("elevated", "maximum"):
            self._hardening_active = True
            hardened.extend(["reduce_aggression", "survival_bias_max", "trust_rotation"])

        mode = "contested" if conf > 0.5 or self._hardening_active else "nominal"
        self._intent_history.append(intent)
        if len(self._intent_history) > 50:
            self._intent_history = self._intent_history[-25:]

        return AdversarialAutonomyState(
            adversarial_intent=intent,
            intent_confidence=conf,
            telemetry_poisoning="telemetry_poisoning" in sabotage,
            sabotage_indicators=sabotage,
            hardened_behaviors=hardened,
            contested_cognition_mode=mode,
        )
