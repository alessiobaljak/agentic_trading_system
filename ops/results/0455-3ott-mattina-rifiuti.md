# 0455-3ott-mattina-rifiuti.req

_eseguito: 2026-10-03 06:19 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.2s

```
Oct 02 07:17:38 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 02 07:32:52 Trading-Agent python[2005927]: [rifiuto] EPICUSDT gen_dfb554f7 long: posizione gia' aperta su questa coin
Oct 02 07:32:52 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 02 10:17:51 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_fb7d035a long: posizione gia' aperta su questa coin
Oct 02 17:17:27 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_fb3d971f long: posizione gia' aperta su questa coin
Oct 02 18:47:51 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_fb3d971f long: cooldown dopo stop (53m)
Oct 02 18:47:55 Trading-Agent python[2005927]: [rifiuto] RSRUSDT gen_b2f350ff long: correlazione: Troppe posizioni correlate >0.85 (PENGUUSDT=0.92, DOTUSDT=0.93, SAHARAUSDT=0.96)
Oct 02 18:48:07 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_fb3d971f long: cooldown dopo stop (53m)
Oct 02 19:03:02 Trading-Agent python[2005927]: [rifiuto] PENGUUSDT gen_a32bee42 long: posizione gia' aperta su questa coin
Oct 02 19:03:03 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: cooldown dopo stop (38m)
Oct 02 19:03:03 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_919c110c long: posizione gia' aperta su questa coin
Oct 02 19:03:03 Trading-Agent python[2005927]: [rifiuto] SAHARAUSDT gen_95aff747 long: posizione gia' aperta su questa coin
Oct 02 19:03:03 Trading-Agent python[2005927]: [rifiuto] XPINUSDT gen_c60cc1b9 long: posizione gia' aperta su questa coin
Oct 02 19:18:03 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: cooldown dopo stop (23m)
Oct 02 19:18:03 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_919c110c long: posizione gia' aperta su questa coin
Oct 02 19:18:03 Trading-Agent python[2005927]: [rifiuto] USELESSUSDT gen_96c1ed1b long: posizione gia' aperta su questa coin
Oct 02 19:18:04 Trading-Agent python[2005927]: [rifiuto] FLOCKUSDT gen_c5194ce4 short: posizione gia' aperta su questa coin
Oct 02 19:32:59 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 02 23:02:40 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_f3661202 short: correlazione: Troppe posizioni correlate >0.85 (PENGUUSDT=0.85, DOTUSDT=0.89, USELESSUSDT=0.85, SAHARAUSDT=0.89)
Oct 02 23:32:31 Trading-Agent python[2005927]: [rifiuto] NEIROUSDT gen_413f1bd7 short: correlazione: Troppe posizioni correlate >0.85 (JUPUSDT=0.87, PENGUUSDT=0.93, DOTUSDT=0.90, SAHARAUSDT=0.94)
Oct 03 00:47:32 Trading-Agent python[2005927]: [rifiuto] JUPUSDT gen_bb762669 short: posizione gia' aperta su questa coin
Oct 03 04:17:56 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_87fce2d2 long: posizione gia' aperta su questa coin
Oct 03 04:32:40 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_87fce2d2 long: posizione gia' aperta su questa coin
```
