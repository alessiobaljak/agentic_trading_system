# 0299-controllo-27set-rifiuti.req

_eseguito: 2026-09-27 06:16 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.2s

```
Sep 26 11:17:09 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 11:32:33 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 11:47:23 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 12:02:15 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 12:17:38 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 12:32:15 Trading-Agent python[1711223]: [rifiuto] STXUSDT gen_14e1775b long: posizione gia' aperta su questa coin
Sep 26 12:32:15 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 12:47:10 Trading-Agent python[1711223]: [rifiuto] STXUSDT gen_14e1775b long: posizione gia' aperta su questa coin
Sep 26 12:47:10 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (47m)
Sep 26 13:02:42 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (32m)
Sep 26 13:17:21 Trading-Agent python[1711223]: [rifiuto] SYRUPUSDT gen_4c6df481 short: posizione gia' aperta su questa coin
Sep 26 13:17:21 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (17m)
Sep 26 13:32:35 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (2m)
Sep 26 13:47:38 Trading-Agent python[1711223]: [rifiuto] TUTUSDT gen_4465723e long: posizione gia' aperta su questa coin
Sep 26 14:02:14 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 14:17:19 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (54m)
Sep 26 14:32:24 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (39m)
Sep 26 14:47:46 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (24m)
Sep 26 15:02:27 Trading-Agent python[1711223]: [rifiuto] TUTUSDT gen_4465723e long: posizione gia' aperta su questa coin
Sep 26 15:02:27 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (9m)
Sep 26 15:32:35 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (58m)
Sep 26 15:32:35 Trading-Agent python[1711223]: [rifiuto] DOTUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 15:47:24 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (43m)
Sep 26 15:47:25 Trading-Agent python[1711223]: [rifiuto] DOTUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 16:02:31 Trading-Agent python[1711223]: [rifiuto] DOTUSDT gen_4d7f7bd3 short: posizione gia' aperta su questa coin
Sep 26 16:02:31 Trading-Agent python[1711223]: [rifiuto] HUMAUSDT gen_6d06dca0 short: cooldown dopo stop (28m)
Sep 26 16:32:31 Trading-Agent python[1711223]: [rifiuto] TAUSDT gen_bf2be656 long: posizione gia' aperta su questa coin
Sep 26 16:47:20 Trading-Agent python[1711223]: [rifiuto] QUSDT gen_cde82a91 long: risk gate: stop troppo largo: 15.1% del prezzo > 6% (ATR gonfiato: primo incasso a +23%, lock a +11%)
Sep 26 16:47:20 Trading-Agent python[1711223]: [rifiuto] DOTUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 26 17:02:28 Trading-Agent python[1711223]: [rifiuto] DOTUSDT gen_4d7f7bd3 short: cooldown dopo stop (47m)
Sep 26 18:32:36 Trading-Agent python[1711223]: [rifiuto] CROSSUSDT gen_d606fde3 long: posizione gia' aperta su questa coin
Sep 27 00:32:07 Trading-Agent python[1733042]: [rifiuto] XPLUSDT gen_2f405402 long: posizione gia' aperta su questa coin
Sep 27 01:02:09 Trading-Agent python[1733042]: [rifiuto] XPLUSDT gen_2f405402 long: posizione gia' aperta su questa coin
Sep 27 03:32:27 Trading-Agent python[1733042]: [rifiuto] XPLUSDT gen_e59ad90b long: posizione gia' aperta su questa coin
```
