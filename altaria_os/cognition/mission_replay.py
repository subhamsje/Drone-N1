"""Human-AI operational cognition — mission reasoning replay for operators."""

import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mission_replay")


@dataclass
class CognitionReplayFrame:
    frame_id: str
    timestamp: float
    action: str
    survivability: float
    reasoning_summary: str
    operator_questions_answered: Dict[str, str]

    def to_dict(self) -> Dict:
        return self.__dict__


class MissionCognitionReplayEngine:
    """Explainable collaborative autonomy — why actions, landings, recovery, routes."""

    def __init__(self, max_frames: int = 500):
        self._frames: deque = deque(maxlen=max_frames)
        self._session_id = str(uuid.uuid4())[:8]

    def record_cycle(self, snapshot: Dict[str, Any], explanation: Dict[str, Any]) -> CognitionReplayFrame:
        decision = snapshot.get("decision", {})
        action = decision.get("action", "NONE")
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0))
        exp = explanation or {}

        answers = {
            "why_action": "; ".join(exp.get("reasoning_chain", [])[:3]) or f"Action {action} from cognition utility",
            "why_landing": exp.get("landing_rationale", snapshot.get("landing_zone", {}).get("selection_reason", "best_score")),
            "why_recovery": exp.get("survival_rationale", snapshot.get("survival", {}).get("strategy", "none")),
            "why_route_change": snapshot.get("route_governance", {}).get("reroute_reason", "none"),
            "why_confidence_degraded": exp.get("uncertainty_explanation", ""),
        }

        frame = CognitionReplayFrame(
            frame_id=f"{self._session_id}-{len(self._frames)}",
            timestamp=time.time(),
            action=action,
            survivability=surv,
            reasoning_summary=exp.get("survival_rationale", "")[:120],
            operator_questions_answered=answers,
        )
        self._frames.append(frame)
        return frame

    def get_replay(self, last_n: int = 20) -> Dict[str, Any]:
        frames = list(self._frames)[-last_n:]
        return {
            "session_id": self._session_id,
            "frame_count": len(self._frames),
            "frames": [f.to_dict() for f in frames],
            "survival_visualization": {
                "timestamps": [f.timestamp for f in frames],
                "survivability": [f.survivability for f in frames],
                "actions": [f.action for f in frames],
            },
        }
