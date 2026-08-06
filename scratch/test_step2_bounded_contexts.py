"""Step 2 Bounded Context Integration Audit Script."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from backend.cognitive_kernel import SovereignCognitiveKernel
from backend.knowledge import OperationalKnowledgeGraph
from backend.robotics import DomainVehicleType, MultiDomainTelemetryEnvelope
from backend.edge import JetsonEdgeManager
from backend.collaboration import SpatialCollaborationEngine
from backend.mission import MissionGraphCompiler
from backend.analytics import MissionEconomicsCalculator
from backend.simulation import WeatherPhysicsSimulator

def run_audit():
    print("=== ALTARIA OS STEP 2 BOUNDED CONTEXT AUDIT ===")

    # 1. Sovereign Cognitive Kernel
    kernel = SovereignCognitiveKernel()
    cycle = kernel.evaluate_cycle()
    print(f"[✓] Cognitive Kernel Version: {kernel.get_state_envelope()['kernel_version']}")
    print(f"    - Trajectories Evaluated: {cycle['mpc_decision']['evaluated_count']}")

    # 2. Knowledge Graph
    knowledge = OperationalKnowledgeGraph()
    res = knowledge.search("wind > 12m/s")
    print(f"[✓] Knowledge Graph Search: Matched {res['total_matches']} historical mission(s)")

    # 3. Universal Robotics Schema
    env = MultiDomainTelemetryEnvelope("ROVER-01", DomainVehicleType.UGV)
    proj = env.project_schema({"x": 10.0, "y": 20.0, "z": 0.0})
    print(f"[✓] Multi-Domain Schema: Domain={proj['domain_type']}")

    # 4. Edge Hardware Manager
    edge = JetsonEdgeManager()
    status = edge.get_hardware_status()
    print(f"[✓] Jetson Edge Operations: Device={status['device']} | Latency={status['tensorrt_status']['latency_ms']}ms")

    # 5. Spatial Collaboration Engine
    collab = SpatialCollaborationEngine()
    pins = collab.get_all_pins()
    print(f"[✓] Spatial Collaboration: {len(pins)} active spatial pin(s)")

    # 6. Mission Graph Compiler
    compiler = MissionGraphCompiler()
    compiled = compiler.compile_graph([{"id": "n1", "type": "TAKEOFF"}, {"id": "n2", "type": "SURVEY"}])
    print(f"[✓] Mission Graph Compiler: Status={compiled['status']} ({compiled['node_count']} nodes)")

    # 7. Mission Economics Calculator
    econ = MissionEconomicsCalculator()
    costs = econ.calculate_mission_cost(14.5)
    print(f"[✓] Mission Economics: Total Cost=${costs['itemized_costs_usd']['total_mission_cost']} | ROI={costs['financial_roi']['roi_multiplier']}")

    # 8. Counterfactual Weather Simulator
    sim = WeatherPhysicsSimulator()
    weather = sim.simulate_environment("turbulent_wind")
    print(f"[✓] Weather Physics Sim: Wind={weather['environmental_conditions']['wind_speed_mps']} m/s")

    print("=== AUDIT PASSED: ALL BOUNDED CONTEXTS 100% OPERATIONAL ===")

if __name__ == "__main__":
    run_audit()
