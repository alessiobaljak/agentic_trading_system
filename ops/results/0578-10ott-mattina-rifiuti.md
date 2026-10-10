# 0578-10ott-mattina-rifiuti.req

_eseguito: 2026-10-10 04:06 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.2s

```
Oct 09 09:47:58 Trading-Agent python[2005927]: [rifiuto] QUSDT gen_1f224994 short: risk gate: stop troppo largo: 12.8% del prezzo > 6% (ATR gonfiato: primo incasso a +19%, lock a +10%)
Oct 09 09:47:58 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 09 10:47:57 Trading-Agent python[2005927]: [rifiuto] GUNUSDT gen_4f890271 long: correlazione: Troppe posizioni correlate >0.85 (VETUSDT=0.88, SOPHUSDT=0.85, ZORAUSDT=0.93, FLOCKUSDT=0.91)
Oct 09 10:47:57 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_2bb283ca long: cooldown dopo stop (49m)
Oct 09 10:47:59 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 09 12:47:36 Trading-Agent python[2005927]: [rifiuto] HYPEUSDT gen_f19b67e8: veto di regime (sideways)
Oct 09 14:02:48 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: posizione gia' aperta su questa coin
Oct 09 15:17:45 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: cooldown dopo stop (48m)
Oct 09 15:33:06 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: cooldown dopo stop (33m)
Oct 10 03:02:52 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_0d7be682 long: posizione gia' aperta su questa coin
```
