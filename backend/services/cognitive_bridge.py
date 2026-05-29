"""Bridge to existing N1 cognitive engines + Altaria OS kernel enrichment."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.config import BACKEND_CONFIG
from backend.services.cognition_service import CognitionService

logger = logging.getLogger("cognitive_bridge")


class CognitiveBridge:
    """
    Wraps UAVHybridEngine for backend consumption.
    Each cycle: physics pipeline → Altaria OS kernel enrichment.
    """

    def __init__(self, uav_id: str = "Altaria-Alpha"):
        self.uav_id = uav_id
        self._engine = None
        self._running = False
        self._callbacks: List[Callable] = []
        self._task: Optional[asyncio.Task] = None
        cfg = BACKEND_CONFIG.cognitive
        self._cognition = CognitionService(uav_id, cfg.fleet_id)

    def _ensure_engine(self):
        if self._engine is None:
            from config.settings import CONFIG
            from main import UAVHybridEngine
            self._engine = UAVHybridEngine(CONFIG)

    def on_snapshot(self, callback: Callable):
        self._callbacks.append(callback)

    def _extract_feature_vector(self) -> Optional[List[float]]:
        try:
            dt = self._engine.digital_twin
            tel = dt.get_window()[-1] if dt.get_window() else None
            if tel is None:
                return None
            ekf = self._engine.ekf.get_state()
            pred = self._engine.predictor.predict(dt.get_window())
            return list(dt.get_feature_vector(tel, pred.battery, pred.rpm, ekf))
        except Exception:
            return None

    async def run_cycle(self) -> Dict[str, Any]:
        self._ensure_engine()
        snap = await self._engine._execute_cycle()
        d = snap.to_dict()
        d["uav_id"] = self.uav_id

        fv = self._extract_feature_vector()
        d = await self._cognition.enrich(d, fv)

        for cb in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(d)
                else:
                    cb(d)
            except Exception as e:
                logger.error("Snapshot callback error: %s", e)
        return d

    async def start_loop(self, interval_ms: int = 200):
        self._running = True
        interval = interval_ms / 1000.0
        logger.info("Cognitive OS loop started for %s @ %dms", self.uav_id, interval_ms)
        while self._running:
            t0 = asyncio.get_event_loop().time()
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error("Cognitive cycle error: %s", e)
            elapsed = asyncio.get_event_loop().time() - t0
            await asyncio.sleep(max(0.0, interval - elapsed))

    def start_background(self, interval_ms: int = 200):
        self._task = asyncio.create_task(self.start_loop(interval_ms))

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    @property
    def cycle(self) -> int:
        return self._engine._cycle if self._engine else 0

    @property
    def os_kernel(self):
        return self._cognition.kernel
