# 0270-controllo-26set-servizi.req

_eseguito: 2026-09-26 06:18 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                           PASSED UNIT                     ACTIVATES
Sat 2026-09-26 07:03:58 UTC 45min Sat 2026-09-26 06:02:49 UTC 15min ago trading-supervisor.timer trading-supervisor.service
-                               - Sat 2026-09-26 06:18:43 UTC 735ms ago trading-ops.timer        trading-ops.service
-                               - Sat 2026-09-26 06:01:25 UTC 17min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
