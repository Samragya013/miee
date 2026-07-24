"""Extended audit trail framework.

Builds complete traceability chains: Finding -> Reasoning -> Evidence ->
Detector -> Metric -> Observation -> Confidence -> Validation -> Assumptions
-> Ground Truth -> Specification -> Certification.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from miie.assurance.models import AuditTrailNode, ExtendedAuditTrail


def _hash_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def build_audit_trail(
    finding_id: str,
    finding_data: Dict[str, Any],
    reasoning_data: Dict[str, Any],
    evidence_data: Dict[str, Any],
    detector_id: str,
    metric: str,
    confidence_data: Dict[str, Any],
    assumption_data: Dict[str, Any],
    ground_truth_data: Dict[str, Any],
) -> ExtendedAuditTrail:
    """Build extended audit trail for a finding.

    Chain: Finding -> Reasoning -> Evidence -> Detector -> Metric ->
           Observation -> Confidence -> Validation -> Assumptions ->
           Ground Truth -> Specification -> Certification.
    """
    nodes: List[AuditTrailNode] = []

    # 1. Finding node (root)
    finding_node_id = _hash_id(f"finding_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=finding_node_id,
            node_type="finding",
            label=f"Finding: {finding_data.get('title', finding_id)}",
            data=finding_data,
            parent_ids=[],
        )
    )

    # 2. Reasoning node
    reasoning_node_id = _hash_id(f"reasoning_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=reasoning_node_id,
            node_type="reasoning",
            label=f"Reasoning: {reasoning_data.get('explanation', 'N/A')}",
            data=reasoning_data,
            parent_ids=[finding_node_id],
        )
    )

    # 3. Evidence node
    evidence_node_id = _hash_id(f"evidence_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=evidence_node_id,
            node_type="evidence",
            label=f"Evidence: {evidence_data.get('summary', 'N/A')}",
            data=evidence_data,
            parent_ids=[reasoning_node_id],
        )
    )

    # 4. Detector node
    detector_node_id = _hash_id(f"detector_{detector_id}_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=detector_node_id,
            node_type="detector",
            label=f"Detector: {detector_id}",
            data={"detector_id": detector_id, "metric": metric},
            parent_ids=[evidence_node_id],
        )
    )

    # 5. Metric node
    metric_node_id = _hash_id(f"metric_{metric}_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=metric_node_id,
            node_type="metric",
            label=f"Metric: {metric}",
            data={"metric": metric},
            parent_ids=[detector_node_id],
        )
    )

    # 6. Observation node
    obs_node_id = _hash_id(f"obs_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=obs_node_id,
            node_type="observation",
            label=f"Observations: {evidence_data.get('observations_total', 0)} total",
            data={
                "total": evidence_data.get("observations_total", 0),
                "valid": evidence_data.get("observations_valid", 0),
            },
            parent_ids=[metric_node_id],
        )
    )

    # 7. Confidence node
    conf_node_id = _hash_id(f"conf_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=conf_node_id,
            node_type="confidence",
            label=f"Confidence: {confidence_data.get('overall', 0):.3f}",
            data=confidence_data,
            parent_ids=[obs_node_id],
        )
    )

    # 8. Validation node
    val_node_id = _hash_id(f"val_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=val_node_id,
            node_type="validation",
            label=f"Validation: assumptions {assumption_data.get('satisfied', 0)}/{assumption_data.get('total', 0)}",
            data=assumption_data,
            parent_ids=[conf_node_id],
        )
    )

    # 9. Assumptions node
    assum_node_id = _hash_id(f"assum_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=assum_node_id,
            node_type="assumptions",
            label=f"Assumptions: {assumption_data.get('status', 'unknown')}",
            data=assumption_data,
            parent_ids=[val_node_id],
        )
    )

    # 10. Ground truth node
    gt_node_id = _hash_id(f"gt_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=gt_node_id,
            node_type="ground_truth",
            label=f"Ground Truth: {ground_truth_data.get('status', 'not_validated')}",
            data=ground_truth_data,
            parent_ids=[assum_node_id],
        )
    )

    # 11. Specification node
    spec_node_id = _hash_id(f"spec_{detector_id}")
    nodes.append(
        AuditTrailNode(
            node_id=spec_node_id,
            node_type="specification",
            label=f"Specification: {detector_id} metric {metric}",
            data={"detector_id": detector_id, "metric": metric},
            parent_ids=[gt_node_id],
        )
    )

    # 12. Certification node
    cert_node_id = _hash_id(f"cert_{finding_id}")
    nodes.append(
        AuditTrailNode(
            node_id=cert_node_id,
            node_type="certification",
            label="Scientific Assurance Certification",
            data={"finding_id": finding_id, "certified": True},
            parent_ids=[spec_node_id],
        )
    )

    return ExtendedAuditTrail(
        trail_id=_hash_id(f"trail_{finding_id}"),
        finding_id=finding_id,
        nodes=nodes,
        root_node_id=finding_node_id,
    )
