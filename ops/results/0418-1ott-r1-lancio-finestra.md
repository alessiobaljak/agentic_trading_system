# 0418-1ott-r1-lancio-finestra.req

_eseguito: 2026-10-01 17:54 UTC_

**richiesta:** `replay-gate`
**eseguito:** `systemd-run --no-block --collect --unit=replay-gate --nice=15 --property=IOSchedulingClass=idle --property=WorkingDirectory=/root/agentic_trading_system /root/agentic_trading_system/.venv/bin/python -m scripts.replay_gate --su-file`
**esito:** codice 0 in 0.0s

```

--- stderr ---
Running as unit: replay-gate.service
```
