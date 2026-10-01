# 0402-1ott-log-bot.req

_eseguito: 2026-10-01 09:11 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 01 05:20:38 Trading-Agent python[1927496]: [learning] filtrati 8/204 trade (esplorativi: 8)
Oct 01 05:20:38 Trading-Agent python[1927496]: [main] pesi ricalcolati: 132 coppie strat×regime da 204 trade (30g)
Oct 01 05:20:39 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 05:20:41 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1716 ms
Oct 01 05:32:43 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 05:32:43 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 05:32:45 Trading-Agent python[1927496]: [selettore] JASMYUSDT gen_b2f350ff short p=0.59 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 05:32:45 Trading-Agent python[1927496]: [DRY_RUN] OPEN short JASMYUSDT qty=9564.8314 @ 0.005342 lev=1.0x SL=0.0055 TP=0.0049
Oct 01 05:32:45 Trading-Agent python[1927496]: [declassata] JASMYUSDT gen_b2f350ff short size x0.25
Oct 01 05:32:53 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=jasmyusdt@bookTicker/mitousdt@bookTicker/tstusdt@bookTicker
Oct 01 05:47:28 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 05:47:28 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 05:47:29 Trading-Agent python[1927496]: [selettore] ORCAUSDT gen_cb8176f2 short p=0.64 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 05:47:29 Trading-Agent python[1927496]: [DRY_RUN] OPEN short ORCAUSDT qty=35.6523 @ 1.701 lev=1.0x SL=1.7243 TP=1.6427
Oct 01 05:47:29 Trading-Agent python[1927496]: [declassata] ORCAUSDT gen_cb8176f2 short size x0.25
Oct 01 05:47:29 Trading-Agent python[1927496]: [rifiuto] JASMYUSDT gen_b2f350ff short: posizione gia' aperta su questa coin
Oct 01 05:47:36 Trading-Agent python[1927496]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=jasmyusdt@bookTicker/mitousdt@bookTicker/orcausdt@bookTicker/tstusdt@bookTicker
Oct 01 06:02:20 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 06:02:20 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 06:13:57 Trading-Agent python[1927496]: [DRY_RUN] CLOSE MITOUSDT @ 0.0156246528482692 (stop_loss)
Oct 01 06:13:57 Trading-Agent python[1927496]: [referto] MITOUSDT gen_8b91ba18: a favore fino a 0.62R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 01 06:14:01 Trading-Agent python[1927496]: [learning] filtrati 8/205 trade (esplorativi: 8)
Oct 01 06:14:01 Trading-Agent python[1927496]: [main] pesi ricalcolati: 132 coppie strat×regime da 205 trade (30g)
Oct 01 06:14:02 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 06:14:04 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=jasmyusdt@bookTicker/orcausdt@bookTicker/tstusdt@bookTicker
Oct 01 06:14:32 Trading-Agent python[1927496]: [main] market scan...
Oct 01 06:16:43 Trading-Agent python[1927496]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 01 06:16:43 Trading-Agent python[1927496]: [main] valutate 71 coin validate (71 nel registro): ['STXUSDT', 'JASMYUSDT', 'ORCAUSDT', 'XPLUSDT', 'ENAUSDT', 'HUMAUSDT', 'SCRUSDT', 'SYRUPUSDT', 'SUPERUSDT', 'USELESSUSDT', 'ARCUSDT', 'SKYAIUSDT', 'BULLAUSDT', 'RAYSOLUSDT', 'TAUSDT', 'MUBARAKUSDT', 'HEIUSDT', 'PUNDIXUSDT', 'GPSUSDT', 'SPXUSDT', 'MITOUSDT', 'TUTUSDT', 'PENGUUSDT', 'XPINUSDT', 'BMTUSDT', 'VETUSDT', 'RENDERUSDT', 'ATOMUSDT', 'PLUMEUSDT', 'TRUMPUSDT', 'CROSSUSDT', 'SUIUSDT', 'ZORAUSDT', 'ONGUSDT', 'JUPUSDT', 'PHAUSDT', 'MTLUSDT', 'CVCUSDT', 'SEIUSDT', 'HOMEUSDT', 'DOTUSDT', 'STEEMUSDT', 'ZKUSDT', 'NEIROUSDT', 'GRIFFAINUSDT', 'QUSDT', 'GALAUSDT', 'CATIUSDT', 'FLOCKUSDT', 'SAHARAUSDT', 'AVAAIUSDT', 'SOPHUSDT', 'EPICUSDT', 'PARTIUSDT', 'DEXEUSDT', 'B2USDT', 'PROMUSDT', 'HEMIUSDT', 'WALUSDT', 'UBUSDT', 'OPENUSDT', 'PNUTUSDT', 'THEUSDT', 'BANKUSDT', 'FORMUSDT', 'RSRUSDT', 'IDUSDT', 'AIOUSDT', 'AXSUSDT', 'TSTUSDT', 'BTRUSDT']
Oct 01 06:19:27 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 06:19:27 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 06:21:00 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 4452 (rifiutati 2562 · controllo 744 · registro 716 · trade 266 · pesi 53 · memoria 50 · deriva 18 · referti 18) — quota gratuita 50000/giorno
Oct 01 06:21:00 Trading-Agent python[1927496]: [learning] filtrati 8/205 trade (esplorativi: 8)
Oct 01 06:21:01 Trading-Agent python[1927496]: [main] pesi ricalcolati: 132 coppie strat×regime da 205 trade (30g)
Oct 01 06:21:02 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 06:21:04 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1778 ms
Oct 01 06:29:28 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 06:29:28 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 06:30:05 Trading-Agent python[1927496]: [DRY_RUN] CLOSE ORCAUSDT @ 1.724322818911092 (stop_loss)
Oct 01 06:30:05 Trading-Agent python[1927496]: [referto] ORCAUSDT gen_cb8176f2: a favore fino a 0.41R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
Oct 01 06:30:08 Trading-Agent python[1927496]: [learning] filtrati 8/206 trade (esplorativi: 8)
Oct 01 06:30:09 Trading-Agent python[1927496]: [main] pesi ricalcolati: 133 coppie strat×regime da 206 trade (30g)
Oct 01 06:30:10 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 06:30:12 Trading-Agent python[1927496]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=jasmyusdt@bookTicker/tstusdt@bookTicker
Oct 01 06:45:16 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 06:45:16 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 06:47:35 Trading-Agent python[1927496]: [selettore] BTRUSDT gen_8981d5f2 long p=0.63 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 06:47:35 Trading-Agent python[1927496]: [DRY_RUN] OPEN long BTRUSDT qty=1847.3202 @ 0.05016 lev=1.0x SL=0.0497 TP=0.0509
Oct 01 06:47:35 Trading-Agent python[1927496]: [declassata] BTRUSDT gen_8981d5f2 long size x0.25
Oct 01 06:47:42 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/jasmyusdt@bookTicker/tstusdt@bookTicker
Oct 01 07:00:47 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 07:00:47 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 07:03:35 Trading-Agent python[1927496]: [selettore] modello caricato: 99688 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-10-01T06:18:19.687945+00:00 -> solo ombra, non decide
Oct 01 07:17:49 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 07:17:49 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 07:17:51 Trading-Agent python[1927496]: [selettore] ZORAUSDT gen_ceab7f6a long p=0.65 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 07:17:51 Trading-Agent python[1927496]: [DRY_RUN] OPEN long ZORAUSDT qty=10767.3734 @ 0.007958 lev=1.0x SL=0.0078 TP=0.0083
Oct 01 07:17:51 Trading-Agent python[1927496]: [declassata] ZORAUSDT gen_ceab7f6

