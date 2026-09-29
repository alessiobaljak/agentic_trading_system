# 0352-log-dopo-foto.req

_eseguito: 2026-09-29 08:13 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 29 05:02:32 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:06:09 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 3511 (rifiutati 2006 · registro 572 · controllo 558 · trade 211 · pesi 57 · memoria 37 · deriva 20 · referti 20) — quota gratuita 50000/giorno
Sep 29 05:06:09 Trading-Agent python[1830204]: [learning] filtrati 5/171 trade (esplorativi: 5)
Sep 29 05:06:10 Trading-Agent python[1830204]: [main] pesi ricalcolati: 110 coppie strat×regime da 171 trade (30g)
Sep 29 05:06:11 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:06:13 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1653 ms
Sep 29 05:08:20 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 05:12:30 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:12:30 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:12:32 Trading-Agent python[1830204]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 29 05:17:24 Trading-Agent python[1830204]: [selettore] MUBARAKUSDT gen_cf6a181e short p=0.66 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 29 05:17:24 Trading-Agent python[1830204]: [DRY_RUN] OPEN short MUBARAKUSDT qty=549.3858 @ 0.06356 lev=1.0x SL=0.0651 TP=0.0598
Sep 29 05:17:24 Trading-Agent python[1830204]: [esplorativa] MUBARAKUSDT gen_cf6a181e short size x0.25
Sep 29 05:17:33 Trading-Agent python[1830204]: [ai-shadow] ok in 9.1s · 782+419 token
Sep 29 05:17:34 Trading-Agent python[1830204]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/orcausdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 05:27:31 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:27:31 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:34:01 Trading-Agent python[1830204]: [DRY_RUN] CLOSE ORCAUSDT @ 1.62425 (trailing_stop)
Sep 29 05:34:02 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:34:02 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:34:04 Trading-Agent python[1830204]: [learning] filtrati 5/172 trade (esplorativi: 5)
Sep 29 05:34:04 Trading-Agent python[1830204]: [main] pesi ricalcolati: 111 coppie strat×regime da 172 trade (30g)
Sep 29 05:34:05 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:34:07 Trading-Agent python[1830204]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 05:34:35 Trading-Agent python[1830204]: [DRY_RUN] CLOSE THEUSDT @ 0.078445 (trailing_stop)
Sep 29 05:34:38 Trading-Agent python[1830204]: [learning] filtrati 5/173 trade (esplorativi: 5)
Sep 29 05:34:38 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 173 trade (30g)
Sep 29 05:34:39 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:34:44 Trading-Agent python[1830204]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/xplusdt@bookTicker
Sep 29 05:35:41 Trading-Agent python[1830204]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.062427500000000004 (trailing_stop)
Sep 29 05:35:44 Trading-Agent python[1830204]: [learning] filtrati 6/174 trade (esplorativi: 6)
Sep 29 05:35:44 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 174 trade (30g)
Sep 29 05:35:45 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:35:48 Trading-Agent python[1830204]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=xplusdt@bookTicker
Sep 29 05:47:37 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:47:37 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:02:40 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 06:02:40 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:03:10 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 06:06:16 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 3946 (rifiutati 2274 · registro 645 · controllo 620 · trade 216 · pesi 68 · memoria 41 · deriva 24 · referti 24) — quota gratuita 50000/giorno
Sep 29 06:06:16 Trading-Agent python[1830204]: [learning] filtrati 6/174 trade (esplorativi: 6)
Sep 29 06:06:16 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 174 trade (30g)
Sep 29 06:06:17 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 06:06:19 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1747 ms
Sep 29 06:07:25 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 06:17:46 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 06:17:46 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:17:48 Trading-Agent python[1830204]: [selettore] SEIUSDT gen_4f890271 short p=0.61 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 29 06:17:48 Trading-Agent python[1830204]: [DRY_RUN] OPEN short SEIUSDT qty=433.9387 @ 0.07482 lev=1.0x SL=0.0768 TP=0.0719
Sep 29 06:17:48 Trading-Agent python[1830204]: [declassata] SEIUSDT gen_4f890271 short size x0.25
Sep 29 06:17:49 Trading-Agent python[1830204]: [selettore] FLOCKUSDT gen_c5194ce4 short p=0.77 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 29 06:17:49 Trading-Agent python[1830204]: [DRY_RUN] OPEN short FLOCKUSDT qty=890.2083 @ 0.06405 lev=1.0x SL=0.0655 TP=0.0612
Sep 29 06:17:49 Trading-Agent python[1830204]: [declassata] FLOCKUSDT gen_c5194ce4 short size x0.25
Sep 29 06:17:54 Trading-Agent python[1830204]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=flockusdt@bookTicker/seiusdt@bookTicker/xplusdt@bookTicker
Sep 29 06:18:06 Trading-Agent python[1830204]: [ai-shadow] ok in 9.1s · 830+450 token
Sep 29 06:21:12 Trading-Agent python[1830204]: [DRY_RUN] CLOSE XPLUSDT @ 0.0974575 (trailing_stop)
Sep 29 06:21:16 Trading-Agent python[1830204]: [learning] filtrati 6/175 trade (esplorativi: 6)
Sep 29 06:21:16 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 175 trade (30g)
Sep 29 06:21:17 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 06:21:21 Trading-Agent python[1830204]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=flockusdt@bookTicker/seiusdt@bookTicker
Sep 29 06:32:47 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 06:32:47 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:36:26 Trading-Agent python[1830204]: [rifiutati] 1 segnali rifiutati valutati
Sep 29 06:47:24 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 06:47:24 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:47:24 Trading-Agent python[1830204]: [rifiuto] FLOCKUSDT gen_c5194ce4 short: posizione gia' aperta su questa coin
Sep 29 06:47:34 Trading-Agent python[1830204]: [ai-shadow] ok in 9.2s · 788+422 token
Sep 29 07:02:40 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 07:02:40 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 07:06:16 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 4223 (rifiutati 2410 · registro 704 · controllo 682 · trade 220 · pesi 73 · memoria 45 · deriva 26 · referti 26) — quota gratuita 50000/giorno
Sep 29 07:06:16 Trading-Agent python[1830204]: [learning] filtrati 6/175 trade (esplorativi: 6)
Sep 29 07:06:16 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 175 trade (30g)
Sep 29 07:06:17 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 07:06:19 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1879 ms
Sep 29 07:06:55 Trading-Agent python[1830204]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 29 07:06:55 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 07:06:55 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 07:07:26 Trading-Agent python[1830204]: [selettore] modello caricato: 87490 righe, soglia 0.50, verdetto NON BATTE, stato ombra, generato 2026-09-29T06:17:31.865034+00:00 -> solo ombra, non decide
Sep 29 07:17:27 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 07:17:27 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 07:32:32 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 07:32:32 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 07:47:43 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 07:47:43 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 08:02:20 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 08:02:20 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 08:03:21 Trading-Agent python[1830204]: [main] market scan...
Sep 29 08:05:26 Trading-Agent python[1830204]: [scanner] 2 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 29 08:05:26 Trading-Agent python[1830204]: [main] valutate 69 coin validate (69 nel registro): ['SYRUPUSDT', 'QUSDT', 'PHAUSDT', 'GALAUSDT', 'DOTUSDT', 'XPLUSDT', 'TUTUSDT', 'AXSUSDT', 'TRUMPUSDT', 'BMTUSDT', 'SAHARAUSDT', 'MTLUSDT', 'RSRUSDT', 'SUIUSDT', 'RENDERUSDT', 'BULLAUSDT', 'NEIROUSDT', 'MUBARAKUSDT', 'PENGUUSDT', 'UBUSDT', 'BANKUSDT', 'ENAUSDT', 'ATOMUSDT', 'VETUSDT', 'STXUSDT', 'JASMYUSDT', 'TSTUSDT', 'ONGUSDT', 'CROSSUSDT', 'OPENUSDT', 'FLOCKUSDT', 'GPSUSDT', 'EPICUSDT', 'HUMAUSDT', 'FORMUSDT', 'ZKUSDT', 'SEIUSDT', 'ARCUSDT', 'USELESSUSDT', 'CVCUSDT', 'SPXUSDT', 'MITOUSDT', 'JUPUSDT', 'WALUSDT', 'PNUTUSDT', 'PUNDIXUSDT', 'SUPERUSDT', 'DEXEUSDT', 'XPINUSDT', 'THEUSDT', 'HEIUSDT', 'SOPHUSDT', 'STEEMUSDT', 'PLUMEUSDT', 'ZORAUSDT', 'PROMUSDT', 'HOMEUSDT', 'GRIFFAINUSDT', 'AIOUSDT', 'RAYSOLUSDT', 'BTRUSDT', 'HEMIUSDT', 'SKYAIUSDT', 'ORCAUSDT', 'CATIUSDT', 'TAUSDT', 'AVAAIUSDT', 'B2USDT', 'PARTIUSDT']
Sep 29 08:05:57 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 08:06:28 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 4633 (rifiutati 2682 · registro 764 · controllo 744 · trade 224 · pesi 77 · memoria 49 · deriva 27 · referti 27) — quota gratuita 50000/giorno
Sep 29 08:06:28 Trading-Agent python[1830204]: [learning] filtrati 6/175 trade (esplorativi: 6)
Sep 29 08:06:28 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 175 trade (30g)
Sep 29 08:06:29 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 08:06:31 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1659 ms
Sep 29 08:07:36 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 08:07:36 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 08:12:12 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 29 08:12:12 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 29 08:12:12 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 29 08:12:12 Trading-Agent systemd[1]: trading-bot.service: Consumed 25min 48.469s CPU time.
Sep 29 08:12:12 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 29 08:12:14 Trading-Agent python[1858347]: [firebase] connesso (Firestore + RTDB)
Sep 29 08:12:15 Trading-Agent python[1858347]: [execution] ricaricate 2 posizioni aperte da Firebase (no orfani al riavvio): ['FLOCKUSDT', 'SEIUSDT']
Sep 29 08:12:15 Trading-Agent python[1858347]: [main] avvio bot @ 2026-09-29T08:12:15.493815+00:00 DRY_RUN=True
Sep 29 08:12:16 Trading-Agent python[1858347]: [main] equity riconciliata: 933.17 (base 1000.00 + realizzato -66.83 + fette aperte +0.00)
Sep 29 08:12:16 Trading-Agent python[1858347]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 29 08:12:16 Trading-Agent python[1858347]: [selettore] modello caricato: 87490 righe, soglia 0.50, verdetto NON BATTE, stato ombra, generato 2026-09-29T06:17:31.865034+00:00 -> solo ombra, non decide
Sep 29 08:12:18 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 08:12:18 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 29 08:12:18 Trading-Agent python[1858347]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=flockusdt@bookTicker/seiusdt@bookTicker
Sep 29 08:12:18 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 250 (trade 175 · rifiutati 68 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Sep 29 08:12:18 Trading-Agent python[1858347]: /root/agentic_trading_system/bot/core/firebase_client.py:513: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 08:12:18 Trading-Agent python[1858347]:   q = q.where(order_by, "<=", max_value)
Sep 29 08:12:18 Trading-Agent python[1858347]: [learning] filtrati 6/175 trade (esplorativi: 6)
Sep 29 08:12:19 Trading-Agent python[1858347]: [main] pesi ricalcolati: 112 coppie strat×regime da 175 trade (30g)
Sep 29 08:12:19 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 08:12:21 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1630 ms
Sep 29 08:12:22 Trading-Agent python[1858347]: [learning] foto del 2026-09-29 scritta: 199 validate, 112 pesi strategia×regime
Sep 29 08:12:25 Trading-Agent python[1858347]: [main] market scan...
```
