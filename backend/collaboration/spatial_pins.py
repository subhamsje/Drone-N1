"""Figma-Style Multiplayer Spatial Canvas & Map Pins."""

import time
from typing import Dict, Any, List

class SpatialCollaborationEngine:
    def __init__(self):
        self._pins: List[Dict[str, Any]] = [
            {
                "id": "PIN-101",
                "author": "Capt. Vance",
                "text": "Inspect thermal hotspot on facade #4",
                "geo": {"lat": 12.972, "lon": 77.594, "alt_m": 85.0},
                "timestamp": time.time() - 300
            }
        ]

    def add_pin(self, author: str, text: str, geo: Dict[str, float]) -> Dict[str, Any]:
        pin = {
            "id": f"PIN-{len(self._pins)+101}",
            "author": author,
            "text": text,
            "geo": geo,
            "timestamp": time.time()
        }
        self._pins.append(pin)
        return pin

    def get_all_pins(self) -> List[Dict[str, Any]]:
        return self._pins
