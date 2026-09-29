# 0349-29set-rifiuti.req

_eseguito: 2026-09-29 06:17 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Sep 28 09:47:41 Trading-Agent python[1807149]: [rifiuto] MUBARAKUSDT gen_2053cba6 short: cooldown dopo stop (52m)
Sep 28 10:17:31 Trading-Agent python[1807149]: [rifiuto] PHAUSDT gen_fa304106 short: posizione gia' aperta su questa coin
Sep 28 10:32:40 Trading-Agent python[1807149]: [rifiuto] PHAUSDT gen_fa304106 short: posizione gia' aperta su questa coin
Sep 28 10:47:15 Trading-Agent python[1807149]: [rifiuto] PHAUSDT gen_c5194ce4 short: posizione gia' aperta su questa coin
Sep 28 14:32:22 Trading-Agent python[1807149]: [rifiuto] AVAAIUSDT gen_14e1775b long: posizione gia' aperta su questa coin
Sep 28 14:47:46 Trading-Agent python[1807149]: [rifiuto] AVAAIUSDT gen_14e1775b long: posizione gia' aperta su questa coin
Sep 28 14:47:48 Trading-Agent python[1807149]: [rifiuto] QUSDT gen_85fadf54 long: risk gate: stop troppo largo: 9.2% del prezzo > 6% (ATR gonfiato: primo incasso a +14%, lock a +7%)
Sep 28 15:17:23 Trading-Agent python[1807149]: [rifiuto] UBUSDT gen_8931b93c long: posizione gia' aperta su questa coin
Sep 28 23:47:41 Trading-Agent python[1830204]: [rifiuto] FLOCKUSDT gen_c5194ce4 short: posizione gia' aperta su questa coin
Sep 29 01:02:30 Trading-Agent python[1830204]: [rifiuto] SYRUPUSDT gen_98d56766 short: cooldown dopo stop (47m)
Sep 29 02:17:36 Trading-Agent python[1830204]: [rifiuto] GPSUSDT gen_8a66a70b long: posizione gia' aperta su questa coin
Sep 29 03:02:14 Trading-Agent python[1830204]: [rifiuto] ORCAUSDT gen_9a383fff long: posizione gia' aperta su questa coin
```
