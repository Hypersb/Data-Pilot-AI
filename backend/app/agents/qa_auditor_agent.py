from typing import Any

import pandas as pd

from app.services.anomaly_engine import detect_anomalies
from app.services.health_score_service import compute_health_score


def run_qa_auditor(df: pd.DataFrame) -> dict[str, Any]:
    health = compute_health_score(df)
    findings: list[str] = [
        f"Overall data health score: {health['overall_score']}/100.",
    ]
    citations = ["health_score"]

    for issue in health["issues"][:5]:
        findings.append(f"[{issue['severity'].upper()}] {issue['description']}")

    try:
        anomalies = detect_anomalies(df)
        if anomalies.get("total_anomalies", 0) > 0:
            findings.append(
                f"{anomalies['total_anomalies']} anomalous rows detected "
                f"(severity {anomalies.get('severity_score', 0):.1f})."
            )
            citations.append("anomaly_detection")
    except (ValueError, Exception):
        pass

    sub = health["sub_scores"]
    if sub["completeness"] < 80:
        findings.append(f"Completeness sub-score is {sub['completeness']}/100 — review missing values.")
    if sub["duplicate_score"] < 90:
        findings.append(f"Duplicate sub-score is {sub['duplicate_score']}/100 — deduplication recommended.")

    return {
        "role": "qa_auditor",
        "findings": findings,
        "confidence": 0.9,
        "citations": citations,
    }
