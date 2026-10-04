# 0475-4ott-mattina-rifiuti.req

_eseguito: 2026-10-04 06:20 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Oct 03 07:32:43 Trading-Agent python[2005927]: [rifiuto] HUMAUSDT gen_da39a23a: veto di regime (sideways)
Oct 03 08:02:32 Trading-Agent python[2005927]: [rifiuto] PLUMEUSDT gen_902fb1fd long: posizione gia' aperta su questa coin
Oct 03 08:02:32 Trading-Agent python[2005927]: [rifiuto] HUMAUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 03 10:17:43 Trading-Agent python[2005927]: [rifiuto] RENDERUSDT gen_1eec02f5 short: correlazione: Troppe posizioni correlate >0.85 (JUPUSDT=0.89, DOTUSDT=0.87, PLUMEUSDT=0.86)
Oct 03 10:17:43 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_919c110c short: posizione gia' aperta su questa coin
Oct 03 10:47:32 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_d85b1f05 short: posizione gia' aperta su questa coin
Oct 03 20:47:52 Trading-Agent python[2005927]: [rifiuto] QUSDT gen_18c839a0 short: posizione gia' aperta su questa coin
Oct 04 00:02:31 Trading-Agent python[2005927]: [rifiuto] STXUSDT gen_14e1775b long: posizione gia' aperta su questa coin
```
