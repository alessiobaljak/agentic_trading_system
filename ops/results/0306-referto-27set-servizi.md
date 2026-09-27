# 0306-referto-27set-servizi.req

_eseguito: 2026-09-27 07:09 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                            LEFT LAST                             PASSED UNIT                     ACTIVATES
Sun 2026-09-27 08:03:49 UTC    54min Sun 2026-09-27 07:02:00 UTC    7min ago trading-supervisor.timer trading-supervisor.service
Sun 2026-09-27 09:01:01 UTC 1h 51min Sun 2026-09-27 06:03:33 UTC 1h 5min ago trading-optimizer.timer  trading-optimizer.service
-                                  - Sun 2026-09-27 07:04:16 UTC    5min ago trading-ops.timer        trading-ops.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
