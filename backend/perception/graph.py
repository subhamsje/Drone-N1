"""Asynchronous perception graph — GPU pipeline fusion."""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import numpy as np

from backend.perception.detectors import (
    YOLODetector, DepthEstimator, SemanticSegmenter, PerceptionFrame,
    HAZARD_CLASSES, LANDABLE_CLASSES,
)

logger = logging.getLogger("perception.graph")


class PerceptionGraph:
    """
    Real-time perception micro-pipeline:
    RGB → YOLO → Depth → Segmentation → Fused scene understanding
    """

    def __init__(self, device: str = "cuda"):
        self.yolo = YOLODetector(device=device)
        self.depth = DepthEstimator()
        self.segmenter = SemanticSegmenter()
        self._last_frame: Optional[PerceptionFrame] = None
        self._obstacle_density = 0.0

    async def process_frame(self, frame: Optional[np.ndarray] = None) -> PerceptionFrame:
        t0 = time.monotonic()
        loop = asyncio.get_event_loop()

        detections, depth, classes = await asyncio.gather(
            loop.run_in_executor(None, self.yolo.detect, frame),
            loop.run_in_executor(None, self.depth.estimate, frame),
            loop.run_in_executor(None, self.segmenter.segment, frame),
        )

        hazard_count = sum(1 for d in detections if d.class_name in HAZARD_CLASSES)
        landable_count = sum(1 for d in detections if d.class_name in LANDABLE_CLASSES)
        total = max(1, len(detections))
        self._obstacle_density = hazard_count / total

        pf = PerceptionFrame(
            timestamp=time.time(),
            detections=detections,
            depth_map_available=depth is not None,
            semantic_mask_classes=classes,
            inference_ms=(time.monotonic() - t0) * 1000,
        )
        self._last_frame = pf
        return pf

    def fuse_into_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        if not self._last_frame:
            return snapshot
        pf = self._last_frame
        hazards = [d.class_name for d in pf.detections if d.class_name in HAZARD_CLASSES]
        snapshot["perception"] = {
            **pf.to_dict(),
            "obstacle_density": self._obstacle_density,
            "hazards": hazards,
            "landable_regions": sum(1 for d in pf.detections if d.class_name in LANDABLE_CLASSES),
        }
        if "vision" in snapshot:
            snapshot["vision"]["obstacle_density"] = self._obstacle_density
            snapshot["vision"]["semantic_hazards"] = hazards
        return snapshot

    @property
    def obstacle_density(self) -> float:
        return self._obstacle_density
