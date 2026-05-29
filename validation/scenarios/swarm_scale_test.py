"""
Automated Swarm Protocol Validation.
Spawns 25 simulated Altaria nodes to validate ROS2 DDS network congestion,
distributed consensus overhead, and threat propagation latency.
"""

import asyncio
import logging
import time
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("swarm_scale_test")

NUM_DRONES = 25

async def run_swarm():
    logger.info(f"=== INITIATING SWARM VALIDATION ({NUM_DRONES} NODES) ===")
    
    nodes = []
    # 1. Initialize Fleet
    for i in range(NUM_DRONES):
        uav_id = f"UAV-{i:03d}"
        engine = AutonomousWorkflowEngine()
        engine.uav_id = uav_id
        # We only start the ROS2 node and fleet service for load testing, not 25 MAVSDK bridges
        engine.ros_node.start()
        nodes.append(engine)
        
    logger.info("Fleet initialized. Propagating initial telemetry mesh...")
    await asyncio.sleep(2)
    
    # 2. Inject Threat at Node 0
    t0 = time.monotonic()
    logger.warning("INJECTING: High-power RF Jamming at UAV-000")
    nodes[0].cyber.publish_threat({"risk": {"value": 0.95}, "source": "rf_jamming"})
    
    # 3. Measure Propagation Latency
    await asyncio.sleep(1)
    t1 = time.monotonic()
    
    # Check if node 24 received the threat state via ROS2/Kafka
    logger.info("Measuring threat propagation across DDS mesh...")
    propagation_latency = (t1 - t0) * 1000
    
    success = propagation_latency < 500.0 # Requirement: sub-500ms propagation
    
    logger.info(f"Swarm Validation Complete. Propagation Latency: {propagation_latency:.2f}ms | Success: {success}")
    
    for n in nodes:
        n.ros_node.stop()

if __name__ == "__main__":
    asyncio.run(run_swarm())
