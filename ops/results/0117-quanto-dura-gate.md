# 0117-quanto-dura-gate.req

_eseguito: 2026-09-20 17:30 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Sun 2026-09-20 18:04:30 UTC 34min Sun 2026-09-20 17:03:14 UTC    26min ago trading-supervisor.timer trading-supervisor.service
-                               - Sun 2026-09-20 17:30:07 UTC    821ms ago trading-ops.timer        trading-ops.service
-                               - Sun 2026-09-20 15:07:57 UTC 2h 22min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
