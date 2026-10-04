# 0469-4ott-mattina-log-bot.req

_eseguito: 2026-10-04 06:05 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 04 01:37:47 Trading-Agent python[2005927]: [DRY_RUN] CLOSE ZORAUSDT @ 0.007653784327160016 (stop_loss)
Oct 04 01:37:47 Trading-Agent python[2005927]: [referto] ZORAUSDT gen_ceab7f6a: a favore fino a 0.37R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Oct 04 01:37:52 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 01:37:52 Trading-Agent python[2005927]: [learning] filtrati 10/260 trade (esplorativi: 10)
Oct 04 01:37:52 Trading-Agent python[2005927]: [main] pesi ricalcolati: 164 coppie strat×regime da 260 trade (30g)
Oct 04 01:37:53 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 01:37:54 Trading-Agent python[2005927]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=griffainusdt@bookTicker/sophusdt@bookTicker/stxusdt@bookTicker/ubusdt@bookTicker/xplusdt@bookTicker
Oct 04 01:47:35 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 01:47:35 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 01:52:55 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 01:52:55 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 01:53:59 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7643 (rifiutati 4080 · controllo 1426 · registro 1406 · trade 378 · pesi 121 · memoria 96 · deriva 42 · referti 42) — quota gratuita 50000/giorno
Oct 04 01:53:59 Trading-Agent python[2005927]: [learning] filtrati 10/260 trade (esplorativi: 10)
Oct 04 01:53:59 Trading-Agent python[2005927]: [main] pesi ricalcolati: 164 coppie strat×regime da 260 trade (30g)
Oct 04 01:54:00 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 01:54:02 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1562 ms
Oct 04 02:02:43 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 02:02:43 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 02:12:18 Trading-Agent python[2005927]: [DRY_RUN] CLOSE STXUSDT @ 0.37783417775385786 (stop_loss)
Oct 04 02:12:18 Trading-Agent python[2005927]: [referto] STXUSDT gen_14e1775b: a favore fino a 0.32R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 04 02:12:22 Trading-Agent python[2005927]: [learning] filtrati 10/261 trade (esplorativi: 10)
Oct 04 02:12:22 Trading-Agent python[2005927]: [main] pesi ricalcolati: 164 coppie strat×regime da 261 trade (30g)
Oct 04 02:12:23 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 02:12:25 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=griffainusdt@bookTicker/sophusdt@bookTicker/ubusdt@bookTicker/xplusdt@bookTicker
Oct 04 02:12:55 Trading-Agent python[2005927]: [DRY_RUN] CLOSE UBUSDT @ 0.1350675 (trailing_stop)
Oct 04 02:12:57 Trading-Agent python[2005927]: [learning] filtrati 10/262 trade (esplorativi: 10)
Oct 04 02:12:58 Trading-Agent python[2005927]: [main] pesi ricalcolati: 164 coppie strat×regime da 262 trade (30g)
Oct 04 02:12:59 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 02:13:01 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=griffainusdt@bookTicker/sophusdt@bookTicker/xplusdt@bookTicker
Oct 04 02:17:53 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 02:17:53 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 02:28:18 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 02:28:19 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 04 02:42:34 Trading-Agent python[2005927]: [main] market scan...
Oct 04 02:44:48 Trading-Agent python[2005927]: [scanner] 6 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 04 02:44:48 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 02:44:48 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 02:44:48 Trading-Agent python[2005927]: [main] valutate 72 coin validate (72 nel registro): ['MUBARAKUSDT', 'RAYSOLUSDT', 'ARCUSDT', 'ZORAUSDT', 'CROSSUSDT', 'SUPERUSDT', 'HUMAUSDT', 'RENDERUSDT', 'TSTUSDT', 'CVCUSDT', 'HEMIUSDT', 'UBUSDT', 'PARTIUSDT', 'DEXEUSDT', 'BANKUSDT', 'STXUSDT', 'GALAUSDT', 'GPSUSDT', 'USELESSUSDT', 'BRUSDT', 'ENAUSDT', 'JASMYUSDT', 'TUTUSDT', 'XPINUSDT', 'ATOMUSDT', 'VETUSDT', 'PUNDIXUSDT', 'SUIUSDT', 'SAHARAUSDT', 'AXSUSDT', 'DOTUSDT', 'BMTUSDT', 'IDUSDT', 'FORMUSDT', 'THEUSDT', 'ONGUSDT', 'SOPHUSDT', 'STEEMUSDT', 'PENGUUSDT', 'NEIROUSDT', 'B2USDT', 'TRUMPUSDT', 'XPLUSDT', 'QUSDT', 'SEIUSDT', 'PROMUSDT', 'OPENUSDT', 'MTLUSDT', 'GRIFFAINUSDT', 'SPXUSDT', 'AIOUSDT', 'PHAUSDT', 'CATIUSDT', 'WALUSDT', 'JUPUSDT', 'FLOCKUSDT', 'SKYAIUSDT', 'PLUMEUSDT', 'SCRUSDT', 'ORCAUSDT', 'EPICUSDT', 'PNUTUSDT', 'HOMEUSDT', 'HEIUSDT', 'SYRUPUSDT', 'BULLAUSDT', 'AVAAIUSDT', 'TAUSDT', 'ZKUSDT', 'MITOUSDT', 'RSRUSDT', 'BTRUSDT']
Oct 04 02:45:22 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 02:48:15 Trading-Agent python[2005927]: [DRY_RUN] CLOSE SOPHUSDT @ 0.003829636921699874 (stop_loss)
Oct 04 02:48:15 Trading-Agent python[2005927]: [referto] SOPHUSDT gen_42acf37e: mai andato a favore (mfe 0.23R): direzione sbagliata
Oct 04 02:48:19 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 02:48:19 Trading-Agent python[2005927]: [learning] filtrati 10/263 trade (esplorativi: 10)
Oct 04 02:48:19 Trading-Agent python[2005927]: [main] pesi ricalcolati: 165 coppie strat×regime da 263 trade (30g)
Oct 04 02:48:20 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 02:48:22 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=griffainusdt@bookTicker/xplusdt@bookTicker
Oct 04 02:52:58 Trading-Agent python[2005927]: [DRY_RUN] CLOSE GRIFFAINUSDT @ 0.016912 (trailing_stop)
Oct 04 02:52:58 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 02:52:58 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 02:53:01 Trading-Agent python[2005927]: [learning] filtrati 10/264 trade (esplorativi: 10)
Oct 04 02:53:01 Trading-Agent python[2005927]: [main] pesi ricalcolati: 166 coppie strat×regime da 264 trade (30g)
Oct 04 02:53:02 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa3

