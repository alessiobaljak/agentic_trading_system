# 0392-1ott-log-bot.req

_eseguito: 2026-10-01 06:13 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 01 00:18:26 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 201 trade (30g)
Oct 01 00:18:27 Trading-Agent python[1927496]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 00:18:29 Trading-Agent python[1927496]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1766 ms
Oct 01 00:25:17 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 00:25:17 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 00:32:48 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 00:32:48 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 00:32:50 Trading-Agent python[1927496]: [selettore] PHAUSDT gen_fa304106 long p=0.69 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 00:32:50 Trading-Agent python[1927496]: [DRY_RUN] OPEN long PHAUSDT qty=395.1786 @ 0.07637 lev=1.0x SL=0.0731 TP=0.0812
Oct 01 00:32:50 Trading-Agent python[1927496]: [declassata] PHAUSDT gen_fa304106 long size x0.25
Oct 01 00:32:56 Trading-Agent python[1927496]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/mitousdt@bookTicker/phausdt@bookTicker/tstusdt@bookTicker
Oct 01 00:47:43 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 00:47:43 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 01:02:38 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 01:02:38 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 01:09:59 Trading-Agent python[1927496]: [DRY_RUN] CLOSE HEMIUSDT @ 0.006379865 (trailing_stop)
Oct 01 01:10:02 Trading-Agent python[1927496]: [learning] filtrati 8/202 trade (esplorativi: 8)
Oct 01 01:10:03 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 202 trade (30g)
Oct 01 01:10:04 Trading-Agent python[1927496]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 01:10:05 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=mitousdt@bookTicker/phausdt@bookTicker/tstusdt@bookTicker
Oct 01 01:17:33 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 01:17:33 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 01:18:34 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 2936 (rifiutati 1755 · controllo 434 · registro 412 · trade 242 · memoria 30 · pesi 29 · deriva 10 · referti 10) — quota gratuita 50000/giorno
Oct 01 01:18:34 Trading-Agent python[1927496]: [learning] filtrati 8/202 trade (esplorativi: 8)
Oct 01 01:18:35 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 202 trade (30g)
Oct 01 01:18:36 Trading-Agent python[1927496]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 01:18:38 Trading-Agent python[1927496]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1771 ms
Oct 01 01:25:26 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 01:25:26 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 01:27:35 Trading-Agent python[1927496]: [DRY_RUN] CLOSE PHAUSDT @ 0.07313795251577564 (stop_loss)
Oct 01 01:27:35 Trading-Agent python[1927496]: [referto] PHAUSDT gen_fa304106: mai andato a favore (mfe 0.08R): direzione sbagliata
Oct 01 01:27:38 Trading-Agent python[1927496]: [learning] filtrati 8/203 trade (esplorativi: 8)
Oct 01 01:27:38 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 203 trade (30g)
Oct 01 01:27:39 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 01:27:41 Trading-Agent python[1927496]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mitousdt@bookTicker/tstusdt@bookTicker
Oct 01 01:32:30 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 01:32:30 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 01:48:08 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 01:54:19 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 01:57:56 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 01:57:56 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 02:02:51 Trading-Agent python[1927496]: [selettore] PNUTUSDT gen_4810faab long p=0.58 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 01 02:02:51 Trading-Agent python[1927496]: [DRY_RUN] OPEN long PNUTUSDT qty=1451.5659 @ 0.05389 lev=1.0x SL=0.0531 TP=0.0563
Oct 01 02:02:51 Trading-Agent python[1927496]: [declassata] PNUTUSDT gen_4810faab long size x0.25
Oct 01 02:02:57 Trading-Agent python[1927496]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=mitousdt@bookTicker/pnutusdt@bookTicker/tstusdt@bookTicker
Oct 01 02:13:14 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 02:13:14 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 02:14:19 Trading-Agent python[1927496]: [main] market scan...
Oct 01 02:16:28 Trading-Agent python[1927496]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 01 02:16:28 Trading-Agent python[1927496]: [main] valutate 70 coin validate (70 nel registro): ['PLUMEUSDT', 'PHAUSDT', 'BULLAUSDT', 'MTLUSDT', 'AVAAIUSDT', 'SCRUSDT', 'XPINUSDT', 'HUMAUSDT', 'ONGUSDT', 'VETUSDT', 'RAYSOLUSDT', 'SUIUSDT', 'XPLUSDT', 'USELESSUSDT', 'TRUMPUSDT', 'UBUSDT', 'BANKUSDT', 'WALUSDT', 'ENAUSDT', 'STXUSDT', 'THEUSDT', 'NEIROUSDT', 'STEEMUSDT', 'SUPERUSDT', 'TUTUSDT', 'MUBARAKUSDT', 'CROSSUSDT', 'QUSDT', 'PARTIUSDT', 'DOTUSDT', 'ORCAUSDT', 'SEIUSDT', 'FLOCKUSDT', 'SKYAIUSDT', 'PENGUUSDT', 'RENDERUSDT', 'GALAUSDT', 'ZKUSDT', 'SPXUSDT', 'OPENUSDT', 'ZORAUSDT', 'GPSUSDT', 'JASMYUSDT', 'ATOMUSDT', 'BMTUSDT', 'B2USDT', 'PNUTUSDT', 'SYRUPUSDT', 'TAUSDT', 'SAHARAUSDT', 'JUPUSDT', 'EPICUSDT', 'AXSUSDT', 'TSTUSDT', 'PROMUSDT', 'HEMIUSDT', 'HEIUSDT', 'DEXEUSDT', 'MITOUSDT', 'HOMEUSDT', 'CVCUSDT', 'FORMUSDT', 'ARCUSDT', 'AIOUSDT', 'RSRUSDT', 'PUNDIXUSDT', 'CATIUSDT', 'GRIFFAINUSDT', 'SOPHUSDT', 'BTRUSDT']
Oct 01 02:19:15 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 02:19:15 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 02:19:46 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 3293 (rifiutati 1955 · controllo 496 · registro 482 · trade 248 · pesi 36 · memoria 34 · deriva 12 · referti 12) — quota gratuita 50000/giorno
Oct 01 02:19:46 Trading-Agent python[1927496]: [learning] filtrati 8/203 trade (esplorativi: 8)
Oct 01 02:19:46 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 203 trade (30g)
Oct 01 02:19:47 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 02:19:49 Trading-Agent python[1927496]: [controllo] pubblicato: sistema g

