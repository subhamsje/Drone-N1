import pytest
from backend.intelligence.swarm_consensus import SwarmConsensusEngine

def test_raft_leader_election():
    engine = SwarmConsensusEngine()
    engine.register_node("UAV-01", battery_pct=72.0, lat=30.26, lon=-97.74)
    engine.register_node("UAV-02", battery_pct=96.0, lat=30.27, lon=-97.73)
    engine.register_node("UAV-03", battery_pct=84.0, lat=30.25, lon=-97.75)

    leader = engine.elect_leader()
    # UAV-02 has highest battery (96%) -> must be elected leader
    assert leader == "UAV-02"
    assert engine.nodes["UAV-02"].role == "LEADER"
    assert engine.nodes["UAV-01"].role == "FOLLOWER"

def test_auction_task_allocation():
    engine = SwarmConsensusEngine()
    engine.register_node("UAV-01", battery_pct=95.0, lat=30.26, lon=-97.74)
    engine.register_node("UAV-02", battery_pct=40.0, lat=30.40, lon=-97.90)

    # Auction corridor close to UAV-01
    res = engine.allocate_task_auction("GRID_SURVEY_ALPHA", target_lat=30.261, target_lon=-97.741)
    assert res["assigned_uav"] == "UAV-01"
    assert "winning_bid_cost" in res