[... 115 caratteri omessi (testa e coda conservate) ...]

m.binance.com/stream?streams=btrusdt@bookTicker/jasmyusdt@bookTicker/tstusdt@bookTicker/zorausdt@bookTicker
Oct 01 07:21:04 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 4763 (rifiutati 2734 · controllo 806 · registro 773 · trade 270 · pesi 58 · memoria 54 · deriva 20 · referti 20) — quota gratuita 50000/giorno
Oct 01 07:21:04 Trading-Agent python[1927496]: [learning] filtrati 8/206 trade (esplorativi: 8)
Oct 01 07:21:04 Trading-Agent python[1927496]: [main] pesi ricalcolati: 133 coppie strat×regime da 206 trade (30g)
Oct 01 07:21:05 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 07:21:07 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1808 ms
Oct 01 07:25:54 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 07:26:27 Trading-Agent python[1927496]: [DRY_RUN] CLOSE ZORAUSDT @ 0.007847983001014863 (stop_loss)
Oct 01 07:26:27 Trading-Agent python[1927496]: [referto] ZORAUSDT gen_ceab7f6a: mai andato a favore (mfe 0.00R): direzione sbagliata
Oct 01 07:26:28 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 07:26:28 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 07:26:31 Trading-Agent python[1927496]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 01 07:26:31 Trading-Agent python[1927496]: [learning] filtrati 8/207 trade (esplorativi: 8)
Oct 01 07:26:31 Trading-Agent python[1927496]: [main] pesi ricalcolati: 134 coppie strat×regime da 207 trade (30g)
Oct 01 07:26:32 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 07:26:34 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/jasmyusdt@bookTicker/tstusdt@bookTicker
Oct 01 07:32:29 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 07:32:29 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 07:32:31 Trading-Agent python[1927496]: [selettore] XPLUSDT gen_e59ad90b short p=0.65 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 07:32:31 Trading-Agent python[1927496]: [DRY_RUN] OPEN short XPLUSDT qty=474.7216 @ 0.09586 lev=2.0x SL=0.0980 TP=0.0915
Oct 01 07:32:31 Trading-Agent python[1927496]: [declassata] XPLUSDT gen_e59ad90b short size x0.25
Oct 01 07:32:32 Trading-Agent python[1927496]: [selettore] ENAUSDT gen_bb762669 long p=0.68 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 07:32:32 Trading-Agent python[1927496]: [DRY_RUN] OPEN long ENAUSDT qty=136.5117 @ 0.26506 lev=1.0x SL=0.2564 TP=0.2781
Oct 01 07:32:32 Trading-Agent python[1927496]: [declassata] ENAUSDT gen_bb762669 long size x0.25
Oct 01 07:32:32 Trading-Agent python[1927496]: [rifiuto] BTRUSDT gen_8981d5f2 long: posizione gia' aperta su questa coin
Oct 01 07:32:33 Trading-Agent python[1927496]: [selettore] USELESSUSDT gen_c0fd1d91 long p=0.68 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 07:32:33 Trading-Agent python[1927496]: [DRY_RUN] OPEN long USELESSUSDT qty=184.1326 @ 0.23631 lev=1.0x SL=0.2294 TP=0.2501
Oct 01 07:32:33 Trading-Agent python[1927496]: [declassata] USELESSUSDT gen_c0fd1d91 long size x0.25
Oct 01 07:32:37 Trading-Agent python[1927496]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/enausdt@bookTicker/jasmyusdt@bookTicker/tstusdt@bookTicker/uselessusdt@bookTicker/xplusdt@bookTicker
Oct 01 07:34:09 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 07:47:53 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 07:47:53 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 07:47:53 Trading-Agent python[1927496]: [rifiuto] BTRUSDT gen_8981d5f2 long: posizione gia' aperta su questa coin
Oct 01 07:48:24 Trading-Agent python[1927496]: [DRY_RUN] CLOSE JASMYUSDT @ 0.0054755092913295915 (stop_loss)
Oct 01 07:48:24 Trading-Agent python[1927496]: [referto] JASMYUSDT gen_b2f350ff: mai andato a favore (mfe 0.17R): direzione sbagliata
Oct 01 07:48:31 Trading-Agent python[1927496]: [learning] filtrati 8/208 trade (esplorativi: 8)
Oct 01 07:48:31 Trading-Agent python[1927496]: [main] pesi ricalcolati: 134 coppie strat×regime da 208 trade (30g)
Oct 01 07:48:32 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 07:48:34 Trading-Agent python[1927496]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/enausdt@bookTicker/tstusdt@bookTicker/uselessusdt@bookTicker/xplusdt@bookTicker
Oct 01 08:02:32 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 08:02:32 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 08:03:38 Trading-Agent python[1927496]: [rifiutati] 1 segnali rifiutati valutati
Oct 01 08:17:43 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 08:17:43 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 08:18:50 Trading-Agent python[1927496]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 01 08:21:31 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 5055 (rifiutati 2870 · controllo 868 · registro 838 · trade 276 · pesi 66 · memoria 58 · deriva 23 · referti 23) — quota gratuita 50000/giorno
Oct 01 08:21:31 Trading-Agent python[1927496]: [learning] filtrati 8/208 trade (esplorativi: 8)
Oct 01 08:21:31 Trading-Agent python[1927496]: [main] pesi ricalcolati: 134 coppie strat×regime da 208 trade (30g)
Oct 01 08:21:33 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 08:21:35 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1960 ms
Oct 01 08:32:27 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 08:32:27 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 08:34:39 Trading-Agent python[1927496]: [DRY_RUN] CLOSE USELESSUSDT @ 0.22940382524043834 (stop_loss)
Oct 01 08:34:39 Trading-Agent python[1927496]: [referto] USELESSUSDT gen_c0fd1d91: a favore fino a 0.40R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Oct 01 08:34:40 Trading-Agent python[1927496]: [main] strategia gen_c0fd1d91 in panchina dopo 3 stop consecutivi
Oct 01 08:34:43 Trading-Agent python[1927496]: [learning] filtrati 8/209 trade (esplorativi: 8)
Oct 01 08:34:44 Trading-Agent python[1927496]: [main] pesi ricalcolati: 134 coppie strat×regime da 209 trade (30g)
Oct 01 08:34:45 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 08:34:46 Trading-Agent python[1927496]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/enausdt@bookTicker/tstusdt@bookTicker/xplusdt@bookTicker
Oct 01 08:47:31 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 08:47:31 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 09:02:35 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 09:02:35 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
```
