# 0499-5ott-mattina-rifiuti.req

_eseguito: 2026-10-05 06:20 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Oct 04 06:48:24 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: risk gate: stop troppo largo: 20.2% del prezzo > 6% (ATR gonfiato: primo incasso a +30%, lock a +15%)
Oct 04 07:02:51 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: risk gate: stop troppo largo: 19.3% del prezzo > 6% (ATR gonfiato: primo incasso a +29%, lock a +14%)
Oct 04 10:32:34 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 04 11:33:06 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 04 13:47:49 Trading-Agent python[2005927]: [rifiuto] TAUSDT gen_543186c5 long: posizione gia' aperta su questa coin
Oct 04 14:48:40 Trading-Agent python[2005927]: [rifiuto] PLUMEUSDT gen_902fb1fd short: cooldown dopo stop (48m)
Oct 04 17:32:43 Trading-Agent python[2005927]: [rifiuto] MYXUSDT gen_a5b0e4de long: posizione gia' aperta su questa coin
Oct 04 21:17:50 Trading-Agent python[2005927]: [rifiuto] HEMIUSDT gen_f001d778 long: posizione gia' aperta su questa coin
Oct 05 01:47:40 Trading-Agent python[2005927]: [rifiuto] MUBARAKUSDT gen_658b2edb short: posizione gia' aperta su questa coin
Oct 05 02:02:51 Trading-Agent python[2005927]: [rifiuto] MUBARAKUSDT gen_e933160c short: posizione gia' aperta su questa coin
Oct 05 03:32:39 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 05 03:47:58 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 05 04:02:51 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: risk gate: stop troppo largo: 9.7% del prezzo > 6% (ATR gonfiato: primo incasso a +15%, lock a +7%)
Oct 05 05:47:35 Trading-Agent python[2005927]: [rifiuto] BRUSDT gen_95fb50ce long: risk gate: stop troppo largo: 7.2% del prezzo > 6% (ATR gonfiato: primo incasso a +11%, lock a +5%)
```
