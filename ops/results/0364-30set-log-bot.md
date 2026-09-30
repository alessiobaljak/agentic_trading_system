# 0364-30set-log-bot.req

_eseguito: 2026-09-30 06:12 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 30 00:20:57 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 6639 (rifiutati 4135 · registro 993 · controllo 992 · trade 276 · pesi 83 · memoria 66 · selettore 29 · deriva 27) — quota gratuita 50000/giorno
Sep 30 00:20:57 Trading-Agent python[1858347]: [learning] filtrati 7/186 trade (esplorativi: 7)
Sep 30 00:20:57 Trading-Agent python[1858347]: [main] pesi ricalcolati: 119 coppie strat×regime da 186 trade (30g)
Sep 30 00:20:58 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 00:21:00 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1557 ms
Sep 30 00:27:44 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 00:27:44 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 00:42:48 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 00:42:48 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 00:57:50 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 00:57:50 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 01:12:55 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 01:12:55 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 01:17:41 Trading-Agent python[1858347]: [selettore] HEMIUSDT gen_f001d778 long p=0.58 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 30 01:17:41 Trading-Agent python[1858347]: [DRY_RUN] OPEN long HEMIUSDT qty=10570.3982 @ 0.00617 lev=1.0x SL=0.0061 TP=0.0063
Sep 30 01:17:41 Trading-Agent python[1858347]: [declassata] HEMIUSDT gen_f001d778 long size x0.25
Sep 30 01:17:48 Trading-Agent python[1858347]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/mubarakusdt@bookTicker/ubusdt@bookTicker
Sep 30 01:17:52 Trading-Agent python[1858347]: [ai-shadow] ok in 10.2s · 782+447 token
Sep 30 01:20:57 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 7058 (rifiutati 4419 · controllo 1054 · registro 1051 · trade 280 · pesi 86 · memoria 70 · selettore 30 · deriva 28) — quota gratuita 50000/giorno
Sep 30 01:20:57 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 01:20:57 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 01:20:57 Trading-Agent python[1858347]: [learning] filtrati 7/186 trade (esplorativi: 7)
Sep 30 01:20:58 Trading-Agent python[1858347]: [main] pesi ricalcolati: 119 coppie strat×regime da 186 trade (30g)
Sep 30 01:20:59 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 01:21:01 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1676 ms
Sep 30 01:28:19 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 01:28:19 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 01:43:30 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 01:43:30 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 01:47:18 Trading-Agent python[1858347]: [selettore] AIOUSDT gen_581d4a68 long p=0.57 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 30 01:47:18 Trading-Agent python[1858347]: [DRY_RUN] OPEN long AIOUSDT qty=2346.2317 @ 0.03969 lev=1.0x SL=0.0392 TP=0.0412
Sep 30 01:47:25 Trading-Agent python[1858347]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=aiousdt@bookTicker/hemiusdt@bookTicker/mubarakusdt@bookTicker/ubusdt@bookTicker
Sep 30 01:47:29 Trading-Agent python[1858347]: [ai-shadow] ok in 10.3s · 784+500 token
Sep 30 01:48:00 Trading-Agent python[1858347]: [DRY_RUN] CLOSE HEMIUSDT @ 0.006231 (trailing_stop)
Sep 30 01:48:07 Trading-Agent python[1858347]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=aiousdt@bookTicker/mubarakusdt@bookTicker/ubusdt@bookTicker
Sep 30 01:48:07 Trading-Agent python[1858347]: [learning] filtrati 7/187 trade (esplorativi: 7)
Sep 30 01:48:08 Trading-Agent python[1858347]: [main] pesi ricalcolati: 120 coppie strat×regime da 187 trade (30g)
Sep 30 01:48:09 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 02:02:15 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 02:02:15 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 02:03:18 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 02:17:24 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 02:17:24 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 02:21:04 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 7480 (rifiutati 4703 · controllo 1116 · registro 1107 · trade 285 · pesi 91 · memoria 74 · selettore 31 · deriva 30) — quota gratuita 50000/giorno
Sep 30 02:21:04 Trading-Agent python[1858347]: [learning] filtrati 7/187 trade (esplorativi: 7)
Sep 30 02:21:05 Trading-Agent python[1858347]: [main] pesi ricalcolati: 120 coppie strat×regime da 187 trade (30g)
Sep 30 02:21:06 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 02:21:08 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1657 ms
Sep 30 02:32:38 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 02:32:38 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 02:47:15 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 02:47:15 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 03:02:27 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 03:02:27 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 03:02:57 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 03:02:58 Trading-Agent python[1858347]: [DRY_RUN] CLOSE AIOUSDT @ 0.03918935610017075 (stop_loss)
Sep 30 03:02:58 Trading-Agent python[1858347]: [referto] AIOUSDT gen_581d4a68: mai andato a favore (mfe 0.13R): direzione sbagliata
Sep 30 03:03:01 Trading-Agent python[1858347]: [learning] filtrati 7/188 trade (esplorativi: 7)
Sep 30 03:03:01 Trading-Agent python[1858347]: [main] pesi ricalcolati: 121 coppie strat×regime da 188 trade (30g)
Sep 30 03:03:02 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 03:03:05 Trading-Agent python[1858347]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/ubusdt@bookTicker
Sep 30 03:04:04 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, re

[... 357 caratteri omessi (testa e coda conservate) ...]

arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 03:17:34 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 03:21:12 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 7851 (rifiutati 4916 · registro 1181 · controllo 1178 · trade 289 · pesi 98 · memoria 78 · selettore 34 · deriva 32) — quota gratuita 50000/giorno
Sep 30 03:21:12 Trading-Agent python[1858347]: [learning] filtrati 7/188 trade (esplorativi: 7)
Sep 30 03:21:12 Trading-Agent python[1858347]: [main] pesi ricalcolati: 121 coppie strat×regime da 188 trade (30g)
Sep 30 03:21:13 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 03:21:15 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1658 ms
Sep 30 03:32:42 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 03:32:42 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 03:47:21 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 03:47:21 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 04:02:25 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 04:02:25 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 04:13:46 Trading-Agent python[1858347]: [main] market scan...
Sep 30 04:15:50 Trading-Agent python[1858347]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 30 04:15:50 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 04:15:50 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 04:15:51 Trading-Agent python[1858347]: [main] valutate 70 coin validate (70 nel registro): ['ENAUSDT', 'MUBARAKUSDT', 'WALUSDT', 'DEXEUSDT', 'QUSDT', 'PUNDIXUSDT', 'SPXUSDT', 'PENGUUSDT', 'BMTUSDT', 'SCRUSDT', 'EPICUSDT', 'GPSUSDT', 'ZORAUSDT', 'USELESSUSDT', 'HUMAUSDT', 'SYRUPUSDT', 'XPLUSDT', 'RENDERUSDT', 'DOTUSDT', 'ZKUSDT', 'UBUSDT', 'ORCAUSDT', 'TUTUSDT', 'VETUSDT', 'TRUMPUSDT', 'ATOMUSDT', 'RAYSOLUSDT', 'JASMYUSDT', 'SAHARAUSDT', 'SUIUSDT', 'STEEMUSDT', 'TAUSDT', 'ONGUSDT', 'SUPERUSDT', 'XPINUSDT', 'PNUTUSDT', 'JUPUSDT', 'PLUMEUSDT', 'PHAUSDT', 'CVCUSDT', 'BANKUSDT', 'SKYAIUSDT', 'NEIROUSDT', 'TSTUSDT', 'GALAUSDT', 'AXSUSDT', 'STXUSDT', 'CROSSUSDT', 'RSRUSDT', 'AVAAIUSDT', 'PARTIUSDT', 'AIOUSDT', 'PROMUSDT', 'CATIUSDT', 'MTLUSDT', 'MITOUSDT', 'GRIFFAINUSDT', 'SEIUSDT', 'FLOCKUSDT', 'FORMUSDT', 'HEIUSDT', 'ARCUSDT', 'HEMIUSDT', 'HOMEUSDT', 'OPENUSDT', 'SOPHUSDT', 'BTRUSDT', 'BULLAUSDT', 'THEUSDT', 'B2USDT']
Sep 30 04:19:02 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 04:19:02 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 04:21:37 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 8267 (rifiutati 5200 · controllo 1240 · registro 1237 · trade 293 · pesi 101 · memoria 82 · selettore 35 · deriva 33) — quota gratuita 50000/giorno
Sep 30 04:21:37 Trading-Agent python[1858347]: [learning] filtrati 7/188 trade (esplorativi: 7)
Sep 30 04:21:37 Trading-Agent python[1858347]: [main] pesi ricalcolati: 121 coppie strat×regime da 188 trade (30g)
Sep 30 04:21:38 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 04:21:40 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1798 ms
Sep 30 04:32:36 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 04:32:36 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 04:47:41 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 04:47:41 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 05:02:45 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 05:02:45 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 05:07:25 Trading-Agent python[1858347]: [DRY_RUN] CLOSE UBUSDT @ 0.1504975 (trailing_stop)
Sep 30 05:07:28 Trading-Agent python[1858347]: [learning] filtrati 7/189 trade (esplorativi: 7)
Sep 30 05:07:28 Trading-Agent python[1858347]: [main] pesi ricalcolati: 122 coppie strat×regime da 189 trade (30g)
Sep 30 05:07:29 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 05:07:32 Trading-Agent python[1858347]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker
Sep 30 05:09:30 Trading-Agent python[1858347]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 30 05:17:23 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 05:17:23 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 05:21:58 Trading-Agent python[1858347]: [firebase] letture ultime 24 h: 8621 (rifiutati 5413 · controllo 1302 · registro 1297 · trade 298 · pesi 106 · memoria 86 · selettore 36 · deriva 35) — quota gratuita 50000/giorno
Sep 30 05:21:58 Trading-Agent python[1858347]: [learning] filtrati 7/189 trade (esplorativi: 7)
Sep 30 05:21:59 Trading-Agent python[1858347]: [main] pesi ricalcolati: 122 coppie strat×regime da 189 trade (30g)
Sep 30 05:22:00 Trading-Agent python[1858347]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 30 05:22:02 Trading-Agent python[1858347]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 2082 ms
Sep 30 05:22:35 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 05:22:35 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 05:32:33 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 05:32:33 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 05:37:41 Trading-Agent python[1858347]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 30 05:47:34 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 05:47:34 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 06:02:37 Trading-Agent python[1858347]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 30 06:02:37 Trading-Agent python[1858347]:   return query.where(field_path, op_string, value)
Sep 30 06:02:39 Trading-Agent python[1858347]: [selettore] STXUSDT gen_a5b0e4de short p=0.57 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 30 06:02:39 Trading-Agent python[1858347]: [DRY_RUN] OPEN short STXUSDT qty=295.9498 @ 0.3147 lev=1.0x SL=0.3196 TP=0.3074
Sep 30 06:02:46 Trading-Agent python[1858347]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/stxusdt@bookTicker
Sep 30 06:02:49 Trading-Agent python[1858347]: [ai-shadow] ok in 10.2s · 780+459 token
```
