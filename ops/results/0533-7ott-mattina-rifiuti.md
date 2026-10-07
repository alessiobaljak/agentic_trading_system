# 0533-7ott-mattina-rifiuti.req

_eseguito: 2026-10-07 06:23 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.1s

```
Oct 06 07:47:54 Trading-Agent python[2005927]: [rifiuto] GUNUSDT gen_4f890271 short: posizione gia' aperta su questa coin
Oct 06 08:03:08 Trading-Agent python[2005927]: [rifiuto] GUNUSDT gen_4f890271 short: posizione gia' aperta su questa coin
Oct 06 09:18:11 Trading-Agent python[2005927]: [rifiuto] TUTUSDT gen_4465723e long: posizione gia' aperta su questa coin
Oct 06 10:48:04 Trading-Agent python[2005927]: [rifiuto] HOMEUSDT gen_a524effe short: cooldown dopo stop (55m)
Oct 06 11:02:47 Trading-Agent python[2005927]: [rifiuto] HOMEUSDT gen_a524effe short: cooldown dopo stop (41m)
Oct 06 12:03:15 Trading-Agent python[2005927]: [rifiuto] RSRUSDT gen_b2f350ff short: posizione gia' aperta su questa coin
Oct 06 16:47:49 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_32ccfe0c long: risk gate: stop troppo largo: 6.0% del prezzo > 6% (ATR gonfiato: primo incasso a +9%, lock a +5%)
Oct 06 18:03:15 Trading-Agent python[2005927]: [rifiuto] ORCAUSDT gen_cb8176f2 short: risk gate: stop troppo largo: 6.7% del prezzo > 6% (ATR gonfiato: primo incasso a +10%, lock a +5%)
Oct 06 19:32:54 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_0d7be682 long: posizione gia' aperta su questa coin
Oct 06 19:47:54 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_0d7be682 long: posizione gia' aperta su questa coin
Oct 06 20:17:49 Trading-Agent python[2005927]: [rifiuto] GRIFFAINUSDT gen_de018454 long: risk gate: stop troppo largo: 12.5% del prezzo > 6% (ATR gonfiato: primo incasso a +19%, lock a +9%)
Oct 06 20:17:49 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_0d7be682 long: posizione gia' aperta su questa coin
Oct 07 01:33:02 Trading-Agent python[2005927]: [rifiuto] SAHARAUSDT gen_6b94025f long: posizione gia' aperta su questa coin
Oct 07 02:03:08 Trading-Agent python[2005927]: [rifiuto] SAHARAUSDT gen_4e6e1ae0 long: cooldown dopo stop (34m)
Oct 07 02:18:11 Trading-Agent python[2005927]: [rifiuto] PTBUSDT gen_684d7623 long: cooldown dopo stop (48m)
Oct 07 02:18:23 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: cooldown dopo stop (48m)
Oct 07 02:18:24 Trading-Agent python[2005927]: [rifiuto] SAHARAUSDT gen_4e6e1ae0 long: cooldown dopo stop (19m)
Oct 07 02:18:27 Trading-Agent python[2005927]: [rifiuto] JUPUSDT gen_938d15dc long: posizione gia' aperta su questa coin
Oct 07 02:18:30 Trading-Agent python[2005927]: [rifiuto] RSRUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 02:18:31 Trading-Agent python[2005927]: [rifiuto] CVCUSDT gen_7b4a474b long: posizione gia' aperta su questa coin
Oct 07 02:18:32 Trading-Agent python[2005927]: [rifiuto] B2USDT gen_ddb3def9 long: margine insufficiente (usato 905 + nuovo 44 > equity 918)
Oct 07 02:18:33 Trading-Agent python[2005927]: [rifiuto] DEXEUSDT gen_b9c251a1 long: margine insufficiente (usato 905 + nuovo 88 > equity 918)
Oct 07 02:32:59 Trading-Agent python[2005927]: [rifiuto] PTBUSDT gen_684d7623 long: cooldown dopo stop (33m)
Oct 07 02:33:00 Trading-Agent python[2005927]: [rifiuto] JASMYUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 02:33:00 Trading-Agent python[2005927]: [rifiuto] KERNELUSDT gen_c647ead7 long: posizione gia' aperta su questa coin
Oct 07 02:33:00 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: cooldown dopo stop (33m)
Oct 07 02:33:00 Trading-Agent python[2005927]: [rifiuto] SAHARAUSDT gen_4e6e1ae0 long: cooldown dopo stop (4m)
Oct 07 02:33:00 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 02:33:09 Trading-Agent python[2005927]: [rifiuto] JUPUSDT gen_938d15dc long: posizione gia' aperta su questa coin
Oct 07 02:33:09 Trading-Agent python[2005927]: [rifiuto] CVCUSDT gen_8c9b332f long: posizione gia' aperta su questa coin
Oct 07 02:48:05 Trading-Agent python[2005927]: [rifiuto] PROMUSDT gen_cd5c842f short: posizione gia' aperta su questa coin
Oct 07 02:48:05 Trading-Agent python[2005927]: [rifiuto] KERNELUSDT gen_c647ead7 long: posizione gia' aperta su questa coin
Oct 07 02:48:05 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: cooldown dopo stop (18m)
Oct 07 02:48:05 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 02:48:05 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 02:48:05 Trading-Agent python[2005927]: [rifiuto] RSRUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 03:03:18 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: cooldown dopo stop (3m)
Oct 07 03:03:18 Trading-Agent python[2005927]: [rifiuto] KERNELUSDT gen_c647ead7 long: posizione gia' aperta su questa coin
Oct 07 03:03:18 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 03:03:18 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 03:03:19 Trading-Agent python[2005927]: [rifiuto] RSRUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 03:03:19 Trading-Agent python[2005927]: [rifiuto] CVCUSDT gen_8c9b332f long: posizione gia' aperta su questa coin
Oct 07 03:18:27 Trading-Agent python[2005927]: [rifiuto] KERNELUSDT gen_c647ead7 long: posizione gia' aperta su questa coin
Oct 07 03:18:27 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 03:18:28 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 03:33:06 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 03:33:06 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 03:33:06 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 03:48:06 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 03:48:06 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:03:13 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:03:13 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:18:15 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:18:15 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:33:17 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:33:17 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:47:59 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:48:04 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 05:03:01 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 05:03:01 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 05:48:09 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 07 06:03:08 Trading-Agent python[2005927]: [rifiuto] SYRUPUSDT gen_f3b97917 long: posizione gia' aperta su questa coin
Oct 07 06:03:08 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 07 06:17:54 Trading-Agent python[2005927]: [rifiuto] SYRUPUSDT gen_f3b97917 long: posizione gia' aperta su questa coin
Oct 07 06:17:58 Trading-Agent python[2005927]: [rifiuto] SAHARAUSDT gen_66848d49 long: correlazione: Troppe posizioni correlate >0.85 (VETUSDT=0.88, HEMIUSDT=0.90, DOTUSDT=0.87, PUNDIXUSDT=0.91)
```
