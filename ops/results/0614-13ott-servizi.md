# 0614-13ott-servizi.req

_eseguito: 2026-10-13 18:10 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Tue 2026-10-13 19:03:25 UTC 53min Tue 2026-10-13 18:03:41 UTC     6min ago trading-supervisor.timer trading-supervisor.service
-                               - Tue 2026-10-13 18:10:01 UTC       1s ago trading-ops.timer        trading-ops.service
-                               - Tue 2026-10-13 15:34:56 UTC 2h 35min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
