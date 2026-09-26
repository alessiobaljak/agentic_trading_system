# 0268-controllo-26set-rifiuti.req

_eseguito: 2026-09-26 06:16 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Sep 25 09:32:05 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 09:47:16 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: posizione gia' aperta su questa coin
Sep 25 09:47:16 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:01:51 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:01:51 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (49m)
Sep 25 10:17:16 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:17:16 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (34m)
Sep 25 10:32:09 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:32:09 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (19m)
Sep 25 10:47:03 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (4m)
Sep 25 10:47:03 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (47m)
Sep 25 11:01:53 Trading-Agent python[1675917]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] USELESSUSDT gen_2031005e: peso 0.26: confidenza 16 < soglia 30
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: posizione gia' aperta su questa coin
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (51m)
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (17m)
Sep 25 11:32:13 Trading-Agent python[1675917]: [rifiuto] USELESSUSDT gen_2031005e: peso 0.26: confidenza 16 < soglia 30
Sep 25 11:32:13 Trading-Agent python[1675917]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (36m)
Sep 25 11:46:13 Trading-Agent python[1681701]: [rifiuto] USELESSUSDT gen_2031005e: peso 0.26: confidenza 16 < soglia 30
Sep 25 11:46:13 Trading-Agent python[1681701]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (24m)
Sep 25 11:48:41 Trading-Agent python[1681701]: [rifiuto] SUIUSDT gen_490a90e5 short: cooldown dopo stop (26m)
Sep 25 11:48:43 Trading-Agent python[1681701]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (20m)
Sep 25 12:02:07 Trading-Agent python[1681701]: [rifiuto] SUIUSDT gen_490a90e5 short: cooldown dopo stop (12m)
Sep 25 12:02:07 Trading-Agent python[1681701]: [rifiuto] DOTUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 12:11:50 Trading-Agent python[1682472]: [rifiuto] SUIUSDT gen_490a90e5 short: cooldown dopo stop (4m)
Sep 25 12:11:50 Trading-Agent python[1682472]: [rifiuto] DOTUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 13:02:14 Trading-Agent python[1682472]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 13:16:50 Trading-Agent python[1682472]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 13:16:50 Trading-Agent python[1682472]: [rifiuto] SUIUSDT gen_490a90e5 short: posizione gia' aperta su questa coin
Sep 25 13:31:53 Trading-Agent python[1682472]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (50m)
Sep 25 13:31:53 Trading-Agent python[1682472]: [rifiuto] SUIUSDT gen_490a90e5 short: posizione gia' aperta su questa coin
Sep 25 13:47:15 Trading-Agent python[1682472]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (34m)
Sep 25 15:31:50 Trading-Agent python[1682472]: [rifiuto] MUBARAKUSDT gen_1f7ead60 short: cooldown dopo stop (55m)
Sep 25 16:16:50 Trading-Agent python[1682472]: [rifiuto] MUBARAKUSDT gen_2053cba6 short: cooldown dopo stop (10m)
Sep 25 16:35:36 Trading-Agent python[1688981]: [rifiuto] MUBARAKUSDT gen_49c2f657 short: posizione gia' aperta su questa coin
Sep 25 21:00:39 Trading-Agent python[1696285]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 23:16:56 Trading-Agent python[1696285]: [rifiuto] QUSDT gen_18c839a0 long: posizione gia' aperta su questa coin
Sep 25 23:32:14 Trading-Agent python[1696285]: [rifiuto] QUSDT gen_bf2be656 long: posizione gia' aperta su questa coin
Sep 26 06:02:14 Trading-Agent python[1696285]: [rifiuto] MUBARAKUSDT gen_ff3e4154 long: risk gate: stop troppo largo: 9.2% del prezzo > 6% (ATR gonfiato: primo incasso a +14%, lock a +7%)
```
