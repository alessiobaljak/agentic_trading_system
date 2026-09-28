# 0326-28set-log-bot.req

_eseguito: 2026-09-28 05:34 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 28 00:47:26 Trading-Agent python[1778756]: [DRY_RUN] OPEN short HUMAUSDT qty=3160.1081 @ 0.029337 lev=1.0x SL=0.0298 TP=0.0284
Sep 28 00:47:33 Trading-Agent python[1778756]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=humausdt@bookTicker/syrupusdt@bookTicker
Sep 28 00:47:36 Trading-Agent python[1778756]: [ai-shadow] ok in 10.0s · 825+521 token
Sep 28 00:52:47 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 00:52:47 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 00:56:24 Trading-Agent python[1778756]: [DRY_RUN] CLOSE HUMAUSDT @ 0.02901525 (trailing_stop)
Sep 28 00:56:30 Trading-Agent python[1778756]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=syrupusdt@bookTicker
Sep 28 00:56:36 Trading-Agent python[1778756]: [learning] filtrati 2/142 trade (esplorativi: 2)
Sep 28 00:56:36 Trading-Agent python[1778756]: [main] pesi ricalcolati: 88 coppie strat×regime da 142 trade (30g)
Sep 28 00:56:37 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 01:11:49 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 01:11:49 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 01:17:21 Trading-Agent python[1778756]: [selettore] XPLUSDT gen_e59ad90b long p=0.71 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 28 01:17:21 Trading-Agent python[1778756]: [DRY_RUN] OPEN long XPLUSDT qty=878.7400 @ 0.1056 lev=1.0x SL=0.1014 TP=0.1139
Sep 28 01:17:27 Trading-Agent python[1778756]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=syrupusdt@bookTicker/xplusdt@bookTicker
Sep 28 01:17:29 Trading-Agent python[1778756]: [ai-shadow] ok in 8.5s · 786+427 token
Sep 28 01:18:30 Trading-Agent python[1778756]: [main] market scan...
Sep 28 01:20:21 Trading-Agent python[1778756]: [scanner] 2 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 28 01:20:21 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 01:20:21 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 01:20:21 Trading-Agent python[1778756]: [main] valutate 61 coin validate (61 nel registro): ['SEIUSDT', 'GPSUSDT', 'USELESSUSDT', 'MUBARAKUSDT', 'PENGUUSDT', 'EPICUSDT', 'ONGUSDT', 'XPLUSDT', 'SOPHUSDT', 'MTLUSDT', 'RAYSOLUSDT', 'TUTUSDT', 'TRUMPUSDT', 'OPENUSDT', 'QUSDT', 'HUMAUSDT', 'PNUTUSDT', 'BULLAUSDT', 'SAHARAUSDT', 'ENAUSDT', 'FLOCKUSDT', 'HOMEUSDT', 'FORMUSDT', 'SUIUSDT', 'DOTUSDT', 'RSRUSDT', 'JASMYUSDT', 'PUNDIXUSDT', 'TSTUSDT', 'PLUMEUSDT', 'MITOUSDT', 'NEIROUSDT', 'SUPERUSDT', 'PHAUSDT', 'ZKUSDT', 'JUPUSDT', 'STXUSDT', 'ATOMUSDT', 'ORCAUSDT', 'RENDERUSDT', 'PROMUSDT', 'SKYAIUSDT', 'GALAUSDT', 'AVAAIUSDT', 'HEMIUSDT', 'AXSUSDT', 'TAUSDT', 'SPXUSDT', 'BANKUSDT', 'VETUSDT', 'ARCUSDT', 'ZORAUSDT', 'HEIUSDT', 'WALUSDT', 'CROSSUSDT', 'BTRUSDT', 'THEUSDT', 'SYRUPUSDT', 'DEXEUSDT', 'B2USDT', 'GRIFFAINUSDT']
Sep 28 01:20:52 Trading-Agent python[1778756]: [learning] filtrati 2/142 trade (esplorativi: 2)
Sep 28 01:20:53 Trading-Agent python[1778756]: [main] pesi ricalcolati: 88 coppie strat×regime da 142 trade (30g)
Sep 28 01:20:54 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 01:20:56 Trading-Agent python[1778756]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1635 ms
Sep 28 01:27:11 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 01:27:11 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 01:42:31 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 01:42:31 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 01:47:02 Trading-Agent python[1778756]: [selettore] PROMUSDT gen_cd5c842f long p=0.60 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 28 01:47:02 Trading-Agent python[1778756]: [DRY_RUN] OPEN long PROMUSDT qty=29.8953 @ 6.208 lev=2.0x SL=6.0957 TP=6.3765
Sep 28 01:47:09 Trading-Agent python[1778756]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker/syrupusdt@bookTicker/xplusdt@bookTicker
Sep 28 01:47:12 Trading-Agent python[1778756]: [ai-shadow] ok in 9.8s · 784+485 token
Sep 28 01:57:40 Trading-Agent python[1778756]: [main] verdetti (trailing/post-stop) assegnati a 7 trade paper
Sep 28 01:57:40 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 01:57:40 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 02:02:42 Trading-Agent python[1778756]: [DRY_RUN] CLOSE SYRUPUSDT @ 0.21442125 (trailing_stop)
Sep 28 02:02:46 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 02:02:46 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 02:02:46 Trading-Agent python[1778756]: [learning] filtrati 2/143 trade (esplorativi: 2)
Sep 28 02:02:47 Trading-Agent python[1778756]: [main] pesi ricalcolati: 89 coppie strat×regime da 143 trade (30g)
Sep 28 02:02:47 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 02:02:52 Trading-Agent python[1778756]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker/xplusdt@bookTicker
Sep 28 02:17:06 Trading-Agent python[1778756]: [main] trade bloccato dal gate: stop troppo largo: 7.0% del prezzo > 6% (ATR gonfiato: primo incasso a +10%, lock a +5%)
Sep 28 02:17:06 Trading-Agent python[1778756]: [rifiuto] QUSDT gen_18c839a0 long: risk gate: stop troppo largo: 7.0% del prezzo > 6% (ATR gonfiato: primo incasso a +10%, lock a +5%)
Sep 28 02:17:17 Trading-Agent python[1778756]: [ai-shadow] ok in 10.5s · 910+535 token
Sep 28 02:17:49 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 02:17:49 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 02:20:54 Trading-Agent python[1778756]: [learning] filtrati 2/143 trade (esplorativi: 2)
Sep 28 02:20:55 Trading-Agent python[1778756]: [main] pesi ricalcolati: 89 coppie strat×regime da 143 trade (30g)
Sep 28 02:20:56 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 02:20:57 Trading-Agent python[1778756]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1644 ms
Sep 28 02:33:16 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 02:33:16 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 02:48:37 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 02:48:37 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 02:48:37 Trading-Agent python[1778756]: [rifiutati] 1 segnali rifiutati valutati
Sep 28 03:03:59 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 03:03:59 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 03:06:03 Trading-Agent python[1778756]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 03:10:10 Trading-Agent python[1778756]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 03:15:20 Trading-Agent python[1778756]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 03:17:21 Trading-Agent python[1778756]: [selettore] TUTUSDT gen_4465723e short p=0.67 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 28 03:17:21 Trading-Agent python[1778756]: [DRY_RUN] OPEN short TUTUSDT qty=1748.3660 @ 0.02447 lev=1.0x SL=0.0251 TP=0.0235
Sep 28 03:17:21 Trading-Agent python[1778756]: [declassata] TUTUSDT gen_4465723e short size x0.25
Sep 28 03:17:28 Trading-Agent python[1778756]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 28 03:17:30 Trading-Agent python[1778756]: [ai-shadow] ok in 8.5s · 783+400 token
Sep 28 03:19:05 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 03:19:05 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 03:21:10 Trading-Agent python[1778756]: [learning] filtrati 2/143 trade (esplorativi: 2)
Sep 28 03:21:10 Trading-Agent python[1778756]: [main] pesi ricalcolati: 89 coppie strat×regime da 143 trade (30g)
Sep 28 03:21:11 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 03:21:13 Trading-Agent python[1778756]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1688 ms
Sep 28 03:32:39 Trading-Agent python[1778756]: [DRY_RUN] CLOSE PROMUSDT @ 6.26975 (trailing_stop)
Sep 28 03:32:43 Trading-Agent python[1778756]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 28 03:32:43 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 03:32:43 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 03:32:43 Trading-Agent python[1778756]: [learning] filtrati 2/144 trade (esplorativi: 2)
Sep 28 03:32:43 Trading-Agent python[1778756]: [main] pesi ricalcolati: 89 coppie strat×regime da 144 trade (30g)
Sep 28 03:32:44 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 03:32:46 Trading-Agent python[1778756]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=tutusdt@bookTicker/xplusdt@bookTicker
Sep 28 03:48:10 Trading-Agent python[1778756]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 28 03:48:10 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 03:48:10 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 04:03:32 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 04:03:32 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 04:17:26 Trading-Agent python[1778756]: [selettore] USELESSUSDT gen_194e2514 long p=0.66 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 28 04:17:26 Trading-Agent python[1778756]: [DRY_RUN] OPEN long USELESSUSDT qty=89.9786 @ 0.25898 lev=1.0x SL=0.2497 TP=0.2821
Sep 28 04:17:26 Trading-Agent python[1778756]: [declassata] USELESSUSDT gen_194e2514 long size x0.25
Sep 28 04:17:32 Trading-Agent python[1778756]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=tutusdt@bookTicker/uselessusdt@bookTicker/xplusdt@bookTicker
Sep 28 04:17:36 Trading-Agent python[1778756]: [ai-shadow] ok in 9.7s · 922+552 token
Sep 28 04:18:38 Trading-Agent python[1778756]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 28 04:18:38 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 04:18:38 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 04:21:15 Trading-Agent python[1778756]: [learning] filtrati 2/144 trade (esplorativi: 2)
Sep 28 04:21:15 Trading-Agent python[1778756]: [main] pesi ricalcolati: 89 coppie strat×regime da 144 trade (30g)
Sep 28 04:21:16 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 04:21:18 Trading-Agent python[1778756]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1562 ms
Sep 28 04:33:45 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 04:33:45 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 04:49:15 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 04:49:15 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 05:03:43 Trading-Agent python[1778756]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 28 05:04:47 Trading-Agent python[1778756]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 28 05:04:47 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 05:04:47 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 05:18:43 Trading-Agent python[1778756]: [main] market scan...
Sep 28 05:20:51 Trading-Agent python[1778756]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 28 05:20:51 Trading-Agent python[1778756]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 28 05:20:51 Trading-Agent python[1778756]:   return query.where(field_path, op_string, value)
Sep 28 05:20:52 Trading-Agent python[1778756]: [main] valutate 66 coin validate (66 nel registro): ['SUIUSDT', 'ZORAUSDT', 'B2USDT', 'EPICUSDT', 'JUPUSDT', 'USELESSUSDT', 'PHAUSDT', 'JASMYUSDT', 'FLOCKUSDT', 'QUSDT', 'BULLAUSDT', 'MUBARAKUSDT', 'GALAUSDT', 'WALUSDT', 'HEMIUSDT', 'TAUSDT', 'STXUSDT', 'XPLUSDT', 'RAYSOLUSDT', 'AXSUSDT', 'CROSSUSDT', 'VETUSDT', 'CVCUSDT', 'OPENUSDT', 'PENGUUSDT', 'ZKUSDT', 'PNUTUSDT', 'TRUMPUSDT', 'ENAUSDT', 'NEIROUSDT', 'SUPERUSDT', 'SAHARAUSDT', 'TUTUSDT', 'ATOMUSDT', 'ARCUSDT', 'THEUSDT', 'DOTUSDT', 'ONGUSDT', 'RSRUSDT', 'RENDERUSDT', 'ORCAUSDT', 'DEXEUSDT', 'SPXUSDT', 'PUNDIXUSDT', 'TSTUSDT', 'STEEMUSDT', 'MTLUSDT', 'BMTUSDT', 'FORMUSDT', 'PLUMEUSDT', 'SOPHUSDT', 'GRIFFAINUSDT', 'SEIUSDT', 'SKYAIUSDT', 'HOMEUSDT', 'SYRUPUSDT', 'HEIUSDT', 'AIOUSDT', 'AVAAIUSDT', 'GPSUSDT', 'BANKUSDT', 'PROMUSDT', 'BTRUSDT', 'MITOUSDT', 'HUMAUSDT', 'UBUSDT']
Sep 28 05:21:24 Trading-Agent python[1778756]: [learning] filtrati 2/144 trade (esplorativi: 2)
Sep 28 05:21:25 Trading-Agent python[1778756]: [main] pesi ricalcolati: 89 coppie strat×regime da 144 trade (30g)
Sep 28 05:21:25 Trading-Agent python[1778756]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 28 05:21:27 Trading-Agent python[1778756]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1608 ms
Sep 28 05:32:33 Trading-Agent python[1778756]: [selettore] EPICUSDT gen_dfb554f7 long p=0.69 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Sep 28 05:32:33 Trading-Agent python[1778756]: [DRY_RUN] OPEN long EPICUSDT qty=118.4594 @ 0.496 lev=1.0x SL=0.4860 TP=0.5161
Sep 28 05:32:33 Trading-Agent python[1778756]: [declassata] EPICUSDT gen_dfb554f7 long size x0.25
Sep 28 05:32:39 Trading-Agent python[1778756]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=epicusdt@bookTicker/tutusdt@bookTicker/uselessusdt@bookTicker/xplusdt@bookTicker
Sep 28 05:32:43 Trading-Agent python[1778756]: [ai-shadow] ok in 9.4s · 783+457 token
```
