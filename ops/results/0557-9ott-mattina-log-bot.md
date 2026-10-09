# 0557-9ott-mattina-log-bot.req

_eseguito: 2026-10-09 03:47 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 09 00:33:47 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 13904 (rifiutati 10176 · controllo 1426 · registro 1352 · trade 512 · pesi 151 · memoria 95 · deriva 59 · referti 59) — quota gratuita 50000/giorno
Oct 09 00:33:47 Trading-Agent python[2005927]: [learning] filtrati 20/413 trade (esplorativi: 17 · short_duration: 3)
Oct 09 00:33:48 Trading-Agent python[2005927]: [main] pesi ricalcolati: 236 coppie strat×regime da 413 trade (30g)
Oct 09 00:33:49 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 09 00:33:49 Trading-Agent python[2005927]: [referti] 10 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 09 00:33:51 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 1 anomalie, 1793 ms
Oct 09 00:36:45 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 09 00:36:45 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 00:36:45 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 00:47:45 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 00:47:45 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 00:47:45 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 09 00:47:48 Trading-Agent python[2005927]: [rifiuto] STEEMUSDT gen_addf82da long: correlazione: Troppe posizioni correlate >0.85 (VETUSDT=0.86, ZORAUSDT=0.87, FLOCKUSDT=0.87, 1000PEPEUSDT=0.87)
Oct 09 00:51:46 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 09 00:51:46 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 09 00:51:52 Trading-Agent python[2005927]: [rifiutati] 2 segnali rifiutati valutati
Oct 09 01:02:54 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 01:02:54 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 01:02:54 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 09 01:02:56 Trading-Agent python[2005927]: [selettore] HEMIUSDT gen_acea368d short p=0.67 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 09 01:02:56 Trading-Agent python[2005927]: [DRY_RUN] OPEN short HEMIUSDT qty=15300.4040 @ 0.005824 lev=1.0x SL=0.0059 TP=0.0056
Oct 09 01:03:02 Trading-Agent python[2005927]: [price_stream] connesso · 11 simboli · wss://fstream.binance.com/stream?streams=1000pepeusdt@bookTicker/catiusdt@bookTicker/flockusdt@bookTicker/hemiusdt@bookTicker/openusdt@bookTicker/orcausdt@bookTicker/pumpusdt@bookTicker/sophusdt@bookTicker/superusdt@bookTicker/vetusdt@bookTicker/zorausdt@bookTicker
Oct 09 01:03:04 Trading-Agent python[2005927]: [rifiuto] STEEMUSDT gen_addf82da long: correlazione: Troppe posizioni correlate >0.85 (VETUSDT=0.86, ZORAUSDT=0.87, FLOCKUSDT=0.87, 1000PEPEUSDT=0.87)
Oct 09 01:03:06 Trading-Agent python[2005927]: [selettore] 0GUSDT gen_aa6bb820 long p=0.67 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 09 01:03:06 Trading-Agent python[2005927]: [DRY_RUN] OPEN long 0GUSDT qty=317.9078 @ 0.2803 lev=1.0x SL=0.2746 TP=0.2889
Oct 09 01:03:12 Trading-Agent python[2005927]: [price_stream] connesso · 12 simboli · wss://fstream.binance.com/stream?streams=0gusdt@bookTicker/1000pepeusdt@bookTicker/catiusdt@bookTicker/flockusdt@bookTicker/hemiusdt@bookTicker/openusdt@bookTicker/orcausdt@bookTicker/pumpusdt@bookTicker/sophusdt@bookTicker/superusdt@bookTicker/vetusdt@bookTicker/zorausdt@bookTicker
Oct 09 01:07:08 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 09 01:07:15 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 09 01:07:15 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 09 01:17:50 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 01:17:50 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 01:17:54 Trading-Agent python[2005927]: [selettore] QUSDT gen_1f224994 short p=0.70 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 09 01:17:54 Trading-Agent python[2005927]: [DRY_RUN] OPEN short QUSDT qty=517.0558 @ 0.0261 lev=1.0x SL=0.0276 TP=0.0222
Oct 09 01:17:54 Trading-Agent python[2005927]: [esplorativa] QUSDT gen_1f224994 short size x0.25
Oct 09 01:18:00 Trading-Agent python[2005927]: [price_stream] connesso · 13 simboli · wss://fstream.binance.com/stream?streams=0gusdt@bookTicker/1000pepeusdt@bookTicker/catiusdt@bookTicker/flockusdt@bookTicker/hemiusdt@bookTicker/openusdt@bookTicker/orcausdt@bookTicker/pumpusdt@bookTicker/qusdt@bookTicker/sophusdt@bookTicker/superusdt@bookTicker/vetusdt@bookTicker/zorausdt@bookTicker
Oct 09 01:23:08 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 09 01:30:40 Trading-Agent python[2005927]: [DRY_RUN] CLOSE 1000PEPEUSDT @ 0.0038686175 (trailing_stop)
Oct 09 01:30:49 Trading-Agent python[2005927]: [price_stream] connesso · 12 simboli · wss://fstream.binance.com/stream?streams=0gusdt@bookTicker/catiusdt@bookTicker/flockusdt@bookTicker/hemiusdt@bookTicker/openusdt@bookTicker/orcausdt@bookTicker/pumpusdt@bookTicker/qusdt@bookTicker/sophusdt@bookTicker/superusdt@bookTicker/vetusdt@bookTicker/zorausdt@bookTicker
Oct 09 01:33:15 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 01:33:15 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 01:33:18 Trading-Agent python[2005927]: [learning] filtrati 20/414 trade (esplorativi: 17 · short_duration: 3)
Oct 09 01:33:18 Trading-Agent python[2005927]: [main] pesi ricalcolati: 237 coppie strat×regime da 414 trade (30g)
Oct 09 01:33:19 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 09 01:33:20 Trading-Agent python[2005927]: [referti] 10 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 09 01:33:50 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 14230 (rifiutati 10491 · controllo 1426 · registro 1359 · trade 511 · pesi 152 · memoria 95 · deriva 59 · referti 59) — quota gratuita 50000/giorno
Oct 09 01:33:50 Trading-Agent python[2005927]: [learning] filtrati 20/414 trade (esplorativi: 17 · short_duration: 3)
Oct 09 01:33:50 Trading-Agent python[2005927]: [main] pesi ricalcolati: 237 coppie strat×regime da 414 trade (30g)
Oct 09 01:33:51 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 09 01:33:52 Trading-Agent python[2005927]: [referti] 10 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/

