# 0295-controllo-27set-log-bot.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 27 01:29:33 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 01:29:35 Trading-Agent python[1733042]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1427 ms
Sep 27 01:36:20 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 01:36:20 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 01:39:31 Trading-Agent python[1733042]: [DRY_RUN] SCALE-OUT 8.7598 PROMUSDT @ 6.08568990872924 (netto +2.0445, residuo 20.4395)
Sep 27 01:47:49 Trading-Agent python[1733042]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 27 01:51:31 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 01:51:31 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 02:06:42 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 02:06:42 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 02:21:55 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 02:21:55 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 02:29:49 Trading-Agent python[1733042]: [learning] filtrati 1/106 trade (esplorativi: 1)
Sep 27 02:29:50 Trading-Agent python[1733042]: [main] pesi ricalcolati: 67 coppie strat×regime da 106 trade (30g)
Sep 27 02:29:50 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 02:29:52 Trading-Agent python[1733042]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1630 ms
Sep 27 02:32:29 Trading-Agent python[1733042]: [selettore] AVAAIUSDT gen_e50a9211 long p=0.62 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 27 02:32:29 Trading-Agent python[1733042]: [DRY_RUN] OPEN long AVAAIUSDT qty=9216.9643 @ 0.010057 lev=1.0x SL=0.0100 TP=0.0103
Sep 27 02:32:36 Trading-Agent python[1733042]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker/dexeusdt@bookTicker/promusdt@bookTicker/vetusdt@bookTicker/xplusdt@bookTicker
Sep 27 02:32:40 Trading-Agent python[1733042]: [ai-shadow] ok in 10.7s · 785+552 token
Sep 27 02:36:55 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 02:36:55 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 02:47:28 Trading-Agent python[1733042]: [selettore] JUPUSDT gen_bb762669 short p=0.68 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 27 02:47:28 Trading-Agent python[1733042]: [DRY_RUN] OPEN short JUPUSDT qty=271.3554 @ 0.3416 lev=1.0x SL=0.3469 TP=0.3337
Sep 27 02:47:34 Trading-Agent python[1733042]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker/dexeusdt@bookTicker/jupusdt@bookTicker/promusdt@bookTicker/vetusdt@bookTicker/xplusdt@bookTicker
Sep 27 02:47:36 Trading-Agent python[1733042]: [ai-shadow] ok in 8.3s · 780+430 token
Sep 27 02:52:26 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 02:52:26 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 03:03:01 Trading-Agent python[1733042]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 27 03:06:15 Trading-Agent python[1733042]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 27 03:07:53 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 03:07:53 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 03:23:20 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 03:23:20 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 03:30:19 Trading-Agent python[1733042]: [learning] filtrati 1/106 trade (esplorativi: 1)
Sep 27 03:30:19 Trading-Agent python[1733042]: [main] pesi ricalcolati: 67 coppie strat×regime da 106 trade (30g)
Sep 27 03:30:20 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 03:30:21 Trading-Agent python[1733042]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1475 ms
Sep 27 03:32:27 Trading-Agent python[1733042]: [rifiuto] XPLUSDT gen_e59ad90b long: posizione gia' aperta su questa coin
Sep 27 03:32:38 Trading-Agent python[1733042]: [ai-shadow] ok in 10.4s · 783+456 token
Sep 27 03:38:30 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 03:38:30 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 03:53:30 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 03:53:30 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 04:08:56 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 04:08:56 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 04:20:05 Trading-Agent python[1733042]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 27 04:24:24 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 04:24:24 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 04:27:06 Trading-Agent python[1733042]: [main] market scan...
Sep 27 04:29:15 Trading-Agent python[1733042]: [scanner] 2 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 27 04:29:15 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 04:29:15 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 04:29:15 Trading-Agent python[1733042]: [main] valutate 68 coin validate (68 nel registro): ['JTOUSDT', 'STXUSDT', 'PHAUSDT', 'SCRUSDT', 'FORMUSDT', 'EGLDUSDT', 'MUBARAKUSDT', 'HUMAUSDT', 'RAYSOLUSDT', 'GRIFFAINUSDT', 'USELESSUSDT', 'TRUMPUSDT', 'B2USDT', 'CROSSUSDT', 'JUPUSDT', 'ENAUSDT', 'JASMYUSDT', 'ZORAUSDT', 'GALAUSDT', 'NEIROUSDT', 'AVAAIUSDT', 'XMRUSDT', 'XPLUSDT', 'ATOMUSDT', 'THEUSDT', 'SOLUSDT', 'PROMUSDT', 'BICOUSDT', 'HEIUSDT', 'SUIUSDT', 'MTLUSDT', 'SOPHUSDT', 'VETUSDT', 'AXSUSDT', 'XRPUSDT', 'QUSDT', 'PENGUUSDT', 'ARCUSDT', 'SYRUPUSDT', 'DOTUSDT', 'PLUMEUSDT', 'TUTUSDT', 'SPXUSDT', 'HEMIUSDT', 'BULLAUSDT', 'PNUTUSDT', 'OPENUSDT', 'FLOCKUSDT', 'EPICUSDT', 'PUNDIXUSDT', 'BTRUSDT', 'SEIUSDT', 'SAHARAUSDT', 'RENDERUSDT', 'HOMEUSDT', 'BANKUSDT', 'ZKUSDT', 'RSRUSDT', 'ONGUSDT', 'WALUSDT', 'MITOUSDT', 'DEXEUSDT', 'SUPERUSDT', 'ORCAUSDT', 'GPSUSDT', 'SKYAIUSDT', 'TAUSDT', 'TSTUSDT']
Sep 27 04:30:20 Trading-Agent python[173

[... 1391 caratteri omessi (testa e coda conservate) ...]

42]: [learning] filtrati 1/107 trade (esplorativi: 1)
Sep 27 04:35:22 Trading-Agent python[1733042]: [main] pesi ricalcolati: 68 coppie strat×regime da 107 trade (30g)
Sep 27 04:35:23 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 04:35:25 Trading-Agent python[1733042]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker/dexeusdt@bookTicker/jupusdt@bookTicker/promusdt@bookTicker/xplusdt@bookTicker
Sep 27 04:41:14 Trading-Agent python[1733042]: [DRY_RUN] CLOSE AVAAIUSDT @ 0.009970649489392708 (stop_loss)
Sep 27 04:41:14 Trading-Agent python[1733042]: [referto] AVAAIUSDT gen_e50a9211: a favore fino a 0.45R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Sep 27 04:41:21 Trading-Agent python[1733042]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/jupusdt@bookTicker/promusdt@bookTicker/xplusdt@bookTicker
Sep 27 04:41:26 Trading-Agent python[1733042]: [learning] filtrati 1/108 trade (esplorativi: 1)
Sep 27 04:41:26 Trading-Agent python[1733042]: [main] pesi ricalcolati: 69 coppie strat×regime da 108 trade (30g)
Sep 27 04:41:27 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 04:47:23 Trading-Agent python[1733042]: [selettore] MITOUSDT gen_8b91ba18 long p=0.54 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 27 04:47:23 Trading-Agent python[1733042]: [DRY_RUN] OPEN long MITOUSDT qty=5748.8817 @ 0.01608 lev=1.0x SL=0.0159 TP=0.0165
Sep 27 04:47:29 Trading-Agent python[1733042]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/jupusdt@bookTicker/mitousdt@bookTicker/promusdt@bookTicker/xplusdt@bookTicker
Sep 27 04:47:41 Trading-Agent python[1733042]: [ai-shadow] ok in 9.8s · 783+498 token
Sep 27 04:56:42 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 04:56:42 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 05:09:00 Trading-Agent python[1733042]: [DRY_RUN] CLOSE JUPUSDT @ 0.34014750000000005 (trailing_stop)
Sep 27 05:09:03 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 05:09:03 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 05:09:04 Trading-Agent python[1733042]: [learning] filtrati 1/109 trade (esplorativi: 1)
Sep 27 05:09:04 Trading-Agent python[1733042]: [main] pesi ricalcolati: 70 coppie strat×regime da 109 trade (30g)
Sep 27 05:09:05 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 05:09:07 Trading-Agent python[1733042]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/mitousdt@bookTicker/promusdt@bookTicker/xplusdt@bookTicker
Sep 27 05:24:29 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 05:24:29 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 05:26:06 Trading-Agent python[1733042]: [DRY_RUN] CLOSE MITOUSDT @ 0.01618 (trailing_stop)
Sep 27 05:26:10 Trading-Agent python[1733042]: [learning] filtrati 1/110 trade (esplorativi: 1)
Sep 27 05:26:10 Trading-Agent python[1733042]: [main] pesi ricalcolati: 71 coppie strat×regime da 110 trade (30g)
Sep 27 05:26:11 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 05:26:13 Trading-Agent python[1733042]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/promusdt@bookTicker/xplusdt@bookTicker
Sep 27 05:33:04 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 05:33:04 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 05:33:05 Trading-Agent python[1733042]: [learning] filtrati 1/110 trade (esplorativi: 1)
Sep 27 05:33:05 Trading-Agent python[1733042]: [main] pesi ricalcolati: 71 coppie strat×regime da 110 trade (30g)
Sep 27 05:33:06 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 05:33:08 Trading-Agent python[1733042]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1626 ms
Sep 27 05:37:20 Trading-Agent python[1733042]: [DRY_RUN] CLOSE PROMUSDT @ 6.2005 (scale_out)
Sep 27 05:37:23 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 05:37:23 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 05:37:24 Trading-Agent python[1733042]: [learning] filtrati 1/111 trade (esplorativi: 1)
Sep 27 05:37:24 Trading-Agent python[1733042]: [main] pesi ricalcolati: 71 coppie strat×regime da 111 trade (30g)
Sep 27 05:37:25 Trading-Agent python[1733042]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5) | gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)
Sep 27 05:37:27 Trading-Agent python[1733042]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/xplusdt@bookTicker
Sep 27 05:47:27 Trading-Agent python[1733042]: [selettore] SPXUSDT gen_d53c153b short p=0.70 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 27 05:47:27 Trading-Agent python[1733042]: [DRY_RUN] OPEN short SPXUSDT qty=205.7130 @ 0.4509 lev=1.0x SL=0.4588 TP=0.4352
Sep 27 05:47:33 Trading-Agent python[1733042]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/spxusdt@bookTicker/xplusdt@bookTicker
Sep 27 05:47:34 Trading-Agent python[1733042]: [ai-shadow] ok in 7.3s · 781+372 token
Sep 27 05:52:49 Trading-Agent python[1733042]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 27 05:52:49 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 05:52:49 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 06:02:24 Trading-Agent python[1733042]: [selettore] USELESSUSDT gen_c0fd1d91 short p=0.70 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 27 06:02:24 Trading-Agent python[1733042]: [DRY_RUN] OPEN short USELESSUSDT qty=323.3944 @ 0.28682 lev=1.0x SL=0.2938 TP=0.2728
Sep 27 06:02:33 Trading-Agent python[1733042]: [ai-shadow] ok in 8.8s · 787+464 token
Sep 27 06:02:33 Trading-Agent python[1733042]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/spxusdt@bookTicker/uselessusdt@bookTicker/xplusdt@bookTicker
Sep 27 06:04:06 Trading-Agent python[1733042]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 27 06:07:50 Trading-Agent python[1733042]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 27 06:07:50 Trading-Agent python[1733042]:   return query.where(field_path, op_string, value)
Sep 27 06:10:29 Trading-Agent python[1733042]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
```
