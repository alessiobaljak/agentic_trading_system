# 0493-5ott-mattina-log-bot.req

_eseguito: 2026-10-05 06:04 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 05 02:18:33 Trading-Agent python[2005927]: [main] pesi ricalcolati: 176 coppie strat×regime da 286 trade (30g)
Oct 05 02:18:34 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/mubarakusdt@bookTicker/uselessusdt@bookTicker
Oct 05 02:18:34 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 02:32:57 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 02:32:57 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 02:34:01 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 05 02:34:01 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 05 02:44:26 Trading-Agent python[2005927]: [main] market scan...
Oct 05 02:46:49 Trading-Agent python[2005927]: [scanner] 7 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 05 02:46:49 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 02:46:49 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 02:46:49 Trading-Agent python[2005927]: [main] valutate 76 coin validate (76 nel registro): ['IDUSDT', 'HUMAUSDT', 'PENGUUSDT', 'AINUSDT', 'STXUSDT', 'SUIUSDT', 'NEIROUSDT', 'PUNDIXUSDT', 'BRUSDT', 'FORMUSDT', 'ONGUSDT', 'MUBARAKUSDT', 'SCRUSDT', 'TRUMPUSDT', 'CVCUSDT', 'RAYSOLUSDT', 'RENDERUSDT', 'TUTUSDT', 'GPSUSDT', 'SKYAIUSDT', 'BTRUSDT', 'HEIUSDT', 'DOTUSDT', 'PHAUSDT', 'OPENUSDT', 'ENAUSDT', 'PNUTUSDT', 'JASMYUSDT', 'B2USDT', 'BANKUSDT', 'AIOUSDT', 'GALAUSDT', 'SPXUSDT', 'SOPHUSDT', 'PUMPUSDT', 'MITOUSDT', 'TSTUSDT', 'EPICUSDT', 'SUPERUSDT', 'ATOMUSDT', 'WALUSDT', 'SAHARAUSDT', 'BMTUSDT', 'AXSUSDT', 'MTLUSDT', 'HOMEUSDT', 'USELESSUSDT', 'DEXEUSDT', 'MYXUSDT', 'XPLUSDT', 'HEMIUSDT', 'CATIUSDT', 'PARTIUSDT', 'ZORAUSDT', 'ZKUSDT', 'RSRUSDT', 'GRIFFAINUSDT', 'THEUSDT', 'FLOCKUSDT', 'STEEMUSDT', 'XPINUSDT', 'JUPUSDT', 'BULLAUSDT', 'PTBUSDT', 'SYRUPUSDT', 'VETUSDT', 'TAUSDT', 'PLUMEUSDT', 'QUSDT', 'AVAAIUSDT', 'SEIUSDT', 'CROSSUSDT', 'UBUSDT', 'PROMUSDT', 'ARCUSDT', 'ORCAUSDT']
Oct 05 02:49:46 Trading-Agent python[2005927]: [scarti] 5 secondo segnale stessa coin
Oct 05 02:49:48 Trading-Agent python[2005927]: [selettore] UBUSDT gen_f3661202 long p=0.57 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 05 02:49:48 Trading-Agent python[2005927]: [DRY_RUN] OPEN long UBUSDT qty=1360.7799 @ 0.13645 lev=2.0x SL=0.1354 TP=0.1395
Oct 05 02:49:54 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/mubarakusdt@bookTicker/ubusdt@bookTicker/uselessusdt@bookTicker
Oct 05 02:50:20 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 05 02:50:20 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 02:50:20 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 02:59:48 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7862 (rifiutati 4210 · controllo 1426 · registro 1419 · trade 430 · pesi 127 · memoria 96 · deriva 45 · referti 45) — quota gratuita 50000/giorno
Oct 05 02:59:48 Trading-Agent python[2005927]: [learning] filtrati 11/286 trade (esplorativi: 11)
Oct 05 02:59:48 Trading-Agent python[2005927]: [main] pesi ricalcolati: 176 coppie strat×regime da 286 trade (30g)
Oct 05 02:59:49 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 02:59:51 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1566 ms
Oct 05 03:05:29 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 03:05:29 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 03:05:31 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 05 03:18:01 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 03:18:01 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 03:18:02 Trading-Agent python[2005927]: [selettore] ZORAUSDT gen_ceab7f6a long p=0.66 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 05 03:18:02 Trading-Agent python[2005927]: [DRY_RUN] OPEN long ZORAUSDT qty=14939.8854 @ 0.007747 lev=2.0x SL=0.0077 TP=0.0080
Oct 05 03:18:02 Trading-Agent python[2005927]: [declassata] ZORAUSDT gen_ceab7f6a long size x0.25
Oct 05 03:18:09 Trading-Agent python[2005927]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/mubarakusdt@bookTicker/ubusdt@bookTicker/uselessusdt@bookTicker/zorausdt@bookTicker
Oct 05 03:19:06 Trading-Agent python[2005927]: [DRY_RUN] CLOSE UBUSDT @ 0.13712925 (trailing_stop)
Oct 05 03:19:09 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 05 03:19:09 Trading-Agent python[2005927]: [learning] filtrati 11/287 trade (esplorativi: 11)
Oct 05 03:19:09 Trading-Agent python[2005927]: [main] pesi ricalcolati: 176 coppie strat×regime da 287 trade (30g)
Oct 05 03:19:11 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 03:19:12 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/mubarakusdt@bookTicker/uselessusdt@bookTicker/zorausdt@bookTicker
Oct 05 03:32:39 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 03:32:39 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 03:32:39 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 05 03:34:18 Trading-Agent python[2005927]: [rifiutati] 2 segnali rifiutati valutati
Oct 05 03:44:24 Trading-Agent python[2005927]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.07052928704457621 (stop_loss)
Oct 05 03:44:24 Trading-Agent python[2005927]: [referto] MUBARAKUSDT gen_e933160c: mai andato a favore (mfe 0.17R): direzione sbagliata
Oct 05 03:44:28 Trading-Agent python[2005927]: [learning] filtrati 11/288 trade (esplorativi: 11)
Oct 05 03:44:28 Trading-Agent python[2005927]: [main] pesi ricalcolati: 176 coppie strat×regime da 288 trade (30g)
Oct 05 03:44:29 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 03:44:30 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/uselessusdt@bookTicker/zorausdt@bookTicker
Oct 05 03:47:58 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 05 03:59:42 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-