[... 6203 caratteri omessi (testa e coda conservate) ...]

ta (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 09 02:28:24 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 02:28:24 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 02:32:50 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 09 02:33:54 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 14379 (rifiutati 10643 · controllo 1426 · registro 1354 · trade 511 · pesi 153 · memoria 95 · deriva 60 · referti 60) — quota gratuita 50000/giorno
Oct 09 02:33:54 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 02:33:54 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 02:33:54 Trading-Agent python[2005927]: [learning] filtrati 21/416 trade (esplorativi: 18 · short_duration: 3)
Oct 09 02:33:54 Trading-Agent python[2005927]: [main] pesi ricalcolati: 238 coppie strat×regime da 416 trade (30g)
Oct 09 02:33:55 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 09 02:33:56 Trading-Agent python[2005927]: [referti] 10 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 09 02:33:58 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 2 anomalie, 1760 ms
Oct 09 02:43:32 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 02:43:32 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 02:43:35 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 09 02:43:41 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 09 02:53:24 Trading-Agent python[2005927]: [main] market scan...
Oct 09 02:55:51 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 02:55:51 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 02:55:52 Trading-Agent python[2005927]: [main] valutate 78 coin validate (78 nel registro): ['RAYSOLUSDT', '0GUSDT', 'VETUSDT', 'PLUMEUSDT', 'ZECUSDT', 'DOTUSDT', 'ENAUSDT', 'STXUSDT', 'TAOUSDT', 'JUPUSDT', 'PTBUSDT', 'AINUSDT', 'SPXUSDT', 'RENDERUSDT', 'MTLUSDT', 'THEUSDT', 'PUNDIXUSDT', 'ORCAUSDT', 'FORMUSDT', 'HEMIUSDT', 'IDOLUSDT', 'BRUSDT', 'ZKUSDT', 'RUNEUSDT', 'WALUSDT', 'MUBARAKUSDT', 'PUMPUSDT', 'TRUMPUSDT', 'AIOUSDT', 'SUIUSDT', 'QUSDT', 'USELESSUSDT', 'HYPEUSDT', 'BTRUSDT', 'STEEMUSDT', 'SCRUSDT', 'GRIFFAINUSDT', 'PARTIUSDT', 'CATIUSDT', '1000PEPEUSDT', 'SEIUSDT', 'IDUSDT', 'DEXEUSDT', 'GALAUSDT', 'HUMAUSDT', 'GUNUSDT', 'SKYAIUSDT', 'PNUTUSDT', 'BULLAUSDT', '1000BONKUSDT', 'UBUSDT', 'HUSDT', 'SYRUPUSDT', 'BANKUSDT', 'SOPHUSDT', 'ASTERUSDT', 'BIOUSDT', 'BMTUSDT', 'HEIUSDT', 'BSVUSDT', 'ZORAUSDT', 'MYXUSDT', 'OPENUSDT', 'GPSUSDT', 'SUPERUSDT', 'ONGUSDT', 'TUTUSDT', 'NEIROUSDT', 'KERNELUSDT', 'MITOUSDT', 'MAVIAUSDT', 'SAHARAUSDT', 'CROSSUSDT', 'XPINUSDT', 'TAUSDT', 'AVAAIUSDT', 'FLOCKUSDT', 'CVCUSDT']
Oct 09 03:02:59 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 03:02:59 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 03:04:38 Trading-Agent python[2005927]: [DRY_RUN] CLOSE OPENUSDT @ 0.10880382301762975 (stop_loss)
Oct 09 03:04:38 Trading-Agent python[2005927]: [referto] OPENUSDT gen_46f0717f: a favore fino a 0.86R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 09 03:04:43 Trading-Agent python[2005927]: [learning] filtrati 21/417 trade (esplorativi: 18 · short_duration: 3)
Oct 09 03:04:43 Trading-Agent python[2005927]: [main] pesi ricalcolati: 239 coppie strat×regime da 417 trade (30g)
Oct 09 03:04:44 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 09 03:04:45 Trading-Agent python[2005927]: [price_stream] connesso · 9 simboli · wss://fstream.binance.com/stream?streams=0gusdt@bookTicker/catiusdt@bookTicker/flockusdt@bookTicker/orcausdt@bookTicker/pumpusdt@bookTicker/sophusdt@bookTicker/superusdt@bookTicker/vetusdt@bookTicker/zorausdt@bookTicker
Oct 09 03:04:45 Trading-Agent python[2005927]: [referti] 10 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 09 03:06:55 Trading-Agent python[2005927]: [DRY_RUN] SCALE-OUT 1.8414 ORCAUSDT @ 2.477997653723956 (netto +0.3160, residuo 4.2967)
Oct 09 03:17:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 03:17:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 03:19:59 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 09 03:20:05 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 09 03:33:08 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 03:33:08 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 09 03:34:12 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 14521 (rifiutati 10793 · controllo 1426 · registro 1351 · trade 512 · pesi 151 · memoria 95 · deriva 59 · referti 59) — quota gratuita 50000/giorno
Oct 09 03:34:12 Trading-Agent python[2005927]: [learning] filtrati 21/417 trade (esplorativi: 18 · short_duration: 3)
Oct 09 03:34:12 Trading-Agent python[2005927]: [main] pesi ricalcolati: 239 coppie strat×regime da 417 trade (30g)
Oct 09 03:34:13 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 09 03:34:13 Trading-Agent python[2005927]: [referti] 10 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 09 03:34:15 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 2 anomalie, 1721 ms
Oct 09 03:35:28 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 09 03:35:28 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
```
