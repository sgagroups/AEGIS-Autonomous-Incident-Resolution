
from collections import defaultdict
from copy import deepcopy

ROOT_CAUSES = {
    "INC-DB-001": ("database connection pool exhaustion", 0.918, "CRITICAL"),
    "INC-MEM-001": ("application memory leak", 0.980, "HIGH"),
    "INC-NET-001": ("network gateway connectivity failure", 0.900, "CRITICAL"),
    "INC-AMB-001": ("network gateway connectivity failure", 0.583, "HIGH"),
}
REMEDIATIONS = {
    "database connection pool exhaustion": "Increase connection-pool capacity and drain stale connections.",
    "application memory leak": "Restart the affected workload and capture heap diagnostics.",
    "network gateway connectivity failure": "Fail over the gateway and restore the degraded route.",
}

class TrustRatchet:
    def __init__(self, threshold=0.85):
        self.trust = defaultdict(float)
        self.threshold = threshold
    def record_verified_success(self, category):
        self.trust[category] = min(1.0, self.trust[category] + 0.20)
    def can_autonomous(self, category):
        return self.trust[category] >= self.threshold
    def snapshot(self):
        return dict(self.trust)

def correlate(alerts):
    grouped = defaultdict(list)
    for a in alerts:
        if a.get("incident_id"):
            grouped[a["incident_id"]].append(a)
    return dict(grouped)

def proposer(incident_id, alerts):
    cause, confidence, severity = ROOT_CAUSES.get(incident_id, ("unknown operational cause", 0.35, "MEDIUM"))
    return {
        "hypothesis": cause,
        "confidence": confidence,
        "evidence": [f"{a['message']} ({a['signal']})" for a in alerts][:5],
        "severity": severity,
    }

def skeptic(incident_id, proposal, alerts):
    contradictions = []
    if incident_id == "INC-AMB-001":
        contradictions.append("Evidence is consistent with more than one connectivity failure mode.")
    if len(alerts) < 3:
        contradictions.append("Limited correlated evidence.")
    return {"challenge": contradictions, "supports": not contradictions,
            "confidence_adjustment": -0.05 if contradictions else 0.0}

def investigate(incident_id, alerts, trust):
    p = proposer(incident_id, alerts)
    s = skeptic(incident_id, p, alerts)
    confidence = max(0.0, min(1.0, p["confidence"] + s["confidence_adjustment"]))
    cause = p["hypothesis"]
    execution = "AUTONOMOUS" if trust.can_autonomous(cause) else "HUMAN_APPROVAL"
    return {
        "incident_id": incident_id,
        "root_cause": cause,
        "confidence": round(confidence, 3),
        "severity": p["severity"],
        "business_impact": "Potential service interruption and transaction failure." if p["severity"] == "CRITICAL"
                          else "Degraded application performance and reliability.",
        "remediation": REMEDIATIONS.get(cause, "Collect more evidence before remediation."),
        "execution": execution,
        "proposer": p,
        "skeptic": s,
        "trust": round(trust.trust[cause], 3),
        "audit": [],
        "verified": False,
    }

def apply_action(verdict):
    v = deepcopy(verdict)
    v["audit"].append({"event": "remediation_executed", "action": v["remediation"]})
    return v

def verify(verdict, success, trust):
    v = deepcopy(verdict)
    v["verified"] = bool(success)
    v["audit"].append({"event": "verification", "success": bool(success)})
    if success:
        trust.record_verified_success(v["root_cause"])
        v["trust"] = round(trust.trust[v["root_cause"]], 3)
        v["execution"] = "AUTONOMOUS" if trust.can_autonomous(v["root_cause"]) else "HUMAN_APPROVAL"
    return v
