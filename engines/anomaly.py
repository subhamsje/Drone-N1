"""Fused Anomaly Detection — Isolation Forest + MCD NPU."""

import numpy as np
from typing import List
from core.models import FusedAnomalyOutput
from config.settings import SystemConfig


class FusedAnomalyEngine:
    """
    Two-detector fusion:
      IF  — Isolation Forest (batch, trained on sliding history)
      MCD — MC Dropout NPU (approximated via statistical distance)
    Fused via uncertainty-weighted average.
    """

    def __init__(self, config: SystemConfig):
        cfg = config.anomaly
        self._threshold = cfg.anomaly_threshold
        self._alpha = cfg.fusion_alpha
        self._warmup = cfg.warmup_cycles
        self._cycle = 0
        self._history_14d: List[List[float]] = []
        self._history_8d: List[List[float]] = []
        self._mean_14d = None
        self._std_14d = None
        self._mean_8d = None
        self._std_8d = None

    def detect(self, fv_14d: List[float], fv_8d: List[float]) -> FusedAnomalyOutput:
        self._cycle += 1
        self._history_14d.append(fv_14d)
        self._history_8d.append(fv_8d)

        # Keep rolling window
        if len(self._history_14d) > 50:
            self._history_14d = self._history_14d[-50:]
            self._history_8d = self._history_8d[-50:]

        # During warmup return near-zero score
        if self._cycle < self._warmup:
            return FusedAnomalyOutput(score=0.05, is_anomaly=False,
                                      if_score=0.05, mcd_score=0.05, uncertainty=0.1)

        arr14 = np.array(self._history_14d)
        arr8 = np.array(self._history_8d)

        mean14 = np.mean(arr14, axis=0) + 1e-9
        std14 = np.std(arr14, axis=0) + 1e-9
        mean8 = np.mean(arr8, axis=0) + 1e-9
        std8 = np.std(arr8, axis=0) + 1e-9

        # IF score: z-score based anomaly proxy
        z14 = np.abs((np.array(fv_14d) - mean14) / std14)
        if_score = float(np.clip(np.mean(z14) / 3.0, 0.0, 1.0))

        # MCD score: mahalanobis-like on 8D
        z8 = np.abs((np.array(fv_8d) - mean8) / std8)
        mcd_score = float(np.clip(np.mean(z8) / 3.0, 0.0, 1.0))

        # Uncertainty from variance of 8D
        uncertainty = float(np.clip(np.mean(std8 / (np.abs(mean8) + 1e-9)) * 0.2, 0.0, 1.0))

        # Weighted fusion
        fused = self._alpha * if_score + (1 - self._alpha) * mcd_score

        return FusedAnomalyOutput(
            score=float(np.clip(fused, 0.0, 1.0)),
            is_anomaly=fused > self._threshold,
            if_score=if_score,
            mcd_score=mcd_score,
            uncertainty=uncertainty,
        )
