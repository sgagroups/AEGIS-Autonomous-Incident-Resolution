# AEGIS — Autonomous Enterprise Incident Resolution Engine

AEGIS demonstrates:
Detection → Correlation → Investigation → Decision → Remediation → Verification → Audit.

## Stages
- `stages/m1` — alert simulation and incident ground truth
- `stages/m2` — Proposer/Skeptic investigation, verdict, remediation, Trust Ratchet
- `stages/m3` — dashboard UI source
- `stages/m4` — integrated FastAPI backend + final frontend

## Run
```bash
pip install -r requirements.txt
uvicorn stages.m4.backend.main:app --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000`.

## Demo scenarios
`db_pool_exhaustion`, `memory_leak`, `network_gateway_failure`, `ambiguous`

This package intentionally contains source/config/docs only; Colab caches, backups,
screenshots and temporary artifacts are excluded.