[... 1902 caratteri omessi (testa e coda conservate) ...]

t 04 03:17:38 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 03:17:38 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 03:32:45 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 03:32:45 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 03:38:25 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 03:44:39 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 04 03:47:26 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 03:47:26 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 03:53:34 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 03:53:34 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 03:54:05 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7663 (rifiutati 4094 · controllo 1426 · registro 1406 · trade 378 · pesi 124 · memoria 96 · deriva 44 · referti 44) — quota gratuita 50000/giorno
Oct 04 03:54:05 Trading-Agent python[2005927]: [learning] filtrati 10/264 trade (esplorativi: 10)
Oct 04 03:54:06 Trading-Agent python[2005927]: [main] pesi ricalcolati: 166 coppie strat×regime da 264 trade (30g)
Oct 04 03:54:07 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 03:54:09 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1653 ms
Oct 04 03:54:09 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 04 04:02:37 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 04:02:37 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 04:08:46 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 04:17:40 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 04:17:40 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 04:23:49 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 04:32:41 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 04:32:41 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 04:32:42 Trading-Agent python[2005927]: [selettore] PNUTUSDT gen_4810faab short p=0.57 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 04 04:32:42 Trading-Agent python[2005927]: [DRY_RUN] OPEN short PNUTUSDT qty=3478.9864 @ 0.05389 lev=2.0x SL=0.0543 TP=0.0527
Oct 04 04:32:49 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=pnutusdt@bookTicker/xplusdt@bookTicker
Oct 04 04:38:54 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 04:47:20 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 04:47:20 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 04:54:35 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7707 (rifiutati 4140 · controllo 1426 · registro 1410 · trade 380 · pesi 120 · memoria 96 · deriva 42 · referti 42) — quota gratuita 50000/giorno
Oct 04 04:54:35 Trading-Agent python[2005927]: [learning] filtrati 10/264 trade (esplorativi: 10)
Oct 04 04:54:35 Trading-Agent python[2005927]: [main] pesi ricalcolati: 166 coppie strat×regime da 264 trade (30g)
Oct 04 04:54:36 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 04:54:38 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1709 ms
Oct 04 05:02:35 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 05:02:35 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 05:09:19 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 05:17:49 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 05:17:49 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 05:24:32 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 05:24:32 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 05:32:30 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 05:32:30 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 05:39:11 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 04 05:39:44 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 05:47:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 05:47:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 05:47:46 Trading-Agent python[2005927]: [selettore] SYRUPUSDT gen_4c6df481 long p=0.56 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 04 05:47:46 Trading-Agent python[2005927]: [DRY_RUN] OPEN long SYRUPUSDT qty=732.9837 @ 0.25578 lev=2.0x SL=0.2518 TP=0.2658
Oct 04 05:47:52 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=pnutusdt@bookTicker/syrupusdt@bookTicker/xplusdt@bookTicker
Oct 04 05:55:03 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7763 (rifiutati 4186 · controllo 1426 · registro 1417 · trade 384 · pesi 119 · memoria 96 · deriva 41 · referti 41) — quota gratuita 50000/giorno
Oct 04 05:55:03 Trading-Agent python[2005927]: [learning] filtrati 10/264 trade (esplorativi: 10)
Oct 04 05:55:04 Trading-Agent python[2005927]: [main] pesi ricalcolati: 166 coppie strat×regime da 264 trade (30g)
Oct 04 05:55:05 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 05:55:07 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1740 ms
Oct 04 06:02:39 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 06:02:39 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
```
