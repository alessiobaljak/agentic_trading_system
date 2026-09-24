# 0193-servizi.req

_eseguito: 2026-09-24 12:30 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                            LEFT LAST                           PASSED UNIT                     ACTIVATES
Thu 2026-09-24 13:01:47 UTC    31min Thu 2026-09-24 12:02:43 UTC 27min ago trading-supervisor.timer trading-supervisor.service
Thu 2026-09-24 15:04:20 UTC 2h 34min Thu 2026-09-24 12:03:40 UTC 26min ago trading-optimizer.timer  trading-optimizer.service
-                                  - Thu 2026-09-24 12:30:01 UTC    1s ago trading-ops.timer        trading-ops.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
