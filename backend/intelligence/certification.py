"""Certification infrastructure — audit trails, evidence graphs, mission lineage."""

from typing import Any, Dict, List

from altaria_os.certification.evidence_dag import MissionEvidenceDAG


class CertificationEvidenceBuilder:
    def __init__(self, evidence_dag: MissionEvidenceDAG):
        self._dag = evidence_dag

    def record_mission_lineage(self, mission_id: str, phase: str, detail: Dict[str, Any]) -> Dict[str, Any]:
        node = self._dag.record_event(f"mission_{phase}", {"mission_id": mission_id, **detail})
        return {
            "mission_id": mission_id,
            "phase": phase,
            "evidence_node": node,
            "standards_targets": ["ASTM F38", "FAA Part 107", "EASA SORA"],
        }

    def build_explainability_record(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "replay_id": snapshot.get("explanation", {}).get("replay_id"),
            "decision": snapshot.get("decision", {}).get("action"),
            "survival_strategy": snapshot.get("survival", {}).get("strategy"),
            "why_route_change": snapshot.get("route_governance", {}).get("reroute_reason"),
            "safety_audit_id": snapshot.get("safety_audit_id"),
            "dag": self._dag.build_from_cycle(snapshot),
        }

    def export_audit_package(self, mission_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "missions": mission_records,
            "certification_report": self._dag.export_certifiable_report(),
            "traceability": "requirements→plan→simulate→approve→execute→replay",
            "compliance_mapping": {
                "DO-178C": "DAG maps high-level semantic intent to low-level MAVLink execution.",
                "EASA_SORA": "Survivability logs serve as Specific Operations Risk Assessment artifacts for BVLOS.",
                "FAA_Part_107": "Flight logs and MAVSDK overrides retained for regulatory auditing."
            }
        }
