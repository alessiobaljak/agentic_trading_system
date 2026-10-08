# 0542-8ott-mattina-log-bot.req

_eseguito: 2026-10-08 03:47 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 08 00:33:20 Trading-Agent python[2005927]: [selettore] FLOCKUSDT gen_c5194ce4 long p=0.75 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 08 00:33:20 Trading-Agent python[2005927]: [DRY_RUN] OPEN long FLOCKUSDT qty=1513.7165 @ 0.05973 lev=1.0x SL=0.0590 TP=0.0612
Oct 08 00:33:26 Trading-Agent python[2005927]: [price_stream] connesso · 9 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/asterusdt@bookTicker/b2usdt@bookTicker/epicusdt@bookTicker/flockusdt@bookTicker/idusdt@bookTicker/jasmyusdt@bookTicker/mitousdt@bookTicker/stxusdt@bookTicker
Oct 08 00:42:44 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 08 00:42:49 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 00:48:20 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 00:48:20 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 00:48:21 Trading-Agent python[2005927]: [selettore] AXSUSDT gen_b922252e long p=0.64 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 08 00:48:21 Trading-Agent python[2005927]: [DRY_RUN] OPEN long AXSUSDT qty=110.4960 @ 1.231 lev=2.0x SL=1.2179 TP=1.2637
Oct 08 00:48:21 Trading-Agent python[2005927]: [declassata] AXSUSDT gen_b922252e long size x0.25
Oct 08 00:48:28 Trading-Agent python[2005927]: [price_stream] connesso · 10 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/asterusdt@bookTicker/axsusdt@bookTicker/b2usdt@bookTicker/epicusdt@bookTicker/flockusdt@bookTicker/idusdt@bookTicker/jasmyusdt@bookTicker/mitousdt@bookTicker/stxusdt@bookTicker
Oct 08 00:48:55 Trading-Agent python[2005927]: [DRY_RUN] CLOSE FLOCKUSDT @ 0.05984375 (trailing_stop)
Oct 08 00:48:58 Trading-Agent python[2005927]: [learning] filtrati 18/373 trade (esplorativi: 15 · short_duration: 3)
Oct 08 00:48:59 Trading-Agent python[2005927]: [main] pesi ricalcolati: 217 coppie strat×regime da 373 trade (30g)
Oct 08 00:48:59 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 08 00:49:00 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 08 00:49:01 Trading-Agent python[2005927]: [price_stream] connesso · 9 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/asterusdt@bookTicker/axsusdt@bookTicker/b2usdt@bookTicker/epicusdt@bookTicker/idusdt@bookTicker/jasmyusdt@bookTicker/mitousdt@bookTicker/stxusdt@bookTicker
Oct 08 01:03:20 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 01:03:20 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 01:04:30 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 01:18:20 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 01:18:20 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 01:18:21 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 08 01:18:21 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_8e475cd9 short: cooldown dopo stop (11m)
Oct 08 01:18:54 Trading-Agent python[2005927]: [DRY_RUN] CLOSE AXSUSDT @ 1.2179241376993435 (stop_loss)
Oct 08 01:18:54 Trading-Agent python[2005927]: [referto] AXSUSDT gen_b922252e: mai andato a favore (mfe 0.01R): direzione sbagliata
Oct 08 01:19:01 Trading-Agent python[2005927]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/asterusdt@bookTicker/b2usdt@bookTicker/epicusdt@bookTicker/idusdt@bookTicker/jasmyusdt@bookTicker/mitousdt@bookTicker/stxusdt@bookTicker
Oct 08 01:19:03 Trading-Agent python[2005927]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Oct 08 01:19:06 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 08 01:19:06 Trading-Agent python[2005927]: [learning] filtrati 18/374 trade (esplorativi: 15 · short_duration: 3)
Oct 08 01:19:06 Trading-Agent python[2005927]: [main] pesi ricalcolati: 217 coppie strat×regime da 374 trade (30g)
Oct 08 01:19:06 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 08 01:19:07 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 08 01:24:36 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 11888 (rifiutati 8200 · controllo 1426 · registro 1300 · trade 497 · pesi 159 · memoria 94 · deriva 62 · referti 62) — quota gratuita 50000/giorno
Oct 08 01:24:36 Trading-Agent python[2005927]: [learning] filtrati 18/374 trade (esplorativi: 15 · short_duration: 3)
Oct 08 01:24:37 Trading-Agent python[2005927]: [main] pesi ricalcolati: 217 coppie strat×regime da 374 trade (30g)
Oct 08 01:24:37 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 08 01:24:38 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 08 01:24:40 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1787 ms
Oct 08 01:32:58 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 01:32:58 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 01:34:37 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 08 01:34:43 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 01:47:56 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 01:47:56 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 01:56:50 Trading-Agent python[2005927]: [DRY_RUN] SCALE-OUT 31.0357 B2USDT @ 0.4631799514203751 (netto +0.3494, residuo 72.4165)
Oct 08 02:02:54 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 02:02:54 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 02:02:55 Trading-Agent python[2005927]: [panchina] DEXEUSDT gen_fa304106: peso 0.23 -> size x0.25
Oct 08 02:02:58 Trading-Agent python[2005927]: [selettore] DEXEUSDT gen_fa304106 long p=0.65 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 08 02:02:58 Trading-Agent python[2005927]: [DRY_RUN] OPEN long DEXEUSDT qty=11.4597 @ 1.853 lev=1.0x SL=1.8362 TP=1.8783
Oct 08 02:02:58 Trading-Agent python[2005927]: [declassata] DEXEUSDT gen_fa304106 long size x0.25
Oct 08 02:03:04 Trading-Agent python[2

[... 3921 caratteri omessi (testa e coda conservate) ...]

prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 08 02:24:47 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1882 ms
Oct 08 02:33:04 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 02:33:04 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 02:34:12 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 08 02:34:12 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 6 trade paper
Oct 08 02:34:17 Trading-Agent python[2005927]: [rifiutati] 3 segnali rifiutati valutati
Oct 08 02:47:51 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 02:47:51 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 02:49:29 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 08 02:49:33 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 02:51:43 Trading-Agent python[2005927]: [main] market scan...
Oct 08 02:54:19 Trading-Agent python[2005927]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 08 02:54:19 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 02:54:19 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 02:54:19 Trading-Agent python[2005927]: [main] valutate 84 coin validate (84 nel registro): ['JUPUSDT', 'TAUSDT', 'XPINUSDT', 'MUBARAKUSDT', 'PTBUSDT', 'BRUSDT', 'ATOMUSDT', 'RAYSOLUSDT', 'PHAUSDT', 'B2USDT', 'GRIFFAINUSDT', 'AIOUSDT', 'SUIUSDT', 'PUNDIXUSDT', 'TAOUSDT', 'SUPERUSDT', 'PARTIUSDT', 'EPICUSDT', 'MYXUSDT', 'USELESSUSDT', '1000BONKUSDT', 'PNUTUSDT', 'ARCUSDT', 'PLUMEUSDT', 'RENDERUSDT', 'ORCAUSDT', 'PUMPUSDT', 'PENGUUSDT', 'TRUMPUSDT', 'HEMIUSDT', 'AINUSDT', 'SOPHUSDT', 'ENAUSDT', 'GPSUSDT', 'SKYAIUSDT', 'VETUSDT', 'GALAUSDT', 'QUSDT', 'PROMUSDT', 'AXSUSDT', 'IDUSDT', 'ASTERUSDT', 'ZKUSDT', 'OPENUSDT', 'DOTUSDT', 'HOMEUSDT', 'RUNEUSDT', 'JASMYUSDT', 'SEIUSDT', 'XPLUSDT', 'BMTUSDT', 'UBUSDT', 'IDOLUSDT', 'STXUSDT', 'ONGUSDT', 'SPXUSDT', 'CVCUSDT', 'SAHARAUSDT', 'SYRUPUSDT', 'ZORAUSDT', 'TUTUSDT', 'WALUSDT', 'THEUSDT', 'GUNUSDT', 'SCRUSDT', 'CATIUSDT', 'DEXEUSDT', 'HEIUSDT', 'NEIROUSDT', 'AVAAIUSDT', 'HUMAUSDT', 'RSRUSDT', 'MTLUSDT', 'KERNELUSDT', 'BTRUSDT', 'MITOUSDT', 'TSTUSDT', 'BANKUSDT', 'FORMUSDT', 'STEEMUSDT', 'BULLAUSDT', 'CROSSUSDT', 'MAVIAUSDT', 'FLOCKUSDT']
Oct 08 03:03:03 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 03:03:03 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 03:03:03 Trading-Agent python[2005927]: [panchina] ZORAUSDT gen_ceab7f6a: peso 0.46 -> size x0.46
Oct 08 03:03:06 Trading-Agent python[2005927]: [selettore] ZORAUSDT gen_ceab7f6a long p=0.64 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 08 03:03:06 Trading-Agent python[2005927]: [DRY_RUN] OPEN long ZORAUSDT qty=4676.2053 @ 0.0072 lev=1.0x SL=0.0071 TP=0.0075
Oct 08 03:03:06 Trading-Agent python[2005927]: [declassata] ZORAUSDT gen_ceab7f6a long size x0.25
Oct 08 03:03:13 Trading-Agent python[2005927]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/b2usdt@bookTicker/dexeusdt@bookTicker/epicusdt@bookTicker/idusdt@bookTicker/mitousdt@bookTicker/stxusdt@bookTicker/zorausdt@bookTicker
Oct 08 03:04:48 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 03:18:03 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 03:18:03 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 03:18:03 Trading-Agent python[2005927]: [panchina] ZORAUSDT gen_ceab7f6a: peso 0.46 -> size x0.46
Oct 08 03:18:04 Trading-Agent python[2005927]: [selettore] PUMPUSDT gen_13cc61f2 long p=0.66 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 08 03:18:04 Trading-Agent python[2005927]: [DRY_RUN] OPEN long PUMPUSDT qty=14495.7316 @ 0.006222 lev=1.0x SL=0.0060 TP=0.0067
Oct 08 03:18:04 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 08 03:18:10 Trading-Agent python[2005927]: [price_stream] connesso · 9 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/b2usdt@bookTicker/dexeusdt@bookTicker/epicusdt@bookTicker/idusdt@bookTicker/mitousdt@bookTicker/pumpusdt@bookTicker/stxusdt@bookTicker/zorausdt@bookTicker
Oct 08 03:20:18 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 08 03:20:21 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 03:24:50 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 12109 (rifiutati 8456 · controllo 1426 · registro 1308 · trade 492 · pesi 150 · memoria 94 · deriva 57 · referti 57) — quota gratuita 50000/giorno
Oct 08 03:24:50 Trading-Agent python[2005927]: [learning] filtrati 18/376 trade (esplorativi: 15 · short_duration: 3)
Oct 08 03:24:51 Trading-Agent python[2005927]: [main] pesi ricalcolati: 219 coppie strat×regime da 376 trade (30g)
Oct 08 03:24:51 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 08 03:24:52 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 08 03:24:54 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2015 ms
Oct 08 03:33:13 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 08 03:33:13 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 08 03:35:28 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 08 03:35:29 Trading-Agent python[2005927]: [DRY_RUN] CLOSE EPICUSDT @ 0.48114999999999997 (scale_out)
Oct 08 03:35:33 Trading-Agent python[2005927]: [learning] filtrati 18/377 trade (esplorativi: 15 · short_duration: 3)
Oct 08 03:35:34 Trading-Agent python[2005927]: [main] pesi ricalcolati: 219 coppie strat×regime da 377 trade (30g)
Oct 08 03:35:34 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 08 03:35:35 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 08 03:35:36 Trading-Agent python[2005927]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/b2usdt@bookTicker/dexeusdt@bookTicker/idusdt@bookTicker/mitousdt@bookTicker/pumpusdt@bookTicker/stxusdt@bookTicker/zorausdt@bookTicker
```
