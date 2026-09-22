# 0137-tempo-giro.req

_eseguito: 2026-09-22 05:45 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Tue 2026-09-22 06:01:05 UTC 15min Tue 2026-09-22 05:04:07 UTC    41min ago trading-supervisor.timer trading-supervisor.service
-                               - Tue 2026-09-22 05:45:43 UTC    876ms ago trading-ops.timer        trading-ops.service
-                               - Tue 2026-09-22 02:52:36 UTC 2h 53min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
