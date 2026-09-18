
from datetime import datetime, timezone
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from stages.m2.agent_engine import correlate, investigate, apply_action, verify, TrustRatchet

ROOT = Path(__file__).resolve().parents[2]
alerts = json.loads((ROOT/"data/alerts.json").read_text())
frontend = ROOT/"stages/m4/frontend"
trust = TrustRatchet()
incidents = {}
audit = []

app = FastAPI(title="AEGIS")

def refresh(incident_id):
    groups = correlate(alerts)
    if incident_id not in groups:
        raise HTTPException(404, "Incident not found")
    incidents[incident_id] = investigate(incident_id, groups[incident_id], trust)
    return incidents[incident_id]

@app.get("/")
def home():
    return FileResponse(frontend/"index.html")
app.mount("/assets", StaticFiles(directory=frontend), name="assets")

@app.get("/api/state")
def state():
    groups = correlate(alerts)
    for iid in groups:
        if iid not in incidents: refresh(iid)
    return {"incidents": list(incidents.values()), "alert_count": len(alerts),
            "incident_count": len(groups), "trust": trust.snapshot(), "audit": audit}

@app.get("/api/alerts")
def get_alerts(): return alerts

@app.get("/api/audit")
def get_audit(): return audit

@app.post("/api/simulate/{scenario}")
def simulate(scenario):
    mapping={"db_pool_exhaustion":"INC-DB-001","memory_leak":"INC-MEM-001",
             "network_gateway_failure":"INC-NET-001","ambiguous":"INC-AMB-001"}
    iid=mapping.get(scenario)
    if not iid: raise HTTPException(400,"Unknown scenario")
    v=refresh(iid); v["audit"].append({"event":"simulated","timestamp":datetime.now(timezone.utc).isoformat()})
    return v

@app.post("/api/incidents/{incident_id}/approve")
def approve(incident_id):
    v=incidents.get(incident_id) or refresh(incident_id)
    v["execution"]="APPROVED"; v=apply_action(v); incidents[incident_id]=v
    audit.append({"incident_id":incident_id,"event":"approved"}); return v

@app.post("/api/incidents/{incident_id}/reject")
def reject(incident_id):
    v=incidents.get(incident_id) or refresh(incident_id)
    v["execution"]="REJECTED"; incidents[incident_id]=v
    audit.append({"incident_id":incident_id,"event":"rejected"}); return v

@app.post("/api/incidents/{incident_id}/execute")
def execute(incident_id):
    v=incidents.get(incident_id) or refresh(incident_id)
    v=apply_action(v); incidents[incident_id]=v
    audit.append({"incident_id":incident_id,"event":"executed"}); return v

@app.post("/api/incidents/{incident_id}/verify")
def verify_incident(incident_id):
    v=incidents.get(incident_id) or refresh(incident_id)
    v=verify(v, True, trust); incidents[incident_id]=v
    audit.append({"incident_id":incident_id,"event":"verified"}); return v
