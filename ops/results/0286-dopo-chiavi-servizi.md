# 0286-dopo-chiavi-servizi.req

_eseguito: 2026-09-27 05:59 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                            LEFT LAST                              PASSED UNIT                     ACTIVATES
Sun 2026-09-27 06:02:10 UTC 2min 53s Sun 2026-09-27 05:05:00 UTC    54min ago trading-supervisor.timer trading-supervisor.service
Sun 2026-09-27 06:03:33 UTC 4min 15s Sun 2026-09-27 03:02:45 UTC 2h 56min ago trading-optimizer.timer  trading-optimizer.service
-                                  - Sun 2026-09-27 05:59:16 UTC    802ms ago trading-ops.timer        trading-ops.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