[... 826 caratteri omessi (testa e coda conservate) ...]

oot/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 02:59:16 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 03:14:30 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 03:14:30 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 03:19:55 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 3606 (rifiutati 2135 · controllo 558 · registro 539 · trade 252 · pesi 39 · memoria 38 · deriva 13 · referti 13) — quota gratuita 50000/giorno
Oct 01 03:19:55 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 03:19:55 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 03:19:55 Trading-Agent python[1927496]: [learning] filtrati 8/203 trade (esplorativi: 8)
Oct 01 03:19:56 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 203 trade (30g)
Oct 01 03:19:57 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 03:19:59 Trading-Agent python[1927496]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1743 ms
Oct 01 03:29:54 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 03:29:54 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 03:45:15 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 03:45:15 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 04:00:35 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 04:00:35 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 04:17:39 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 04:17:39 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 04:20:15 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 3910 (rifiutati 2307 · controllo 620 · registro 594 · trade 257 · memoria 42 · pesi 42 · deriva 14 · referti 14) — quota gratuita 50000/giorno
Oct 01 04:20:15 Trading-Agent python[1927496]: [learning] filtrati 8/203 trade (esplorativi: 8)
Oct 01 04:20:16 Trading-Agent python[1927496]: [main] pesi ricalcolati: 131 coppie strat×regime da 203 trade (30g)
Oct 01 04:20:17 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 04:20:19 Trading-Agent python[1927496]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1582 ms
Oct 01 04:32:27 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 04:32:27 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 04:47:41 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 04:47:41 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 04:52:23 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 05:02:24 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 05:02:24 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 05:02:54 Trading-Agent python[1927496]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 01 05:02:56 Trading-Agent python[1927496]: [DRY_RUN] CLOSE PNUTUSDT @ 0.054552500000000004 (trailing_stop)
Oct 01 05:02:59 Trading-Agent python[1927496]: [learning] filtrati 8/204 trade (esplorativi: 8)
Oct 01 05:02:59 Trading-Agent python[1927496]: [main] pesi ricalcolati: 132 coppie strat×regime da 204 trade (30g)
Oct 01 05:03:00 Trading-Agent python[1927496]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 01 05:03:02 Trading-Agent python[1927496]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mitousdt@bookTicker/tstusdt@bookTicker
Oct 01 05:17:31 Trading-Agent python[1927496]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 01 05:17:31 Trading-Agent python[1927496]:   return query.where(field_path, op_string, value)
Oct 01 05:20:38 Trading-Agent python[1927496]: [firebase] letture ultime 24 h: 4185 (rifiutati 2433 · controllo 682 · registro 661 · trade 261 · pesi 48 · memoria 46 · deriva 16 · referti 16) — quota gratuita 50000/giorno
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
```
