# 0381-voto-t-completo.req

_eseguito: 2026-09-30 15:53 UTC_

**richiesta:** `voto-t-completo`
**eseguito:** `systemd-run --no-block --collect --unit=voto-t-completo --nice=15 --property=IOSchedulingClass=idle --property=WorkingDirectory=/root/agentic_trading_system /root/agentic_trading_system/.venv/bin/python -m scripts.t_validate --su-file --budget 0`
**esito:** codice 0 in 0.0s

```

--- stderr ---
Running as unit: voto-t-completo.service
```
