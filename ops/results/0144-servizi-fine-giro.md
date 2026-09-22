# 0144-servizi-fine-giro.req

_eseguito: 2026-09-22 06:02 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Tue 2026-09-22 07:01:28 UTC 58min Tue 2026-09-22 06:01:05 UTC 1min 44s ago trading-supervisor.timer trading-supervisor.service
-                               - Tue 2026-09-22 06:02:48 UTC    817ms ago trading-ops.timer        trading-ops.service
-                               - Tue 2026-09-22 02:52:36 UTC 3h 10min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
