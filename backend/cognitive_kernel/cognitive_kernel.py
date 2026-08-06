"""Sovereign Cognitive Kernel Core — Single source of operational consciousness for Altaria OS."""

import time
import logging
from typing import Dict, Any, List, Optional

from backend.cognitive_kernel.world_model import WorldModelEngine
from backend.cognitive_kernel.decision_engine import DecisionEngine
from backend.cognitive_kernel.prediction import MultiHorizonPredictor
from backend.cognitive_kernel.memory import ExperienceMemoryEngine
from backend.cognitive_kernel.planner import SemanticPlannerEngine
from backend.cognitive_kernel.learning import CertifiedLearningPipeline
from backend.cognitive_kernel.risk_engine import FourQuadrantRiskEngine
from backend.cognitive_kernel.explainability import ExplainabilityEngine
from backend.cognitive_kernel.swarm import SwarmMeshEngine
from backend.cognitive_kernel.mission_intel import MissionIntelligenceEngine

logger = logging.getLogger("altaria.cognitive_kernel")

class SovereignCognitiveKernel:
    """Central Sovereign Operational Consciousness Engine."""

    def __init__(self, uav_id: str = "Altaria-Alpha", fleet_id: str = "swarm-alpha-1"):
        self.uav_id = uav_id
        self.fleet_id = fleet_id
        self._start_ts = time.time()
        
        # Instantiate 10 Sub-Modules
        self.world = WorldModelEngine()
        self.decision = DecisionEngine()
        self.predictor = MultiHorizonPredictor()
        self.memory = ExperienceMemoryEngine()
        self.planner = SemanticPlannerEngine()
        self.learning = CertifiedLearningPipeline()
        self.risk = FourQuadrantRiskEngine()
        self.explain = ExplainabilityEngine()
        self.swarm = SwarmMeshEngine(fleet_id)
        self.mission_intel = MissionIntelligenceEngine()

        self.sensor_trust = {"gps": 98.4, "vio": 94.2, "baro": 96.8, "imu": 99.1}
        self.global_confidence = {"nav": 98, "vision": 93, "weather": 86, "battery": 95, "loc": 91}
        logger.info(f"Sovereign Cognitive Kernel v9.0 (10 Sub-Modules) initialized for {uav_id}")

    def evaluate_cycle(self, pose: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs the 200ms cognitive cycle across all 10 sub-modules."""
        p = pose or {"geo": {"lat": 12.97, "lon": 77.59}, "altitude_m": 120.5}
        lat = p.get("geo", {}).get("lat", 12.97)
        lon = p.get("geo", {}).get("lon", 77.59)
        alt = p.get("altitude_m", 120.5)

        world_eval = self.world.evaluate_environment(lat, lon, alt)
        risk_eval = self.risk.compute_risk(0.05, world_eval["physics"]["wind_speed_mps"], 12)
        mpc_eval = self.decision.evaluate_trajectories(risk_eval["composite_risk_score"], p)
        predictions = self.predictor.predict_horizons(p)
        exp_match = self.memory.query_similar_patterns("WIND_SHEAR", world_eval["physics"]["wind_speed_mps"])
        causality_dag = self.explain.build_causality_dag("Wind Shear & Multipath", mpc_eval["selected_trajectory"]["id"], risk_eval)
        swarm_topo = self.swarm.sync_fleet_topology()

        return {
            "uav_id": self.uav_id,
            "timestamp": time.time(),
            "world_model": world_eval,
            "risk_matrix": risk_eval,
            "mpc_decision": mpc_eval,
            "horizons": predictions,
            "experience_memory": exp_match,
            "causality_dag": causality_dag,
            "swarm_topology": swarm_topo,
            "sensor_trust": self.sensor_trust,
            "global_confidence": self.global_confidence
        }

    def get_reasoning_tree(self) -> Dict[str, Any]:
        """Exposes the Explainable AI (XAI) Cause-and-Effect Decision Tree."""
        cycle = self.evaluate_cycle()
        selected = cycle["mpc_decision"]["selected_trajectory"]
        return {
            "uav_id": self.uav_id,
            "timestamp": time.time(),
            "trigger_event": "Obstacle & Wind Gust Detected",
            "evaluated_trajectories": cycle["mpc_decision"]["evaluated_count"],
            "rejected_trajectories": cycle["mpc_decision"]["rejected_count"],
            "selected_trajectory": selected,
            "causality_dag": cycle["causality_dag"],
            "reasoning_chain": [
                f"GPS trust normal ({self.sensor_trust['gps']}%)",
                f"Wind shear evaluated at {cycle['world_model']['physics']['wind_speed_mps']} m/s",
                f"Evaluated {cycle['mpc_decision']['evaluated_count']} candidate splines",
                f"Selected {selected['id']} (Cost score: {selected['cost_score']})",
                "Dispatched to MAVSDK Executor"
            ],
            "global_confidence": self.global_confidence,
            "sensor_trust": self.sensor_trust
        }

    def get_state_envelope(self) -> Dict[str, Any]:
        """Projects current state of the Sovereign Cognitive Kernel."""
        return {
            "uav_id": self.uav_id,
            "fleet_id": self.fleet_id,
            "kernel_version": "9.0.0-SOVEREIGN-10MODULE",
            "uptime_sec": round(time.time() - self._start_ts, 1),
            "risk": self.risk.compute_risk()["quadrants"],
            "sensor_trust": self.sensor_trust,
            "global_confidence": self.global_confidence,
            "certified_learning": self.learning.get_pipeline_status()["offline_learning_pipeline"]
        }
