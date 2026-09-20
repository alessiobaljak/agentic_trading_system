# 0108-quando-gira.req

_eseguito: 2026-09-20 06:36 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                           PASSED UNIT                     ACTIVATES
Sun 2026-09-20 07:00:42 UTC 23min Sun 2026-09-20 06:01:01 UTC 35min ago trading-supervisor.timer trading-supervisor.service
-                               - Sun 2026-09-20 06:36:52 UTC 830ms ago trading-ops.timer        trading-ops.service
-                               - Sun 2026-09-20 06:02:34 UTC 34min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
