# 0385-ombra-spenta-log-bot.req

_eseguito: 2026-09-30 18:15 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 30 14:32:36 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 14:32:37 Trading-Agent python[1858347]: [selettore] HUMAUSDT gen_771790b1 short p=0.61 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 30 14:32:37 Trading-Agent python[1858347]: [DRY_RUN] OPEN short HUMAUSDT qty=1407.6280 @ 0.030994 lev=2.0x SL=0.0317 TP=0.0295
Sep 30 14:32:38 Trading-Agent python[1858347]: [declassata] HUMAUSDT gen_771790b1 short size x0.25
Sep 30 14:32:44 Trading-Agent python[1858347]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=humausdt@bookTicker/qusdt@bookTicker
Sep 30 14:32:46 Trading-Agent python[1858347]: [ai-shadow] ok in 7.9s · 782+367 token
Sep 30 14:34:49 Trading-Agent python[1858347]: [DRY_RUN] CLOSE QUSDT @ 0.022161201688231085 (stop_loss)
Sep 30 14:34:49 Trading-Agent python[1858347]: [referto] QUSDT gen_85fadf54: mai andato a favore (mfe 0.01R): direzione sbagliata
Sep 30 14:34:52 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 30 14:34:52 Trading-Agent python[1858347]: [learning] filtrati 7/197 trade (esplorativi: 7)
Sep 30 14:34:53 Trading-Agent python[1858347]: [main] pesi ricalcolati: 128 coppie strat×regime da 197 trade (30g)
Sep 30 14:34:54 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 14:34:58 Trading-Agent python[1858347]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=humausdt@bookTicker
Sep 30 14:47:24 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 14:47:24 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 14:47:26 Trading-Agent python[1858347]: [selettore] UBUSDT gen_fb7d035a long p=0.67 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 30 14:47:26 Trading-Agent python[1858347]: [DRY_RUN] OPEN long UBUSDT qty=396.2080 @ 0.14529 lev=1.0x SL=0.1423 TP=0.1528
Sep 30 14:47:26 Trading-Agent python[1858347]: [declassata] UBUSDT gen_fb7d035a long size x0.25
Sep 30 14:47:34 Trading-Agent python[1858347]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=humausdt@bookTicker/ubusdt@bookTicker
Sep 30 14:47:39 Trading-Agent python[1858347]: [ai-shadow] ok in 12.6s · 1105+737 token
Sep 30 15:02:50 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 15:02:50 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 15:05:27 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 15:06:30 Trading-Agent python[1858347]: [DRY_RUN] CLOSE HUMAUSDT @ 0.031734921082418904 (stop_loss)
Sep 30 15:06:30 Trading-Agent python[1858347]: [referto] HUMAUSDT gen_771790b1: a favore fino a 0.29R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
Sep 30 15:06:36 Trading-Agent python[1858347]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=ubusdt@bookTicker
Sep 30 15:06:42 Trading-Agent python[1858347]: [learning] filtrati 7/198 trade (esplorativi: 7)
Sep 30 15:06:42 Trading-Agent python[1858347]: [main] pesi ricalcolati: 128 coppie strat×regime da 198 trade (30g)
Sep 30 15:06:43 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 15:12:51 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 15:17:38 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 15:17:38 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 15:17:38 Trading-Agent python[1858347]: [rifiuto] HUMAUSDT gen_f1550028 short: cooldown dopo stop (51m)
Sep 30 15:17:50 Trading-Agent python[1858347]: [ai-shadow] ok in 11.2s · 866+603 token
Sep 30 15:21:57 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 15:25:00 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 9521 (rifiutati 5975 · registro 1447 · controllo 1426 · trade 330 · pesi 119 · memoria 94 · deriva 40 · referti 40) — quota gratuita 50000/giorno
Sep 30 15:25:00 Trading-Agent python[1858347]: [learning] filtrati 7/198 trade (esplorativi: 7)
Sep 30 15:25:01 Trading-Agent python[1858347]: [main] pesi ricalcolati: 128 coppie strat×regime da 198 trade (30g)
Sep 30 15:25:02 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 15:25:04 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1917 ms
Sep 30 15:32:25 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 15:32:25 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 15:47:27 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 15:47:27 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 15:47:29 Trading-Agent python[1858347]: [selettore] QUSDT gen_18c839a0 short p=0.70 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 30 15:47:29 Trading-Agent python[1858347]: [DRY_RUN] OPEN short QUSDT qty=4023.1735 @ 0.023076 lev=1.0x SL=0.0238 TP=0.0216
Sep 30 15:47:35 Trading-Agent python[1858347]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=qusdt@bookTicker/ubusdt@bookTicker
Sep 30 15:47:42 Trading-Agent python[1858347]: [ai-shadow] ok in 13.0s · 1030+739 token
Sep 30 15:52:22 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 15:55:29 Trading-Agent python[1858347]: [DRY_RUN] CLOSE QUSDT @ 0.0225675 (trailing_stop)
Sep 30 15:55:31 Trading-Agent python[1858347]: [learning] filtrati 7/199 trade (esplorativi: 7)
Sep 30 15:55:32 Trading-Agent python[1858347]: [main] pesi ricalcolati: 129 coppie strat×regime da 199 trade (30g)
Sep 30 15:55:33 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 15:55:35 Trading-Agent python[1858347]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=ubusdt@bookTicker
Sep 30 16:02:21 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 16:02:21 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 16:11:03 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 16:14:39 Trading-Agent python[1858347]: [main] market scan...
Sep 30 16:16:51 Trading-Agent python[1858347]: [scanner] 3 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 30 16:16:51 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 16:16:51 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 16:16:51 Trading-Agent python[1858347]: [main] valutate 70 coin validate (70 nel registro): ['GPSUSDT', 'STXUSDT', 'HUMAUSDT', 'SUIUSDT', 'HEMIUSDT', 'SPXUSDT', 'SKYAIUSDT', 'ENAUSDT', 'SOPHUSDT', 'SEIUSDT', 'RAYSOLUSDT', 'CROSSUSDT', 'EPICUSDT', 'PARTIUSDT', 'PROMUSDT', 'XPINUSDT', 'TRUMPUSDT', 'HOMEUSDT', 'SYRUPUSDT', 'FLOCKUSDT', 'RENDERUSDT', 'QUSDT', 'XPLUSDT', 'MUBARAKUSDT', 'FORMUSDT', 'SCRUSDT', 'UBUSDT', 'HEIUSDT', 'DOTUSDT', 'BTRUSDT', 'BULLAUSDT', 'ONGUSDT', 'PENGUUSDT', 'SAHARAUSDT', 'JUPUSDT', 'ARCUSDT', 'GALAUSDT', 'USELESSUSDT', 'DEXEUSDT', 'PLUMEUSDT', 'ATOMUSDT', 'TUTUSDT', 'WALUSDT', 'PUNDIXUSDT', 'ZKUSDT', 'PHAUSDT', 'MITOUSDT', 'CATIUSDT', 'VETUSDT', 'MTLUSDT', 'JASMYUSDT', 'AXSUSDT', 'ORCAUSDT', 'AIOUSDT', 'ZORAUSDT', 'BMTUSDT', 'OPENUSDT', 'NEIROUSDT', 'PNUTUSDT', 'TSTUSDT', 'GRIFFAINUSDT', 'RSRUSDT', 'BANKUSDT', 'CVCUSDT', 'STEEMUSDT', 'SUPERUSDT', 'TAUSDT', 'AVAAIUSDT', 'THEUSDT', 'B2USDT']
Sep 30 16:25:11 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 9584 (rifiutati 6052 · registro 1444 · controllo 1426 · trade 330 · pesi 113 · memoria 94 · selettore 39 · deriva 37) — quota gratuita 50000/giorno
Sep 30 16:25:11 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 16:25:11 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 16:25:11 Trading-Agent python[1858347]: [learning] filtrati 7/199 trade (esplorativi: 7)
Sep 30 16:25:12 Trading-Agent python[1858347]: [main] pesi ricalcolati: 129 coppie strat×regime da 199 trade (30g)
Sep 30 16:25:13 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 16:25:15 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 2132 ms
Sep 30 16:26:21 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 16:26:21 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 16:32:40 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 16:32:40 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 16:41:21 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 16:47:40 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 16:47:40 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 17:02:43 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 17:02:43 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 17:13:27 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 17:17:45 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 17:17:45 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 17:25:23 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 9670 (rifiutati 6131 · registro 1447 · controllo 1426 · trade 334 · pesi 113 · memoria 94 · selettore 39 · deriva 37) — quota gratuita 50000/giorno
Sep 30 17:25:24 Trading-Agent python[1858347]: [learning] filtrati 7/199 trade (esplorativi: 7)
Sep 30 17:25:24 Trading-Agent python[1858347]: [main] pesi ricalcolati: 129 coppie strat×regime da 199 trade (30g)
Sep 30 17:25:25 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 17:25:27 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1830 ms
Sep 30 17:27:02 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 17:27:02 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 17:27:02 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 17:27:03 Trading-Agent python[1858347]: [rifiutati] 1 segnali rifiutati valutati
Sep 30 17:32:35 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 17:32:35 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 17:47:38 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 17:47:38 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 18:02:39 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 18:02:39 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 18:06:13 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 18:13:23 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 18:14:04 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 30 18:14:04 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 30 18:14:04 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 30 18:14:04 Trading-Agent systemd[1]: trading-bot.service: Consumed 1h 21min 45.567s CPU time.
Sep 30 18:14:04 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 30 18:14:06 Trading-Agent python[1927496]: [firebase] connesso (Firestore + RTDB)
Sep 30 18:14:07 Trading-Agent python[1927496]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['UBUSDT']
Sep 30 18:14:07 Trading-Agent python[1927496]: [main] avvio bot @ 2026-09-30T18:14:07.487527+00:00 DRY_RUN=True
Sep 30 18:14:08 Trading-Agent python[1927496]: [main] equity riconciliata: 930.32 (base 1000.00 + realizzato -69.68 + fette aperte +0.00)
Sep 30 18:14:08 Trading-Agent python[1927496]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 30 18:14:08 Trading-Agent python[1927496]: [selettore] modello caricato: 92257 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-09-30T06:17:35.247267+00:00 -> solo ombra, non decide
Sep 30 18:14:09 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 18:14:09 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Sep 30 18:14:09 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 279 (trade 199 · rifiutati 73 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Sep 30 18:14:09 Trading-Agent python[1927496]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 18:14:09 Trading-Agent python[1927496]:   q = q.where(order_by, "<=", max_value)
Sep 30 18:14:09 Trading-Agent python[1927496]: [learning] filtrati 7/199 trade (esplorativi: 7)
Sep 30 18:14:10 Trading-Agent python[1927496]: [main] pesi ricalcolati: 129 coppie strat×regime da 199 trade (30g)
Sep 30 18:14:10 Trading-Agent python[1927496]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=ubusdt@bookTicker
Sep 30 18:14:11 Trading-Agent python[1927496]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 18:14:13 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1855 ms
Sep 30 18:14:16 Trading-Agent python[1927496]: [main] market scan...
```
