"""Autonomous operations economics — insurance, uptime, maintenance leverage."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger("ops.economics")


@dataclass
class OperationalLeverageReport:
    crash_reduction_index: float
    insurance_risk_reduction_pct: float
    fleet_uptime_optimization_pct: float
    maintenance_forecast_savings_pct: float
    operational_leverage_score: float
    pilot_reduction_pct: float

    def to_dict(self) -> Dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class OperationalEconomicsPlatform:
    """Extends enterprise ROI with flight-hour and hardware-informed economics."""

    def __init__(self, aircraft_value_usd: float = 15000.0):
        self.aircraft_value = aircraft_value_usd
        self._crashes_prevented = 0
        self._cycles = 0

    def analyze_cycle(
        self,
        snapshot: Dict[str, Any],
        enterprise_roi: Optional[Dict] = None,
        flight_hours: Optional[Dict] = None,
        hardware: Optional[Dict] = None,
    ) -> OperationalLeverageReport:
        self._cycles += 1
        roi = enterprise_roi or {}
        if float(snapshot.get("inference", {}).get("crash_probability", 0)) > 0.7:
            if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
                self._crashes_prevented += 1

        crashes = roi.get("crashes_prevented", self._crashes_prevented)
        crash_idx = min(1.0, crashes / max(1, self._cycles) * 50)

        insurance = float(roi.get("insurance_risk_reduction_pct", 0))
        if hardware:
            hw_surv = float(hardware.get("hardware_survivability_factor", 1))
            insurance = max(insurance, (1 - hw_surv) * 100 * 0.3)

        uptime = float(roi.get("fleet_uptime_pct", 85))
        maint = float(roi.get("maintenance_optimization_pct", 0))
        if hardware and hardware.get("maintenance_urgency") == "scheduled":
            maint = max(maint, 12.0)

        pilot_red = float(roi.get("human_intervention_reduction_pct", 0))
        leverage = min(1.0, crash_idx * 0.35 + insurance / 100 * 0.2 + uptime / 100 * 0.25 + maint / 100 * 0.2)

        return OperationalLeverageReport(
            crash_reduction_index=crash_idx,
            insurance_risk_reduction_pct=insurance,
            fleet_uptime_optimization_pct=uptime,
            maintenance_forecast_savings_pct=maint,
            operational_leverage_score=leverage,
            pilot_reduction_pct=pilot_red,
        )
