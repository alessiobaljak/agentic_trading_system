# 0416-1ott-log-dopo-riavvio.req

_eseguito: 2026-10-01 15:25 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 01 11:22:31 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 11:22:32 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1680 ms
Oct 01 11:32:35 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 11:32:35 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 11:47:48 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 11:47:48 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 12:02:30 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 12:02:30 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 12:17:48 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 12:17:48 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 12:18:18 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 12:23:01 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 6287 (rifiutati 3531 · controllo 1116 · registro 1083 · trade 296 · pesi 87 · memoria 74 · deriva 30 · referti 30) — quota gratuita 50000/giorno
Oct 01 12:23:01 Trading-Agent python[1927496]: [learning] filtrati 8/211 trade (esplorativi: 8)
Oct 01 12:23:01 Trading-Agent python[1927496]: [main] pesi ricalcolati: 136 coppie strat×regime da 211 trade (30g)
Oct 01 12:23:03 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 12:23:05 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 2137 ms
Oct 01 12:24:40 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 12:32:39 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 12:32:39 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 12:47:53 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 12:47:53 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 13:02:36 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 13:02:36 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 13:08:48 Trading-Agent python[1927496]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 01 13:17:49 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 13:17:49 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 13:22:59 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 6553 (rifiutati 3660 · controllo 1178 · registro 1141 · trade 303 · pesi 90 · memoria 78 · deriva 31 · referti 31) — quota gratuita 50000/giorno
Oct 01 13:22:59 Trading-Agent python[1927496]: [learning] filtrati 8/211 trade (esplorativi: 8)
Oct 01 13:22:59 Trading-Agent python[1927496]: [main] pesi ricalcolati: 136 coppie strat×regime da 211 trade (30g)
Oct 01 13:23:00 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 13:23:03 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1899 ms
Oct 01 13:24:08 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 13:24:08 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 13:32:43 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 13:32:43 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 13:47:33 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 13:47:33 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 13:47:35 Trading-Agent python[1927496]: [selettore] SUPERUSDT gen_0eb999b7 short p=0.67 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 13:47:35 Trading-Agent python[1927496]: [DRY_RUN] OPEN short SUPERUSDT qty=330.2604 @ 0.19822 lev=1.0x SL=0.2018 TP=0.1893
Oct 01 13:47:35 Trading-Agent python[1927496]: [declassata] SUPERUSDT gen_0eb999b7 short size x0.25
Oct 01 13:47:41 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=superusdt@bookTicker/tstusdt@bookTicker/xplusdt@bookTicker
Oct 01 14:02:38 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 14:02:38 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 14:08:54 Trading-Agent python[1927496]: [DRY_RUN] CLOSE XPLUSDT @ 0.09498999999999999 (trailing_stop)
Oct 01 14:08:56 Trading-Agent python[1927496]: [learning] filtrati 8/212 trade (esplorativi: 8)
Oct 01 14:08:57 Trading-Agent python[1927496]: [main] pesi ricalcolati: 136 coppie strat×regime da 212 trade (30g)
Oct 01 14:08:58 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 14:09:00 Trading-Agent python[1927496]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=superusdt@bookTicker/tstusdt@bookTicker
Oct 01 14:15:09 Trading-Agent python[1927496]: [main] market scan...
Oct 01 14:17:21 Trading-Agent python[1927496]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 01 14:17:21 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 14:17:21 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 14:17:22 Trading-Agent python[1927496]: [main] valutate 71 coin validate (71 nel registro): ['PENGUUSDT', 'QUSDT', 'XPLUSDT', 'AIOUSDT', 'THEUSDT', 'VETUSDT', 'ZKUSDT', 'PARTIUSDT', 'ONGUSDT', 'NEIROUSDT', 'ORCAUSDT', 'ZORAUSDT', 'ENAUSDT', 'HOMEUSDT', 'TRUMPUSDT', 'ATOMUSDT', 'IDUSDT', 'MUBARAKUSDT', 'SAHARAUSDT', 'MTLUSDT', 'SYRUPUSDT', 'SCRUSDT', 'DOTUSDT', 'GPSUSDT', 'SUIUSDT', 'STXUSDT', 'OPENUSDT', 'RAYSOLUSDT', 'SUPERUSDT', 'PLUMEUSDT', 'BTRUSDT', 'FLOCKUSDT', 'USELESSUSDT', 'JUPUSDT', 'RSRUSDT', 'GALAUSDT', 'RENDERUSDT', 'XPINUSDT', 'FORMUSDT', 'STEEMUSDT', 'PUNDIXUSDT', 'WALUSDT', 'PHAUSDT', 'SPXUSDT', 'EPICUSDT', 'BMTUSDT', 'SOPHUSDT', 'AXSUSDT', 'DEXEUSDT', 'BULLAUSDT', 'HEIUSDT', 'CVCUSDT', 'PNUTUSDT', 'TUTUSDT', 'SKYAIUSDT', 'MITOUSDT', 'B2USDT', 'ARCUSDT', 'SEIUSDT', 'JASMYUSDT', 'GRIFFAINUSDT', 'HEMIUSDT', 'TAUSDT', 'HUMAUSDT', 'BANKUSDT', 'TSTUSDT', 'UBUSDT', 'PROMUSDT', 'CATIUSDT', 'CROSSUSDT', 'AVAAIUSDT']
Oct 01 14:23:15 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 6818 (rifiutati 3787 · controllo 1240 · registro 1194 · trade 311 · pesi 95 · memoria 82 · deriva 

[... 17 caratteri omessi (testa e coda conservate) ...]

— quota gratuita 50000/giorno
Oct 01 14:23:15 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 14:23:15 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 14:23:15 Trading-Agent python[1927496]: [learning] filtrati 8/212 trade (esplorativi: 8)
Oct 01 14:23:15 Trading-Agent python[1927496]: [main] pesi ricalcolati: 136 coppie strat×regime da 212 trade (30g)
Oct 01 14:23:16 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 14:23:20 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 2939 ms
Oct 01 14:24:25 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 14:24:25 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 14:32:28 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 14:32:28 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 14:32:29 Trading-Agent python[1927496]: [selettore] BTRUSDT gen_8981d5f2 short p=0.66 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 14:32:29 Trading-Agent python[1927496]: [DRY_RUN] OPEN short BTRUSDT qty=2075.4801 @ 0.05014 lev=2.0x SL=0.0509 TP=0.0491
Oct 01 14:32:29 Trading-Agent python[1927496]: [declassata] BTRUSDT gen_8981d5f2 short size x0.25
Oct 01 14:32:36 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/superusdt@bookTicker/tstusdt@bookTicker
Oct 01 14:39:17 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 14:47:57 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 14:47:57 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 14:55:16 Trading-Agent python[1927496]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 01 15:02:46 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 15:02:46 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 15:04:20 Trading-Agent python[1927496]: [DRY_RUN] CLOSE SUPERUSDT @ 0.20178843521722345 (stop_loss)
Oct 01 15:04:20 Trading-Agent python[1927496]: [referto] SUPERUSDT gen_0eb999b7: a favore fino a 0.49R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Oct 01 15:04:23 Trading-Agent python[1927496]: [learning] filtrati 8/213 trade (esplorativi: 8)
Oct 01 15:04:23 Trading-Agent python[1927496]: [main] pesi ricalcolati: 137 coppie strat×regime da 213 trade (30g)
Oct 01 15:04:25 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 15:04:27 Trading-Agent python[1927496]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker/tstusdt@bookTicker
Oct 01 15:10:35 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 15:17:30 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 15:17:30 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 15:18:01 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 15:18:01 Trading-Agent python[1927496]: [DRY_RUN] CLOSE TSTUSDT @ 0.0175575 (trailing_stop)
Oct 01 15:18:05 Trading-Agent python[1927496]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 01 15:18:05 Trading-Agent python[1927496]: [learning] filtrati 8/214 trade (esplorativi: 8)
Oct 01 15:18:05 Trading-Agent python[1927496]: [main] pesi ricalcolati: 137 coppie strat×regime da 214 trade (30g)
Oct 01 15:18:06 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 15:18:08 Trading-Agent python[1927496]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker
Oct 01 15:23:43 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 7117 (rifiutati 3913 · controllo 1302 · registro 1273 · trade 318 · pesi 105 · memoria 86 · deriva 36 · referti 36) — quota gratuita 50000/giorno
Oct 01 15:23:43 Trading-Agent python[1927496]: [learning] filtrati 8/214 trade (esplorativi: 8)
Oct 01 15:23:43 Trading-Agent python[1927496]: [main] pesi ricalcolati: 137 coppie strat×regime da 214 trade (30g)
Oct 01 15:23:44 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 15:23:47 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 2889 ms
Oct 01 15:24:43 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Oct 01 15:24:43 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Oct 01 15:24:43 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Oct 01 15:24:43 Trading-Agent systemd[1]: trading-bot.service: Consumed 35min 18.924s CPU time.
Oct 01 15:24:43 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Oct 01 15:24:45 Trading-Agent python[1975598]: [firebase] connesso (Firestore + RTDB)
Oct 01 15:24:46 Trading-Agent python[1975598]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['BTRUSDT']
Oct 01 15:24:46 Trading-Agent python[1975598]: [main] avvio bot @ 2026-10-01T15:24:46.055221+00:00 DRY_RUN=True
Oct 01 15:24:46 Trading-Agent python[1975598]: [main] equity riconciliata: 921.96 (base 1000.00 + realizzato -78.04 + fette aperte +0.00)
Oct 01 15:24:46 Trading-Agent python[1975598]: [main] versione dell'avvio: commit ebe4d0d, config a3508539a199
Oct 01 15:24:46 Trading-Agent python[1975598]: [main] cooldown ricaricati: 1 coin, 0 strategie in panchina (spenta in parita': non si applica)
Oct 01 15:24:46 Trading-Agent python[1975598]: [selettore] modello caricato: 99688 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-10-01T06:18:19.687945+00:00 -> solo ombra, non decide
Oct 01 15:24:47 Trading-Agent python[1975598]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=btrusdt@bookTicker
Oct 01 15:24:52 Trading-Agent python[1975598]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 15 trade paper
Oct 01 15:24:52 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 15:24:52 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 01 15:24:52 Trading-Agent python[1975598]: [firebase] letture ultime 24 h: 263 (trade 214 · rifiutati 42 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Oct 01 15:24:52 Trading-Agent python[1975598]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 15:24:52 Trading-Agent python[1975598]:   q = q.where(order_by, "<=", max_value)
Oct 01 15:24:52 Trading-Agent python[1975598]: [learning] filtrati 8/214 trade (esplorativi: 8)
Oct 01 15:24:52 Trading-Agent python[1975598]: [main] pesi ricalcolati: 137 coppie strat×regime da 214 trade (30g)
Oct 01 15:24:53 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 15:24:56 Trading-Agent python[1975598]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1793 ms
Oct 01 15:24:56 Trading-Agent python[1975598]: [giorni] riga del 2026-09-30: cicli None/96, aperti None, rifiutati None, riavvii 1
Oct 01 15:24:59 Trading-Agent python[1975598]: [main] market scan...
```
