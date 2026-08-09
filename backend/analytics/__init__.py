"""Analytics Bounded Context Package."""

from backend.analytics.mission_economics import MissionEconomicsEngine

# Alias for backwards compatibility
MissionEconomicsCalculator = MissionEconomicsEngine

__all__ = ["MissionEconomicsEngine", "MissionEconomicsCalculator"]
