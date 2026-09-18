
from __future__ import annotations
import json, random
from pathlib import Path
from datetime import datetime, timezone

SCENARIOS = {
    "INC-DB-001": ("orders-db", "database connection pool exhaustion", "CRITICAL"),
    "INC-MEM-001": ("checkout-api", "application memory leak", "HIGH"),
    "INC-NET-001": ("edge-gateway", "network gateway connectivity failure", "CRITICAL"),
    "INC-AMB-001": ("edge-gateway", "network gateway connectivity failure", "HIGH"),
}

TEMPLATES = {
    "INC-DB-001": [
        ("DB connection timeout", "db.pool.active=98%", "CRITICAL"),
        ("DB pool waiters high", "db.pool.waiters=41", "CRITICAL"),
        ("Orders API latency high", "p95=3.8s", "HIGH"),
        ("Checkout transaction failures", "5xx=18%", "CRITICAL"),
        ("Connection acquire timeout", "timeout=4.2s", "CRITICAL"),
    ],
    "INC-MEM-001": [
        ("Heap usage rising", "heap=92%", "HIGH"),
        ("GC pause increase", "gc.pause=840ms", "HIGH"),
        ("Container RSS rising", "rss=7.8GB", "HIGH"),
        ("Checkout latency high", "p95=2.7s", "HIGH"),
        ("OOM risk warning", "oom.score=0.81", "CRITICAL"),
    ],
    "INC-NET-001": [
        ("Gateway packet loss", "loss=38%", "CRITICAL"),
        ("Upstream timeout", "timeout=71%", "CRITICAL"),
        ("Route flap detected", "flaps=14", "HIGH"),
        ("External API unreachable", "reachability=false", "CRITICAL"),
        ("Gateway health degraded", "health=degraded", "CRITICAL"),
    ],
    "INC-AMB-001": [
        ("Connectivity degradation", "loss=11%", "HIGH"),
        ("Gateway timeout", "timeout=19%", "HIGH"),
        ("Route instability", "flaps=4", "MEDIUM"),
        ("Upstream retry burst", "retries=28", "HIGH"),
        ("Gateway health warning", "health=warning", "HIGH"),
    ],
}

NOISE = [
    ("payments-api", "HTTP 429 burst", "transient traffic spike"),
    ("search-api", "Cache miss increase", "cache churn"),
    ("orders-ui", "Slow page render", "client-side latency"),
    ("auth-service", "Login retry burst", "credential retry noise"),
    ("worker-queue", "Queue depth increase", "temporary backlog"),
]

def generate(seed=42):
    random.seed(seed)
    now = datetime.now(timezone.utc).isoformat()
    alerts = []
    n = 1
    for inc_id, rows in TEMPLATES.items():
        service = SCENARIOS[inc_id][0]
        for message, signal, severity in rows:
            alerts.append({
                "alert_id": f"ALT-{n:03d}",
                "incident_id": inc_id,
                "timestamp": now,
                "service": service,
                "message": message,
                "signal": signal,
                "severity": severity,
            })
            n += 1
    for _ in range(40):
        service, message, signal = random.choice(NOISE)
        alerts.append({
            "alert_id": f"ALT-{n:03d}",
            "incident_id": None,
            "timestamp": now,
            "service": service,
            "message": message,
            "signal": signal,
            "severity": random.choice(["LOW", "MEDIUM"]),
        })
        n += 1
    random.shuffle(alerts)
    return alerts

def write(path="data/alerts.json"):
    alerts = generate()
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(alerts, indent=2), encoding="utf-8")
    return alerts

if __name__ == "__main__":
    print(f"Generated {len(write())} alerts")
