# 0595-11ott-settimanale-servizi.req

_eseguito: 2026-10-11 04:04 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Sun 2026-10-11 05:02:10 UTC 57min Sun 2026-10-11 04:02:30 UTC 2min 10s ago trading-supervisor.timer trading-supervisor.service
-                               - Sun 2026-10-11 03:47:23 UTC    17min ago trading-ops.timer        trading-ops.service
-                               - Sun 2026-10-11 01:40:54 UTC 2h 23min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