[... 2566 caratteri omessi (testa e coda conservate) ...]

Agent python[2005927]: [main] pesi ricalcolati: 177 coppie strat×regime da 289 trade (30g)
Oct 05 04:13:51 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 04:13:52 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=uselessusdt@bookTicker/zorausdt@bookTicker
Oct 05 04:18:21 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 05 04:26:34 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 05 04:29:09 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 04:29:09 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 04:33:12 Trading-Agent python[2005927]: [DRY_RUN] CLOSE ZORAUSDT @ 0.0076557282784572404 (stop_loss)
Oct 05 04:33:12 Trading-Agent python[2005927]: [referto] ZORAUSDT gen_ceab7f6a: mai andato a favore (mfe 0.03R): direzione sbagliata
Oct 05 04:33:16 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 05 04:33:16 Trading-Agent python[2005927]: [learning] filtrati 11/290 trade (esplorativi: 11)
Oct 05 04:33:17 Trading-Agent python[2005927]: [main] pesi ricalcolati: 177 coppie strat×regime da 290 trade (30g)
Oct 05 04:33:18 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 04:33:19 Trading-Agent python[2005927]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=uselessusdt@bookTicker
Oct 05 04:47:56 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 04:47:56 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 04:47:56 Trading-Agent python[2005927]: [panchina] HEMIUSDT gen_4c6df481: peso 0.46 -> size x0.46
Oct 05 04:47:58 Trading-Agent python[2005927]: [selettore] HEMIUSDT gen_4c6df481 long p=0.65 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 05 04:47:58 Trading-Agent python[2005927]: [DRY_RUN] OPEN long HEMIUSDT qty=6740.0454 @ 0.005954 lev=1.0x SL=0.0059 TP=0.0061
Oct 05 04:47:58 Trading-Agent python[2005927]: [esplorativa] HEMIUSDT gen_4c6df481 long size x0.25
Oct 05 04:48:04 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/uselessusdt@bookTicker
Oct 05 04:48:31 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 05 04:48:32 Trading-Agent python[2005927]: [rifiutati] 2 segnali rifiutati valutati
Oct 05 05:00:21 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7457 (rifiutati 3940 · controllo 1364 · registro 1356 · trade 415 · pesi 131 · memoria 92 · deriva 48 · referti 48) — quota gratuita 50000/giorno
Oct 05 05:00:21 Trading-Agent python[2005927]: [learning] filtrati 11/290 trade (esplorativi: 11)
Oct 05 05:00:22 Trading-Agent python[2005927]: [main] pesi ricalcolati: 177 coppie strat×regime da 290 trade (30g)
Oct 05 05:00:23 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 05:00:25 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1963 ms
Oct 05 05:03:58 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 05 05:03:58 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 05:03:58 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 05:17:45 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 05:17:45 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 05:19:20 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 05 05:32:36 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 05:32:36 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 05:38:17 Trading-Agent python[2005927]: [DRY_RUN] CLOSE USELESSUSDT @ 0.23627499999999999 (trailing_stop)
Oct 05 05:38:24 Trading-Agent python[2005927]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker
Oct 05 05:38:28 Trading-Agent python[2005927]: [learning] filtrati 11/291 trade (esplorativi: 11)
Oct 05 05:38:29 Trading-Agent python[2005927]: [main] pesi ricalcolati: 178 coppie strat×regime da 291 trade (30g)
Oct 05 05:38:30 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 05:47:33 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 05 05:47:33 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 05 05:47:35 Trading-Agent python[2005927]: [main] trade bloccato dal gate: stop troppo largo: 7.2% del prezzo > 6% (ATR gonfiato: primo incasso a +11%, lock a +5%)
Oct 05 05:47:35 Trading-Agent python[2005927]: [rifiuto] BRUSDT gen_95fb50ce long: risk gate: stop troppo largo: 7.2% del prezzo > 6% (ATR gonfiato: primo incasso a +11%, lock a +5%)
Oct 05 05:53:44 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 05 06:00:21 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7201 (rifiutati 3962 · controllo 1364 · registro 1348 · trade 147 · pesi 130 · memoria 92 · deriva 48 · referti 48) — quota gratuita 50000/giorno
Oct 05 06:00:21 Trading-Agent python[2005927]: [learning] filtrati 11/291 trade (esplorativi: 11)
Oct 05 06:00:22 Trading-Agent python[2005927]: [main] pesi ricalcolati: 178 coppie strat×regime da 291 trade (30g)
Oct 05 06:00:23 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 05 06:00:26 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1866 ms
Oct 05 06:02:52 Trading-Agent python[2005927]: [selettore] MUBARAKUSDT gen_1f7ead60 short p=0.60 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 05 06:02:52 Trading-Agent python[2005927]: [DRY_RUN] OPEN short MUBARAKUSDT qty=454.8088 @ 0.07801 lev=2.0x SL=0.0803 TP=0.0712
Oct 05 06:02:52 Trading-Agent python[2005927]: [declassata] MUBARAKUSDT gen_1f7ead60 short size x0.25
Oct 05 06:03:01 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/mubarakusdt@bookTicker
```
