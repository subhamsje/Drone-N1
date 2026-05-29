"""Survival service — exposes survival plans and manual triggers."""

from typing import Any, Dict, Optional
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engines.survival import AutonomousSurvivalEngine


class SurvivalService:
    def __init__(self):
        self._engine = AutonomousSurvivalEngine()

    def evaluate(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        plan = self._engine.plan(snapshot)
        return plan.to_dict()

    def get_last_plan(self) -> Optional[Dict]:
        if self._engine._last_plan:
            return self._engine._last_plan.to_dict()
        return None
