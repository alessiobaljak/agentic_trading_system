# 0275-giro-completo-servizi.req

_eseguito: 2026-09-26 10:47 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Sat 2026-09-26 11:02:36 UTC 15min Sat 2026-09-26 10:03:08 UTC    44min ago trading-supervisor.timer trading-supervisor.service
-                               - Sat 2026-09-26 10:47:13 UTC       2s ago trading-ops.timer        trading-ops.service
-                               - Sat 2026-09-26 09:04:41 UTC 1h 42min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
