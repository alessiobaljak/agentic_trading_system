# 0430-2ott-mattina-rifiuti.req

_eseguito: 2026-10-02 06:17 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Oct 01 07:32:32 Trading-Agent python[1927496]: [rifiuto] BTRUSDT gen_8981d5f2 long: posizione gia' aperta su questa coin
Oct 01 07:47:53 Trading-Agent python[1927496]: [rifiuto] BTRUSDT gen_8981d5f2 long: posizione gia' aperta su questa coin
Oct 01 18:17:43 Trading-Agent python[1975598]: [rifiuto] QUSDT gen_18c839a0 long: posizione gia' aperta su questa coin
Oct 01 21:47:32 Trading-Agent python[1975598]: [rifiuto] TAUSDT gen_4e6e1ae0 long: cooldown dopo stop (58m)
Oct 01 22:02:28 Trading-Agent python[1975598]: [rifiuto] TAUSDT gen_4e6e1ae0 long: cooldown dopo stop (43m)
Oct 02 00:17:51 Trading-Agent python[1975598]: [rifiuto] QUSDT gen_1e7e2564 long: cooldown dopo stop (57m)
Oct 02 02:02:44 Trading-Agent python[1975598]: [rifiuto] SCRUSDT gen_bd8f158b short: risk gate: stop troppo largo: 6.2% del prezzo > 6% (ATR gonfiato: primo incasso a +9%, lock a +5%)
Oct 02 02:17:19 Trading-Agent python[1975598]: [rifiuto] SCRUSDT gen_bd8f158b short: risk gate: stop troppo largo: 7.1% del prezzo > 6% (ATR gonfiato: primo incasso a +11%, lock a +5%)
Oct 02 03:47:23 Trading-Agent python[1975598]: [rifiuto] SCRUSDT gen_bd8f158b short: risk gate: stop troppo largo: 9.8% del prezzo > 6% (ATR gonfiato: primo incasso a +15%, lock a +7%)
Oct 02 04:47:32 Trading-Agent python[1975598]: [rifiuto] ENAUSDT gen_bb762669 short: posizione gia' aperta su questa coin
Oct 02 05:17:21 Trading-Agent python[1975598]: [rifiuto] HUMAUSDT gen_771790b1 short: posizione gia' aperta su questa coin
Oct 02 05:47:47 Trading-Agent python[1975598]: [rifiuto] HUMAUSDT gen_771790b1 short: posizione gia' aperta su questa coin
```
