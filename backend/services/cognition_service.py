"""Backend service wrapper for OS cognition layer."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from altaria_os.kernel import CognitiveOSKernel


class CognitionService:
    def __init__(self, uav_id: str, fleet_id: str):
        self.kernel = CognitiveOSKernel(uav_id, fleet_id)

    async def enrich(self, snapshot: Dict[str, Any], feature_vector: Optional[list] = None) -> Dict[str, Any]:
        return await self.kernel.process(snapshot, feature_vector)

    def set_autonomy_mode(self, mode: str):
        from altaria_os.autonomy_modes import AutonomyMode
        self.kernel.autonomy.set_mode(AutonomyMode(mode))
