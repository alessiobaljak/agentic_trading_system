# 0280-giro-completo-servizi-3.req

_eseguito: 2026-09-26 12:18 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Sat 2026-09-26 13:02:54 UTC 44min Sat 2026-09-26 12:00:04 UTC    18min ago trading-supervisor.timer trading-supervisor.service
-                               - Sat 2026-09-26 12:18:42 UTC       2s ago trading-ops.timer        trading-ops.service
-                               - Sat 2026-09-26 09:04:41 UTC 3h 14min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
