"""
Cognitive OS Kernel v8 — fully operational autonomous machine cognition infrastructure.
Flight-hour intelligence, hardware cognition, certifiable operational autonomy, planetary airspace.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config.settings import CONFIG, SystemConfig
from engines.sensor_trust import SensorTrustEngine
from engines.survival import AutonomousSurvivalEngine
from engines.autonomous_cognition import AutonomousCognitionEngine
from engines.vision_autonomy import VisualAutonomyEngine
from engines.route_governance import RouteGovernanceEngine
from engines.fleet_learning import FleetLearningEngine
from engines.gps_denied_nav import GPSDeniedNavigator
from engines.emergency_landing import EmergencyLandingIntelligence
from engines.cyber_response import AutonomousCyberResponseEngine
from engines.autonomy_confidence import AutonomyConfidenceEngine
from engines.swarm_cognition import SwarmCognitionEngine
from engines.twin_physics_hf import HighFidelityTwinPhysics
from engines.adaptive_control import AdaptiveFlightController
from backend.inference.gateway import InferenceGateway
from backend.perception.graph import PerceptionGraph
from backend.execution.mavsdk_executor import MAVSDKExecutor, VehicleMode
from backend.execution.px4_bridge import PX4Bridge
from backend.telemetry_lake.ingest import TelemetryLakehouse
from altaria_os.autonomy_modes import AutonomyModeController, AutonomyMode
from altaria_os.safety.runtime import SafetyCriticalRuntime, SafetyState
from altaria_os.safety.probabilistic import ProbabilisticSafetyEngine
from altaria_os.safety.envelope import DeterministicSafetyController
from altaria_os.runtime.scheduler import RealTimeScheduler, TaskPriority
from altaria_os.modes.industry import IndustryModeController, IndustryMode
from engines.fleet_meta_learning import FleetMetaLearningEngine
from engines.control_intelligence import ControlIntelligenceEngine
from engines.cyber_fleet_intel import DistributedCyberIntelligence
from backend.perception.robustness import PerceptionRobustnessLayer
from backend.operations.intelligence import OperationalIntelligencePlatform
from backend.federation_global.federation import GlobalFederationController
from backend.federation_global.cognition_fabric import GlobalCognitionFabric
from backend.operations.flight_orchestrator import FlightOperationsOrchestrator
from backend.operations.economics import OperationalEconomicsEngine
from backend.perception.multimodal_fusion import MultimodalPerceptionFusion
from backend.telemetry_lake.knowledge_graph import OperationalKnowledgeGraph
from engines.online_learning import OnlineAdaptiveLearningEngine
from engines.airspace_cognition import AirspaceCognitionEngine
from engines.distributed_swarm import DistributedSwarmCognition
from engines.cyber_warfare import CyberWarfareResilienceEngine
from engines.evolution_engine import AutonomousEvolutionEngine
from altaria_os.cognition.explainability import AutonomyExplainabilityEngine
from altaria_os.certification.compliance import CertificationComplianceEngine
from altaria_os.modes.tactical import TacticalModeOrchestrator
from engines.embodied_cognition import EmbodiedCognitionEngine
from engines.predictive_world_model import PredictiveWorldModelEngine
from backend.perception.adversarial_resilience import AdversarialPerceptionResilience
from altaria_os.cognition.meta_cognition import MetaCognitionEngine
from altaria_os.cognition.mission_replay import MissionCognitionReplayEngine
from altaria_os.certification.formal import CertifiableAutonomyEngine
from altaria_os.runtime.operational_executor import OperationalExecutionOrchestrator
from backend.telemetry_lake.planetary import PlanetaryTelemetryLakehouse
from backend.federation_global.planetary_federation import PlanetaryAutonomousFederation
from engines.embodied_learning import EmbodiedLearningEngine
from engines.foundation_world_model import FoundationWorldModelEngine
from engines.adversarial_operations import AdversarialOperationalResilience
from backend.operations.autonomous_ops import AutonomousOperationsOrchestrator
from altaria_os.runtime.mixed_criticality import MixedCriticalityRuntime, CriticalityDomain
from altaria_os.cognition.operational_trust import OperationalTrustEngine
from engines.embodied_evolution import ContinuousEmbodiedEvolutionEngine
from engines.world_cognition import WorldCognitionEngine
from engines.collective_intelligence import DecentralizedCollectiveIntelligence
from engines.adaptive_adversarial_autonomy import AdaptiveAdversarialAutonomyEngine
from altaria_os.certification.evidence_dag import MissionEvidenceDAG
from altaria_os.cognition.strategic_evolution import StrategicEvolutionEngine
from backend.federation_global.planetary_governance import PlanetaryGovernanceEngine
from backend.telemetry_lake.flight_hour_intelligence import FlightHourIntelligenceEngine
from engines.hardware_cognition import HardwareCognitionEngine
from backend.federation_global.airspace_coordination import PlanetaryAirspaceCoordination
from backend.operations.operational_economics import OperationalEconomicsPlatform
from altaria_os.certification.operational_autonomy import CertifiableOperationalAutonomyRuntime

logger = logging.getLogger("os.kernel")


class CognitiveOSKernel:
    """Full autonomous aerial cognition kernel — production deployment."""

    def __init__(
        self,
        uav_id: str = "Altaria-Alpha",
        fleet_id: str = "swarm-alpha-1",
        config: SystemConfig = CONFIG,
        edge_mode: bool = True,
        px4_mode: Optional[str] = None,
    ):
        import os
        if px4_mode is None:
            px4_mode = os.getenv("PX4_MODE", "sitl")
            
        self.uav_id = uav_id
        self.fleet_id = fleet_id
        self.config = config

        self.sensor_trust = SensorTrustEngine(config)
        self.inference = InferenceGateway(uav_id, edge_mode=edge_mode)
        self.survival = AutonomousSurvivalEngine()
        self.cognition = AutonomousCognitionEngine()
        self.vision = VisualAutonomyEngine()
        self.routing = RouteGovernanceEngine()
        self.fleet_learning = FleetLearningEngine(fleet_id)
        self.gps_denied = GPSDeniedNavigator()
        self.landing_intel = EmergencyLandingIntelligence()
        self.cyber_response = AutonomousCyberResponseEngine()
        self.confidence = AutonomyConfidenceEngine()
        self.twin_physics = HighFidelityTwinPhysics()
        self.adaptive_control = AdaptiveFlightController()
        self.perception = PerceptionGraph(device="cuda" if edge_mode else "cpu")
        self.safety = SafetyCriticalRuntime()
        self.lake = TelemetryLakehouse(fleet_id)
        self.swarm = SwarmCognitionEngine(fleet_id, [uav_id, "UAV-101", "UAV-102", "UAV-103"])
        self.px4 = PX4Bridge(uav_id, px4_mode)
        self.autonomy = AutonomyModeController(AutonomyMode.AUTONOMOUS)
        self.prob_safety = ProbabilisticSafetyEngine()
        self.safety_envelope = DeterministicSafetyController()
        self.rt_scheduler = RealTimeScheduler()
        self.meta_learning = FleetMetaLearningEngine(fleet_id)
        self.control_intel = ControlIntelligenceEngine()
        self.cyber_fleet = DistributedCyberIntelligence(fleet_id)
        self.perception_robust = PerceptionRobustnessLayer()
        self.operations = OperationalIntelligencePlatform(fleet_id)
        self.federation = GlobalFederationController()
        self.cognition_fabric = GlobalCognitionFabric()
        self.industry = IndustryModeController(IndustryMode.STANDARD)
        self.tactical = TacticalModeOrchestrator()
        self.flight_ops = FlightOperationsOrchestrator(uav_id, fleet_id)
        self.online_learning = OnlineAdaptiveLearningEngine()
        self.multimodal = MultimodalPerceptionFusion()
        self.airspace = AirspaceCognitionEngine()
        self.dist_swarm = DistributedSwarmCognition(fleet_id, [uav_id, "UAV-101", "UAV-102", "UAV-103"])
        self.cyber_warfare = CyberWarfareResilienceEngine()
        self.explainer_os = AutonomyExplainabilityEngine()
        self.certification = CertificationComplianceEngine()
        self.knowledge_graph = OperationalKnowledgeGraph(fleet_id)
        self.evolution = AutonomousEvolutionEngine(fleet_id)
        self.economics = OperationalEconomicsEngine(fleet_size=4)
        self.embodied = EmbodiedCognitionEngine()
        self.world_model = PredictiveWorldModelEngine()
        self.adversarial_perception = AdversarialPerceptionResilience()
        self.meta_cognition = MetaCognitionEngine(fleet_id)
        self.formal_cert = CertifiableAutonomyEngine()
        self.rt_executor = OperationalExecutionOrchestrator(self.rt_scheduler)
        self.planetary_lake = PlanetaryTelemetryLakehouse(shard_id=f"{fleet_id}-shard")
        self.planetary_federation = PlanetaryAutonomousFederation()
        self.mission_replay = MissionCognitionReplayEngine()
        self.embodied_learning = EmbodiedLearningEngine()
        self.foundation_world = FoundationWorldModelEngine()
        self.adversarial_ops = AdversarialOperationalResilience(fleet_id)
        self.autonomous_ops = AutonomousOperationsOrchestrator(fleet_id, fleet_size=4)
        self.mixed_criticality = MixedCriticalityRuntime()
        self.operational_trust = OperationalTrustEngine()
        self.embodied_evolution = ContinuousEmbodiedEvolutionEngine()
        self.world_cognition = WorldCognitionEngine()
        self.collective_intel = DecentralizedCollectiveIntelligence(fleet_id)
        self.adaptive_adversarial = AdaptiveAdversarialAutonomyEngine()
        self.evidence_dag = MissionEvidenceDAG()
        self.strategic_evolution = StrategicEvolutionEngine(fleet_id)
        self.planetary_governance = PlanetaryGovernanceEngine()
        self.flight_hour_intel = FlightHourIntelligenceEngine(uav_id)
        self.hardware_cognition = HardwareCognitionEngine()
        self.airspace_coordination = PlanetaryAirspaceCoordination()
        self.ops_economics = OperationalEconomicsPlatform()
        self.operational_cert = CertifiableOperationalAutonomyRuntime()
        self._tactical_mode: Optional[str] = None

        self._feature_vector: List[float] = []
        self._mission_intent: Optional[str] = None
        self._pending_execution: Optional[Dict] = None

    def set_industry_mode(self, mode: str):
        self._tactical_mode = mode if mode in ("DEFENSE", "DISASTER_RESPONSE") else None
        try:
            self.industry.set_mode(IndustryMode(mode))
        except ValueError:
            pass
        self.online_learning.set_mission_category(mode.lower().replace("_", ""))

    def set_mission_intent(self, intent: str):
        self._mission_intent = intent
        constraints = self.routing.parse_semantic_intent(intent)
        if constraints.get("avoid_populated"):
            self.routing.set_geofence({"min_x": -500, "max_x": 500, "min_y": -500, "max_y": 500})

    async def initialize_execution(self):
        await self.px4.start()

    async def process(self, snapshot: Dict[str, Any], feature_vector: Optional[List[float]] = None) -> Dict[str, Any]:
        self.safety.heartbeat()
        if feature_vector:
            self._feature_vector = feature_vector

        import time as _time
        _critical_t0 = _time.monotonic()
        self.mixed_criticality.begin_cycle()

        ekf = snapshot.get("ekf", {})
        physics = snapshot.get("physics", {})
        cyber = snapshot.get("cybersecurity", {}) or {}
        nav = snapshot.get("navigation", {}) or {}

        # RT: perception (non-critical path scheduled)
        await self.perception.process_frame(None)
        snapshot = self.perception.fuse_into_snapshot(snapshot)

        # Perception robustness layer
        perc_health = self.perception_robust.update(
            float(nav.get("weather_hazard", 0)),
            float(snapshot.get("perception", {}).get("obstacle_density", 0.2)),
        )
        snapshot["perception_health"] = perc_health.to_dict()

        # Multi-modal fusion
        mm = self.multimodal.fuse(snapshot.get("perception"), perc_health.to_dict())
        snapshot["multimodal_perception"] = mm.to_dict()
        if mm.survival_mode != "nominal":
            snapshot.setdefault("vision", {})["gps_denied_mode"] = True

        # Adversarial perception resilience
        adv_perc = self.adversarial_perception.assess(
            perc_health.to_dict(),
            mm.to_dict(),
            environment={"weather_hazard": float((snapshot.get("navigation") or {}).get("weather_hazard", 0))},
        )
        snapshot["adversarial_perception"] = adv_perc.to_dict()
        if adv_perc.thermal_nav_assist:
            snapshot.setdefault("vision", {})["thermal_nav_active"] = True

        # Sensor trust
        trust = self.sensor_trust.evaluate(
            ekf_confidence=float(ekf.get("confidence", 0.9)),
            innovation_mag=float(ekf.get("innovation_mag", 0)),
            imu=physics.get("imu", [0, 0, 0]),
            comm_delay=0.05,
            is_gps_spoofed=bool(cyber.get("is_spoofed", False)),
            vision_confidence=float(snapshot.get("perception", {}).get("landable_regions", 1) > 0 and 0.91 or 0.5),
        )
        snapshot["sensor_trust"] = trust.to_dict()

        # GPS-denied navigation
        nav_state = self.gps_denied.update(
            trust.gps_confidence,
            physics.get("imu", [0, 0, 0]),
            dt=0.2,
            vision_confidence=trust.vision_confidence,
        )
        snapshot["navigation_state"] = nav_state.to_dict()
        if nav_state.mode != "gps":
            trust = self.sensor_trust.evaluate(
                ekf_confidence=float(ekf.get("confidence", 0.9)),
                innovation_mag=float(ekf.get("innovation_mag", 0)),
                imu=physics.get("imu", [0, 0, 0]),
                comm_delay=0.05,
                is_gps_spoofed=True,
                vision_confidence=nav_state.localization_confidence,
            )
            snapshot["sensor_trust"] = trust.to_dict()

        # Vision
        vision = self.vision.update(trust.to_dict(), physics, nav)
        snapshot["vision"] = vision.to_dict()

        # Inference
        fv = self._feature_vector or self._default_features(snapshot)
        failure_pred = await self.inference.infer_failure(fv, snapshot, trust.to_dict())
        snapshot["inference"] = failure_pred.to_dict()

        # High-fidelity twin physics
        twin = self.twin_physics.step(physics, physics.get("motor_thrusts", []), float(snapshot.get("risk", {}).get("value", 0)))
        snapshot["twin_physics"] = twin.to_dict()

        # Flight-hour operational intelligence (early harvest for hardware + economics)
        snapshot["flight_hour_intelligence"] = self.flight_hour_intel.harvest_cycle(snapshot)
        snapshot["hardware_cognition"] = self.hardware_cognition.evaluate(
            snapshot, snapshot["flight_hour_intelligence"],
        ).to_dict()
        if float(snapshot["hardware_cognition"].get("hardware_survivability_factor", 1)) < 0.5:
            snapshot.setdefault("risk", {})["value"] = min(
                1.0, float(snapshot.get("risk", {}).get("value", 0)) + 0.1
            )

        # Route governance
        route = self.routing.evaluate(snapshot, self._mission_intent, position=(0, 0))
        if self.gps_denied.should_reroute():
            route.reroute_required = True
        snapshot["route_governance"] = route.to_dict()

        # Airspace cognition
        pos = tuple(nav_state.position_ned) if nav_state else (0, 0, float(physics.get("altitude", 10)))
        urban = self.industry.profile.mode == IndustryMode.LOGISTICS if hasattr(self.industry, "profile") else False
        air = self.airspace.evaluate(pos, (0, 0, 0), route.to_dict(), urban=urban)
        snapshot["airspace"] = air.to_dict()
        snapshot["airspace_traffic"] = self.airspace.traffic_intelligence(urban=urban)
        snapshot["airspace_conflict_prediction"] = self.airspace.predict_conflict(30.0)
        snapshot["airspace_federation"] = self.airspace.federation_export()
        if urban and not self.airspace._corridors:
            self.airspace.generate_corridor("uam-urban-1", (0, 0), (200, 0), altitude_m=30.0)

        # Fleet + swarm
        fleet_intel = self.fleet_learning.ingest_local_observation(self.uav_id, snapshot)
        snapshot["fleet_intelligence"] = fleet_intel.to_dict()
        self.swarm.update_member(self.uav_id, snapshot)
        snapshot["swarm"] = self.swarm.compute_consensus().to_dict()
        self.dist_swarm.ingest_member(self.uav_id, snapshot)
        collective = self.dist_swarm.collective_reason()
        snapshot["distributed_swarm"] = collective.to_dict()
        snapshot["shared_perception_map"] = self.dist_swarm.get_shared_map()
        snapshot["collective_swarm"] = {
            "consensus": collective.to_dict(),
            "collective_simulation": self.dist_swarm.collective_simulate(),
            "collaborative_world_sim": self.dist_swarm.collaborative_world_simulation(),
            "collective_defend": self.dist_swarm.collective_defend(),
            "mission_optimize": self.dist_swarm.optimize_collective_mission(),
            "emergent_routing": self.dist_swarm.emergent_route_adaptation(),
            "cognition_graph": self.dist_swarm.distributed_consensus_graph(),
        }
        fleet_boost = self.fleet_learning.get_fleet_risk_boost()
        if fleet_boost > 0 and "risk" in snapshot:
            snapshot["risk"]["value"] = min(1.0, float(snapshot["risk"]["value"]) + fleet_boost)

        # Cyber autonomous response
        cyber_actions = self.cyber_response.respond(cyber, trust.to_dict())
        snapshot["cyber_response"] = [a.to_dict() for a in cyber_actions]
        for a in cyber_actions:
            if a.nav_mode_switch and "navigation_state" in snapshot:
                snapshot["navigation_state"]["mode"] = a.nav_mode_switch

        # Emergency landing zone
        best_lz = self.landing_intel.select_best(nav, snapshot.get("perception"), trust.gps_confidence)
        snapshot["landing_zone"] = best_lz.to_dict()
        if nav:
            nav = dict(nav)
            nav["landing_x"] = best_lz.position[0]
            nav["landing_y"] = best_lz.position[1]
            nav["landing_safety"] = best_lz.total_score
            snapshot["navigation"] = nav

        # Survival
        survival_plan = self.survival.plan(snapshot, failure_pred.to_dict(), trust.to_dict())
        snapshot["survival"] = survival_plan.to_dict()

        # Cognition
        cognition = self.cognition.reason(snapshot, trust.to_dict(), failure_pred.to_dict(), survival_plan.to_dict())
        snapshot["cognition"] = cognition.to_dict()

        # Confidence engine
        conf = self.confidence.evaluate(snapshot, trust.to_dict(), snapshot.get("perception"))
        snapshot["confidence"] = conf.to_dict()
        if conf.operator_required:
            snapshot["operator_required"] = True

        # Adaptive control + control intelligence
        base_u = physics.get("motor_thrusts", [5.42] * 4)
        ctrl = self.adaptive_control.compute(base_u, twin.to_dict(), conf.to_dict(), survival_plan.to_dict())
        snapshot["adaptive_control"] = ctrl.to_dict()
        ctrl_intel = self.control_intel.compute(snapshot, ctrl.to_dict(), conf.to_dict(), twin.to_dict())
        snapshot["control_intelligence"] = ctrl_intel.to_dict()

        # Predictive + foundation world models — simulate BEFORE safety commit
        _t_wm = _time.monotonic()
        world_forecast = self.world_model.simulate(
            snapshot, snapshot.get("airspace"), collective_risk=collective.collective_risk,
        )
        snapshot["world_model"] = world_forecast.to_dict()
        foundation = self.foundation_world.simulate(
            snapshot, world_forecast.to_dict(), snapshot.get("collective_swarm"),
        )
        snapshot["foundation_world_model"] = foundation.to_dict()
        uncertainty = self.world_cognition.propagate_uncertainty(
            snapshot, foundation.to_dict(), world_forecast.to_dict(),
        )
        snapshot["world_cognition"] = {
            "uncertainty": uncertainty.to_dict(),
            "future_graph": self.world_cognition.build_future_cognition_graph(
                foundation.to_dict(), uncertainty
            ),
        }
        self.mixed_criticality.record_domain(
            CriticalityDomain.COGNITION, (_time.monotonic() - _t_wm) * 1000
        )
        preempt = foundation.preemptive_recommendation or world_forecast.recommended_preemptive_action
        if preempt and snapshot.get("decision"):
            snapshot["decision"]["world_model_preempt"] = preempt

        # Probabilistic safety assessment
        prob_safety = self.prob_safety.assess(
            snapshot, trust.to_dict(), conf.to_dict(), survival_plan.to_dict(), snapshot.get("landing_zone"),
        )
        snapshot["probabilistic_safety"] = prob_safety.to_dict()

        # Deterministic safety envelope
        envelope_status = self.safety_envelope.evaluate_snapshot(snapshot)
        snapshot["safety_envelope"] = envelope_status

        # Fleet meta-learning + cyber fleet intel
        self.meta_learning.ingest_fleet_cycle(self.uav_id, snapshot)
        snapshot["meta_learning"] = self.meta_learning.get_fleet_intelligence_export()
        fleet_alerts = self.cyber_fleet.process_local(self.uav_id, snapshot.get("cyber_response", []))
        snapshot["cyber_fleet"] = self.cyber_fleet.get_fleet_containment_directive()

        # Cyber warfare resilience
        cw = self.cyber_warfare.assess_and_contain(snapshot)
        cw_state = self.cyber_warfare.get_resilience_state()
        cw_state["mission_continuity_under_attack"] = cw_state.get("mission_continuity", 1.0) > 0.55
        snapshot["cyber_warfare"] = {
            "attacks": [{"type": a.attack_type, "conf": a.confidence, "sev": a.severity} for a in cw],
            **cw_state,
        }
        adv_ops = self.adversarial_ops.assess(snapshot, snapshot["cyber_warfare"], snapshot.get("cyber_fleet"))
        snapshot["adversarial_operations"] = adv_ops.to_dict()
        snapshot["adaptive_adversarial"] = self.adaptive_adversarial.assess(
            snapshot, snapshot["adversarial_operations"], snapshot["cyber_warfare"],
        ).to_dict()
        self.dist_swarm.collective_simulate(world_forecast.to_dict())
        snapshot["collective_swarm"]["collaborative_world_sim"] = self.dist_swarm.collaborative_world_simulation(
            foundation.to_dict()
        )

        # Online adaptive learning
        policy = self.online_learning.update_from_cycle(snapshot)
        snapshot["adaptive_policy"] = policy.to_dict()

        # Industry / tactical modes
        if self._tactical_mode:
            snapshot = self.tactical.apply(snapshot, self._tactical_mode)
        else:
            snapshot = self.industry.apply_to_snapshot(snapshot)

        # Embodied cognition + RL learning — after policy + industry context
        embodied = self.embodied.adapt(
            snapshot,
            snapshot.get("adaptive_policy"),
            snapshot.get("industry_profile"),
        )
        snapshot["embodied_cognition"] = embodied.to_dict()
        embodied_rl = self.embodied_learning.update(snapshot, snapshot.get("adaptive_policy"))
        snapshot["embodied_learning"] = embodied_rl.to_dict()
        snapshot["embodied_evolution"] = self.embodied_evolution.evolve_cycle(
            snapshot, embodied_rl.to_dict(), snapshot.get("collective_swarm"),
        ).to_dict()
        if embodied.control_aggression_scale < 1.0 and "control_intelligence" in snapshot:
            snapshot["control_intelligence"]["aggression_scale"] = embodied.control_aggression_scale
        snapshot["control_intelligence"]["hover_gain"] = embodied_rl.hover_stability_gain
        snapshot["control_intelligence"]["turbulence_damping"] = embodied_rl.turbulence_damping

        snapshot = self.federation.route_snapshot(snapshot, self.uav_id)
        self.cognition_fabric.sync_regional_learning(self.federation.home_zone, snapshot.get("meta_learning", {}))

        # Flight operations
        snapshot["flight_operations"] = self.flight_ops.ingest_cycle(snapshot)

        # Operational + economics intelligence
        self.operations.record_cycle(snapshot)
        self.economics.record_cycle(snapshot)
        snapshot["operations"] = self.operations.compute_metrics().to_dict()
        snapshot["enterprise_roi"] = self.economics.compute_roi().to_dict()

        # Knowledge graph + evolution (feeds meta-cognition)
        self.knowledge_graph.ingest(snapshot, self.uav_id)
        snapshot["knowledge_graph"] = self.knowledge_graph.get_stats()
        snapshot["evolution"] = self.evolution.evolve_generation([snapshot])

        # Meta-cognition — introspect, evolve doctrine, strategic fleet evolution
        meta = self.meta_cognition.introspect(
            snapshot, world_forecast.to_dict(), snapshot.get("evolution"),
        )
        snapshot = self.meta_cognition.apply_doctrine_to_snapshot(snapshot, meta)
        snapshot["strategic_evolution"] = self.meta_cognition.strategic_evolution(
            snapshot.get("evolution", {}), snapshot.get("embodied_learning"),
        )
        self.collective_intel.ingest_collective_snapshot(
            snapshot.get("collective_swarm", {}), snapshot.get("foundation_world_model", {}),
        )
        emergent = self.collective_intel.emergent_reason(snapshot.get("collective_swarm", {}))
        snapshot["collective_intelligence"] = {
            "emergent": emergent.to_dict(),
            "strategic": self.collective_intel.distributed_strategic_adaptation(
                snapshot.get("meta_cognition", {}),
            ),
        }
        doctrine = self.strategic_evolution.evolve(
            snapshot.get("meta_cognition", {}),
            snapshot.get("evolution", {}),
            emergent.to_dict(),
            snapshot.get("adaptive_adversarial", {}),
        )
        snapshot["strategic_doctrine"] = doctrine.to_dict()

        # Explainability + human-AI mission replay + operational trust
        explanation = self.explainer_os.explain_cycle(snapshot)
        snapshot["explanation"] = explanation.to_dict()
        snapshot["mission_replay"] = self.mission_replay.record_cycle(snapshot, snapshot["explanation"]).to_dict()
        snapshot["operational_trust"] = self.operational_trust.evaluate(
            snapshot, snapshot["explanation"], snapshot.get("mission_replay"),
        ).to_dict()

        # Certification + formal verifiable autonomy + evidence graph
        snapshot["compliance"] = self.certification.evaluate_cycle(snapshot)
        snapshot["formal_certification"] = self.formal_cert.verify_cycle(snapshot)
        snapshot["certification_evidence_graph"] = self.formal_cert.build_evidence_graph(snapshot)
        snapshot["mission_evidence_dag"] = self.evidence_dag.build_from_cycle(snapshot)

        # Autonomous operations AI — fleet allocation
        self.autonomous_ops.register_uav_cycle(self.uav_id, snapshot)
        fleet_ops = self.autonomous_ops.allocate_fleet(snapshot.get("airspace"))
        fleet_ops["airspace_throughput"] = self.autonomous_ops.airspace_throughput(snapshot.get("airspace", {}))
        snapshot["autonomous_operations"] = fleet_ops
        snapshot["fleet_economics"] = self.autonomous_ops.compute_operational_economics(snapshot.get("enterprise_roi"))
        snapshot["operational_economics"] = self.ops_economics.analyze_cycle(
            snapshot,
            snapshot.get("enterprise_roi"),
            snapshot.get("flight_hour_intelligence"),
            snapshot.get("hardware_cognition"),
        ).to_dict()
        snapshot["cognition_fabric"] = self.cognition_fabric.get_fabric_status()

        # Autonomy overrides — gated by deterministic envelope
        snapshot["autonomy_mode"] = self.autonomy.mode.value
        current_action = snapshot.get("decision", {}).get("action", "NONE")

        if self.autonomy.policy.survival_override and self.survival.should_override_decision(survival_plan, current_action):
            override_action = self.survival.map_to_decision_action(survival_plan.strategy)
            env_ok, env_reason = self.safety_envelope.authorize_command(override_action, snapshot)
            safety_ok = not self.safety.veto_command(
                override_action, float(snapshot.get("risk", {}).get("value", 0)), conf.global_uncertainty
            )
            if env_ok and safety_ok:
                snapshot["decision"]["action"] = override_action
                snapshot["decision"]["os_override"] = True
                snapshot["decision"]["override_reason"] = f"survival:{survival_plan.urgency}"
                self._pending_execution = {"strategy": survival_plan.strategy, "landing": snapshot.get("landing_zone")}
                self.autonomy.escalate_to_survival()
                self.safety.transition(SafetyState.RECOVERY)
            else:
                snapshot["decision"]["vetoed"] = True
                snapshot["decision"]["veto_reason"] = env_reason if not env_ok else "safety_veto"

        if failure_pred.crash_probability > 0.8:
            self.autonomy.escalate_to_survival()
            self.safety.transition(SafetyState.EMERGENCY)

        if prob_safety.recommendation in ("ABORT_MISSION_ESCALATE", "RECOVERY_REQUIRED"):
            snapshot["probabilistic_escalation"] = prob_safety.recommendation

        # Mixed-criticality + RT execution status
        critical_ms = (_time.monotonic() - _critical_t0) * 1000
        self.mixed_criticality.record_domain(CriticalityDomain.SURVIVAL, critical_ms * 0.4)
        emergency = snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH")
        if emergency:
            self.mixed_criticality.escalate_emergency(snapshot.get("survival", {}).get("strategy", "unknown"))
        mc_status = self.mixed_criticality.finalize_cycle(emergency=emergency)
        snapshot["mixed_criticality"] = mc_status
        snapshot["rt_execution"] = {
            "critical_path_ms": round(critical_ms, 2),
            "critical_path_met": critical_ms <= self.rt_executor.CRITICAL_BUDGET_MS,
            "defer_persistence": mc_status.get("defer_analytics", False),
            **self.rt_executor.get_execution_status(),
        }

        # Safety audit (low priority — after critical path)
        audit = self.safety.audit_cycle(snapshot)
        snapshot["safety_audit_id"] = audit.record_id
        snapshot["safety"] = self.safety.get_status()
        snapshot["rt_scheduler"] = self.rt_scheduler.get_stats()

        snapshot["operational_certification"] = self.operational_cert.certify_cycle(
            snapshot,
            snapshot.get("mixed_criticality", {}),
            snapshot.get("formal_certification", {}),
            snapshot.get("mission_evidence_dag", {}),
        )

        # Planetary telemetry + federation (deferred band — after survival path)
        region = self.federation.home_zone if hasattr(self.federation, "home_zone") else "us-west"
        self.planetary_lake.ingest_event(snapshot, self.uav_id, region)
        snapshot["planetary_intelligence"] = self.planetary_lake.get_planetary_intelligence()
        self.planetary_federation.propagate_intelligence(region, snapshot.get("meta_learning", {}))
        snapshot["planetary_federation"] = self.planetary_federation.get_planetary_status()
        self.planetary_governance.update_zone(region, snapshot.get("planetary_intelligence", {}))
        snapshot["planetary_governance"] = self.planetary_governance.get_planetary_status()
        self.airspace_coordination.register_region(
            region,
            snapshot.get("airspace_traffic", {}),
            snapshot.get("airspace_federation", {}),
        )
        snapshot["planetary_airspace"] = self.airspace_coordination.coordinate_planetary()

        if not mc_status.get("defer_persistence"):
            self.lake.ingest_cycle(snapshot, self.uav_id)
        snapshot["uav_id"] = self.uav_id
        snapshot["os_version"] = "8.0.0"
        return snapshot

    async def execute_pending_recovery(self) -> Optional[Dict]:
        """RT-priority MAVSDK execution — survival preempts all other work."""
        if not self._pending_execution:
            return None
        pe = self._pending_execution
        self._pending_execution = None
        lz = pe.get("landing", {})
        strategy = pe["strategy"]

        result = await self.px4.execute_survival(
            strategy,
            {"lat": lz.get("position", [0, 0])[0], "lon": lz.get("position", [0, 0])[1], "alt": 0} if lz else None,
        )
        return result.to_dict()

    def _default_features(self, snapshot: Dict) -> List[float]:
        p = snapshot.get("physics", {})
        r = snapshot.get("risk", {})
        return [
            float(p.get("altitude", 0)), float(p.get("battery", 100)), float(p.get("rpm", 0)),
            float(r.get("value", 0)), float(snapshot.get("anomaly", {}).get("score", 0)),
            float(snapshot.get("ekf", {}).get("confidence", 0.9)),
        ] + [0.0] * 8
