# 0337-log-dopo-riavvio.req

_eseguito: 2026-09-28 20:02 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 28 16:03:12 Trading-Agent python[1807149]: [DRY_RUN] CLOSE UBUSDT @ 0.14569 (trailing_stop)
Sep 28 16:03:15 Trading-Agent python[1807149]: [learning] filtrati 3/158 trade (esplorativi: 3)
Sep 28 16:03:16 Trading-Agent python[1807149]: [main] pesi ricalcolati: 102 coppie strat×regime da 158 trade (30g)
Sep 28 16:03:17 Trading-Agent python[1807149]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 16:03:18 Trading-Agent python[1807149]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=phausdt@bookTicker/theusdt@bookTicker
Sep 28 16:06:22 Trading-Agent python[1807149]: [DRY_RUN] CLOSE THEUSDT @ 0.07763500000000001 (trailing_stop)
Sep 28 16:06:26 Trading-Agent python[1807149]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 28 16:06:26 Trading-Agent python[1807149]: [learning] filtrati 3/159 trade (esplorativi: 3)
Sep 28 16:06:26 Trading-Agent python[1807149]: [main] pesi ricalcolati: 103 coppie strat×regime da 159 trade (30g)
Sep 28 16:06:27 Trading-Agent python[1807149]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 16:06:29 Trading-Agent python[1807149]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=phausdt@bookTicker
Sep 28 16:15:08 Trading-Agent python[1807149]: [DRY_RUN] CLOSE PHAUSDT @ 0.059605000000000005 (trailing_stop)
Sep 28 16:17:19 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 16:17:19 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 16:17:22 Trading-Agent python[1807149]: [learning] filtrati 4/160 trade (esplorativi: 4)
Sep 28 16:17:22 Trading-Agent python[1807149]: [main] pesi ricalcolati: 103 coppie strat×regime da 160 trade (30g)
Sep 28 16:17:23 Trading-Agent python[1807149]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 16:21:56 Trading-Agent python[1807149]: [firebase] letture ultime 24 h: 3155 (rifiutati 1682 · controllo 558 · registro 549 · trade 192 · pesi 62 · memoria 37 · deriva 24 · referti 24) — quota gratuita 50000/giorno
Sep 28 16:21:56 Trading-Agent python[1807149]: [learning] filtrati 4/160 trade (esplorativi: 4)
Sep 28 16:21:56 Trading-Agent python[1807149]: [main] pesi ricalcolati: 103 coppie strat×regime da 160 trade (30g)
Sep 28 16:21:57 Trading-Agent python[1807149]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 16:21:59 Trading-Agent python[1807149]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1741 ms
Sep 28 16:32:13 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 16:32:13 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 16:32:46 Trading-Agent python[1807149]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 28 16:32:49 Trading-Agent python[1807149]: [rifiutati] 6 segnali rifiutati valutati
Sep 28 16:47:33 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 16:47:33 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 16:47:34 Trading-Agent python[1807149]: [selettore] PROMUSDT gen_cd5c842f long p=0.59 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 28 16:47:34 Trading-Agent python[1807149]: [DRY_RUN] OPEN long PROMUSDT qty=11.7276 @ 6.271 lev=2.0x SL=6.1441 TP=6.4614
Sep 28 16:47:34 Trading-Agent python[1807149]: [declassata] PROMUSDT gen_cd5c842f long size x0.25
Sep 28 16:47:36 Trading-Agent python[1807149]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker
Sep 28 16:47:43 Trading-Agent python[1807149]: [ai-shadow] ok in 8.6s · 783+406 token
Sep 28 16:48:16 Trading-Agent python[1807149]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 28 16:57:26 Trading-Agent python[1807149]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 17:02:39 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 17:02:39 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 17:17:18 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 17:17:18 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 17:22:26 Trading-Agent python[1807149]: [firebase] letture ultime 24 h: 3544 (rifiutati 1934 · controllo 620 · registro 609 · trade 196 · pesi 65 · memoria 41 · deriva 25 · referti 25) — quota gratuita 50000/giorno
Sep 28 17:22:26 Trading-Agent python[1807149]: [learning] filtrati 4/160 trade (esplorativi: 4)
Sep 28 17:22:26 Trading-Agent python[1807149]: [main] pesi ricalcolati: 103 coppie strat×regime da 160 trade (30g)
Sep 28 17:22:27 Trading-Agent python[1807149]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 17:22:29 Trading-Agent python[1807149]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1810 ms
Sep 28 17:32:22 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 17:32:22 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 17:47:22 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 17:47:22 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 18:02:18 Trading-Agent python[1807149]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 18:02:18 Trading-Agent python[1807149]:   return query.where(field_path, op_string, value)
Sep 28 18:05:55 Trading-Agent python[1807149]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 18:11:01 Trading-Agent python[1807149]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 18:13:50 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 28 18:13:50 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 28 18:13:50 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 28 18:13:50 Trading-Agent systemd[1]: trading-bot.service: Consumed 33min 17.307s CPU time.
Sep 28 18:13:50 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 28 18:13:51 Trading-Agent python[1827804]: [firebase] connesso (Firestore + RTDB)
Sep 28 18:13:52 Trading-Agent python[1827804]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['PROMUSDT']
Sep 28 18:13:52 Trading-Agent python[1827804]: [main] avvio bot @ 2026-09-28T18:13:52.556378+00:00 DRY_RUN=True
Sep 28 18:13:53 Trading-Agent python[1827804]: [main] equity riconciliata: 931.39 (base 1000.00 + realizzato -68.61 + fette aperte +0.00)
Sep 28 18:13:53 Trading-Agent python[1827804]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 28 18:13:53 Trading-Agent python[1827804]: [selettore] modello caricato: 81490 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-09-28T06:19:25.022249+00:00 -> solo ombra, non decide
Sep 28 18:13:55 Trading-Agent python[1827804]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker
Sep 28 18:13:55 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 18:13:55 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 18:13:55 Trading-Agent python[1827804]: [firebase] letture ultime 24 h: 230 (trade 160 · rifiutati 63 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Sep 28 18:13:55 Trading-Agent python[1827804]: /root/agentic_trading_system/bot/core/firebase_client.py:409: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 18:13:55 Trading-Agent python[1827804]:   q = q.where(order_by, "<=", max_value)
Sep 28 18:13:56 Trading-Agent python[1827804]: [learning] filtrati 4/160 trade (esplorativi: 4)
Sep 28 18:13:56 Trading-Agent python[1827804]: [main] pesi ricalcolati: 103 coppie strat×regime da 160 trade (30g)
Sep 28 18:13:57 Trading-Agent python[1827804]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 18:13:59 Trading-Agent python[1827804]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1794 ms
Sep 28 18:14:02 Trading-Agent python[1827804]: [main] market scan...
Sep 28 18:16:10 Trading-Agent python[1827804]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 28 18:16:10 Trading-Agent python[1827804]: [main] valutate 66 coin validate (66 nel registro): ['QUSDT', 'SYRUPUSDT', 'XPLUSDT', 'JASMYUSDT', 'SUPERUSDT', 'BULLAUSDT', 'ZORAUSDT', 'HUMAUSDT', 'ORCAUSDT', 'ARCUSDT', 'RAYSOLUSDT', 'TRUMPUSDT', 'NEIROUSDT', 'JUPUSDT', 'USELESSUSDT', 'ENAUSDT', 'VETUSDT', 'CROSSUSDT', 'SKYAIUSDT', 'PENGUUSDT', 'SUIUSDT', 'GALAUSDT', 'HEIUSDT', 'SPXUSDT', 'SEIUSDT', 'THEUSDT', 'PLUMEUSDT', 'AIOUSDT', 'DOTUSDT', 'GPSUSDT', 'FLOCKUSDT', 'PROMUSDT', 'PHAUSDT', 'CVCUSDT', 'PNUTUSDT', 'WALUSDT', 'AXSUSDT', 'MUBARAKUSDT', 'RENDERUSDT', 'UBUSDT', 'STEEMUSDT', 'TUTUSDT', 'SOPHUSDT', 'STXUSDT', 'EPICUSDT', 'BMTUSDT', 'SAHARAUSDT', 'AVAAIUSDT', 'ZKUSDT', 'OPENUSDT', 'TAUSDT', 'B2USDT', 'PUNDIXUSDT', 'MITOUSDT', 'HOMEUSDT', 'FORMUSDT', 'HEMIUSDT', 'DEXEUSDT', 'BANKUSDT', 'RSRUSDT', 'MTLUSDT', 'ATOMUSDT', 'ONGUSDT', 'GRIFFAINUSDT', 'BTRUSDT', 'TSTUSDT']
Sep 28 18:20:58 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 18:20:58 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 18:44:10 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 18:44:10 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 18:44:13 Trading-Agent python[1827804]: [rifiutati] 1 segnali rifiutati valutati
Sep 28 18:59:24 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 18:59:24 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 19:14:18 Trading-Agent python[1827804]: [firebase] letture ultime 24 h: 551 (rifiutati 253 · trade 164 · controllo 62 · registro 59 · memoria 5 · pesi 4 · selettore 2 · deriva 1) — quota gratuita 50000/giorno
Sep 28 19:14:18 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 19:14:18 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 19:14:18 Trading-Agent python[1827804]: [learning] filtrati 4/160 trade (esplorativi: 4)
Sep 28 19:14:18 Trading-Agent python[1827804]: [main] pesi ricalcolati: 103 coppie strat×regime da 160 trade (30g)
Sep 28 19:14:19 Trading-Agent python[1827804]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 19:14:21 Trading-Agent python[1827804]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1708 ms
Sep 28 19:14:57 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 19:14:57 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 19:30:18 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 19:30:18 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 19:47:15 Trading-Agent python[1827804]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 19:47:15 Trading-Agent python[1827804]:   return query.where(field_path, op_string, value)
Sep 28 20:00:25 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 28 20:00:25 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 28 20:00:25 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 28 20:00:25 Trading-Agent systemd[1]: trading-bot.service: Consumed 1min 58.646s CPU time.
Sep 28 20:00:25 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 28 20:00:27 Trading-Agent python[1830204]: [firebase] connesso (Firestore + RTDB)
Sep 28 20:00:28 Trading-Agent python[1830204]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['PROMUSDT']
Sep 28 20:00:28 Trading-Agent python[1830204]: [main] avvio bot @ 2026-09-28T20:00:28.338895+00:00 DRY_RUN=True
Sep 28 20:00:28 Trading-Agent python[1830204]: [main] equity riconciliata: 931.39 (base 1000.00 + realizzato -68.61 + fette aperte +0.00)
Sep 28 20:00:29 Trading-Agent python[1830204]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 28 20:00:29 Trading-Agent python[1830204]: [selettore] modello caricato: 81490 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-09-28T06:19:25.022249+00:00 -> solo ombra, non decide
Sep 28 20:00:30 Trading-Agent python[1830204]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker
Sep 28 20:00:31 Trading-Agent python[1830204]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 28 20:00:31 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 20:00:31 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 28 20:00:31 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 230 (trade 160 · rifiutati 63 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Sep 28 20:00:31 Trading-Agent python[1830204]: /root/agentic_trading_system/bot/core/firebase_client.py:409: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 20:00:31 Trading-Agent python[1830204]:   q = q.where(order_by, "<=", max_value)
Sep 28 20:00:32 Trading-Agent python[1830204]: [benchmark] BTC all'inizio del paper: 75734.00 (candela 1h delle 2026-09-16 16:00 UTC)
Sep 28 20:00:32 Trading-Agent python[1830204]: [learning] filtrati 4/160 trade (esplorativi: 4)
Sep 28 20:00:32 Trading-Agent python[1830204]: [main] pesi ricalcolati: 103 coppie strat×regime da 160 trade (30g)
Sep 28 20:00:33 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 20:00:35 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1706 ms
Sep 28 20:00:38 Trading-Agent python[1830204]: [main] market scan...
```
