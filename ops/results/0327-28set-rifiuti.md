# 0327-28set-rifiuti.req

_eseguito: 2026-09-28 05:34 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Sep 27 06:52:46 Trading-Agent python[1755628]: [rifiuto] SUIUSDT gen_490a90e5 short: posizione gia' aperta su questa coin
Sep 27 08:02:36 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (60m)
Sep 27 08:17:49 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_271ab7ec short: cooldown dopo stop (44m)
Sep 27 08:32:19 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_cb8176f2 short: cooldown dopo stop (30m)
Sep 27 08:47:25 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_cb8176f2 short: cooldown dopo stop (15m)
Sep 27 09:02:51 Trading-Agent python[1755628]: [rifiuto] SUIUSDT gen_490a90e5 short: posizione gia' aperta su questa coin
Sep 27 10:02:49 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (51m)
Sep 27 10:17:34 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (37m)
Sep 27 10:32:22 Trading-Agent python[1755628]: [rifiuto] DEXEUSDT gen_887d87df long: posizione gia' aperta su questa coin
Sep 27 10:32:22 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_cb8176f2 short: cooldown dopo stop (22m)
Sep 27 10:47:44 Trading-Agent python[1755628]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (6m)
Sep 27 11:32:29 Trading-Agent python[1755628]: [rifiuto] DEXEUSDT gen_887d87df long: posizione gia' aperta su questa coin
Sep 27 11:47:29 Trading-Agent python[1755628]: [rifiuto] USELESSUSDT gen_2031005e short: posizione gia' aperta su questa coin
Sep 27 13:02:41 Trading-Agent python[1768344]: [rifiuto] SPXUSDT gen_d53c153b long: posizione gia' aperta su questa coin
Sep 27 13:32:06 Trading-Agent python[1769840]: [rifiuto] SOLUSDT gen_f3124a14 long: posizione gia' aperta su questa coin
Sep 27 13:35:07 Trading-Agent python[1769840]: [rifiuto] SOLUSDT gen_f3124a14 long: posizione gia' aperta su questa coin
Sep 27 14:32:40 Trading-Agent python[1769840]: [rifiuto] XMRUSDT gen_35632db9 long: posizione gia' aperta su questa coin
Sep 27 15:17:33 Trading-Agent python[1769840]: [rifiuto] XMRUSDT gen_35632db9 long: cooldown dopo stop (58m)
Sep 27 15:32:29 Trading-Agent python[1769840]: [rifiuto] XMRUSDT gen_35632db9 long: cooldown dopo stop (43m)
Sep 27 22:32:34 Trading-Agent python[1778756]: [rifiuto] SKYAIUSDT gen_6191df86 short: posizione gia' aperta su questa coin
Sep 28 02:17:06 Trading-Agent python[1778756]: [rifiuto] QUSDT gen_18c839a0 long: risk gate: stop troppo largo: 7.0% del prezzo > 6% (ATR gonfiato: primo incasso a +10%, lock a +5%)
```
