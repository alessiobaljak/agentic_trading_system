# 0158-servizi-mattina.req

_eseguito: 2026-09-23 04:56 UTC_

**richiesta:** `servizi`
**eseguito:** `systemctl list-timers --no-pager trading-*`
**esito:** codice 0 in 0.0s

```
NEXT                        LEFT LAST                              PASSED UNIT                     ACTIVATES
Wed 2026-09-23 05:03:59 UTC 7min Wed 2026-09-23 04:01:51 UTC    54min ago trading-supervisor.timer trading-supervisor.service
-                              - Wed 2026-09-23 04:56:05 UTC       2s ago trading-ops.timer        trading-ops.service
-                              - Wed 2026-09-23 03:07:56 UTC 1h 48min ago trading-optimizer.timer  trading-optimizer.service

3 timers listed.
Pass --all to see loaded but inactive timers, too.
```
