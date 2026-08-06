"""AI Copilot — natural language to full mission package."""

import logging
from typing import Any, Dict, List, Optional

from backend.intelligence.mission.semantic_planner import SemanticMissionPlanner

logger = logging.getLogger("mission_copilot")


class MissionCopilot:
    """
    Operator-facing NL interface.
    Examples: "Map this region", "Inspect power lines", "Minimize civilian exposure"
    """

    TEMPLATES = {
        "map": "Survey the selected region with maximum coverage and minimum overlap",
        "inspect": "Inspect infrastructure while minimizing risk and preserving battery",
        "powerline": "Inspect power lines at safe altitude avoiding populated areas",
        "civilian": "Minimize civilian exposure and maintain low corridor risk",
        "stealth": "Minimize RF exposure and avoid jamming corridors",
    }

    def __init__(self):
        self._planner = SemanticMissionPlanner()

    def parse_operator_message(self, message: str) -> str:
        """Expand shorthand into operational intent."""
        m = message.lower().strip()
        if m.startswith("map"):
            return self.TEMPLATES["map"]
        if "power line" in m or "powerline" in m:
            return self.TEMPLATES["powerline"]
        if "inspect" in m:
            return self.TEMPLATES["inspect"]
        if "civilian" in m or "populated" in m:
            return self.TEMPLATES["civilian"]
        if "rf" in m or "stealth" in m or "jamming" in m:
            return self.TEMPLATES["stealth"]
        return message

    def generate_mission_package(
        self,
        message: str,
        origin: Dict[str, float],
        geospatial_context: Optional[Dict[str, Any]] = None,
        waypoints: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        intent = self.parse_operator_message(message)
        
        # Phase 14: Autonomous Checks
        checks = {
            "weather": "GREEN" if (geospatial_context or {}).get("weather", {}).get("wind_mps", 0) < 12 else "WARNING",
            "airspace": "OPEN" if (geospatial_context or {}).get("airspace", {}).get("restriction_level") == "low" else "RESTRICTED",
            "battery": "OK" if origin.get("battery", 1.0) > 0.3 else "CRITICAL",
            "traffic": "LOW" if (geospatial_context or {}).get("airspace", {}).get("active_traffic", 0) < 3 else "MODERATE",
        }
        
        plan = self._planner.plan_from_intent(intent, origin, geospatial_context, waypoints)
        summary = self._summarize(plan.to_dict())
        
        return {
            "copilot_message": message,
            "resolved_intent": intent,
            "checks": checks,
            "plan": plan.to_dict(),
            "operator_summary": f"{summary} | Checks: W:{checks['weather']} A:{checks['airspace']} B:{checks['battery']} T:{checks['traffic']}",
        }

    def _summarize(self, plan: Dict[str, Any]) -> str:
        n = len(plan.get("waypoints", []))
        risk = plan.get("max_risk", 0.5) * 100
        return (
            f"Generated {n}-waypoint mission · max risk {risk:.0f}% · "
            f"recovery {plan.get('recovery_strategy')} · "
            f"{len(plan.get('contingencies', []))} contingencies"
        )
