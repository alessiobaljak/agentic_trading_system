# 0482-4ott-settimanale-servizi.req

_eseguito: 2026-10-04 07:19 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                         LEFT LAST                              PASSED UNIT                     ACTIVATES
Sun 2026-10-04 08:04:52 UTC 45min Sun 2026-10-04 07:04:06 UTC    15min ago trading-supervisor.timer trading-supervisor.service
-                               - Sun 2026-10-04 07:14:00 UTC     5min ago trading-ops.timer        trading-ops.service
-                               - Sun 2026-10-04 06:04:25 UTC 1h 15min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
