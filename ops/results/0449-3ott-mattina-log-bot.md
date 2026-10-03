# 0449-3ott-mattina-log-bot.req

_eseguito: 2026-10-03 06:04 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 03 01:47:54 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 01:47:54 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 01:48:24 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 5678 (rifiutati 2754 · controllo 1178 · registro 1104 · trade 346 · pesi 98 · memoria 78 · deriva 35 · referti 35) — quota gratuita 50000/giorno
Oct 03 01:48:24 Trading-Agent python[2005927]: [learning] filtrati 8/241 trade (esplorativi: 8)
Oct 03 01:48:25 Trading-Agent python[2005927]: [main] pesi ricalcolati: 152 coppie strat×regime da 241 trade (30g)
Oct 03 01:48:26 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 01:48:28 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1604 ms
Oct 03 01:52:58 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 01:52:58 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 02:02:33 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 02:02:33 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 02:17:37 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 02:17:37 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 02:32:42 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 02:32:42 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 02:41:03 Trading-Agent python[2005927]: [main] market scan...
Oct 03 02:43:14 Trading-Agent python[2005927]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 03 02:43:14 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 02:43:14 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 02:43:14 Trading-Agent python[2005927]: [main] valutate 71 coin validate (71 nel registro): ['ARCUSDT', 'THEUSDT', 'ZORAUSDT', 'SCRUSDT', 'SUIUSDT', 'ATOMUSDT', 'GALAUSDT', 'HEMIUSDT', 'RAYSOLUSDT', 'SEIUSDT', 'DEXEUSDT', 'BULLAUSDT', 'OPENUSDT', 'MUBARAKUSDT', 'ZKUSDT', 'PROMUSDT', 'HUMAUSDT', 'DOTUSDT', 'ENAUSDT', 'SUPERUSDT', 'TUTUSDT', 'PARTIUSDT', 'PHAUSDT', 'EPICUSDT', 'TRUMPUSDT', 'STXUSDT', 'SYRUPUSDT', 'JUPUSDT', 'RENDERUSDT', 'XPLUSDT', 'ORCAUSDT', 'JASMYUSDT', 'FLOCKUSDT', 'SKYAIUSDT', 'SPXUSDT', 'VETUSDT', 'QUSDT', 'PLUMEUSDT', 'HEIUSDT', 'BANKUSDT', 'PENGUUSDT', 'USELESSUSDT', 'BTRUSDT', 'TAUSDT', 'GRIFFAINUSDT', 'AXSUSDT', 'WALUSDT', 'CATIUSDT', 'B2USDT', 'BMTUSDT', 'IDUSDT', 'NEIROUSDT', 'TSTUSDT', 'GPSUSDT', 'MTLUSDT', 'ONGUSDT', 'AIOUSDT', 'UBUSDT', 'HOMEUSDT', 'SAHARAUSDT', 'CROSSUSDT', 'PNUTUSDT', 'MITOUSDT', 'STEEMUSDT', 'XPINUSDT', 'PUNDIXUSDT', 'CVCUSDT', 'RSRUSDT', 'FORMUSDT', 'AVAAIUSDT', 'SOPHUSDT']
Oct 03 02:48:47 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 5986 (rifiutati 2930 · controllo 1240 · registro 1156 · trade 354 · pesi 101 · memoria 82 · deriva 36 · referti 36) — quota gratuita 50000/giorno
Oct 03 02:48:47 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 02:48:47 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 02:48:47 Trading-Agent python[2005927]: [learning] filtrati 8/241 trade (esplorativi: 8)
Oct 03 02:48:47 Trading-Agent python[2005927]: [main] pesi ricalcolati: 152 coppie strat×regime da 241 trade (30g)
Oct 03 02:48:48 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 02:48:50 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1611 ms
Oct 03 02:53:18 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 02:53:18 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 03:02:49 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 03:02:49 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 03:08:23 Trading-Agent python[2005927]: [rifiutati] 3 segnali rifiutati valutati
Oct 03 03:17:53 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 03:17:53 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 03:23:27 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 03 03:26:14 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 03 03:32:23 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 03:32:23 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 03:32:56 Trading-Agent python[2005927]: [DRY_RUN] CLOSE XPINUSDT @ 0.000831475 (trailing_stop)
Oct 03 03:32:59 Trading-Agent python[2005927]: [learning] filtrati 8/242 trade (esplorativi: 8)
Oct 03 03:32:59 Trading-Agent python[2005927]: [main] pesi ricalcolati: 153 coppie strat×regime da 242 trade (30g)
Oct 03 03:33:00 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 03:33:02 Trading-Agent python[2005927]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=bmtusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/penguusdt@bookTicker/qusdt@bookTicker/saharausdt@bookTicker/steemusdt@bookTicker/uselessusdt@bookTicker
Oct 03 03:35:09 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 03 03:47:51 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 03:47:51 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 03:48:23 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 03 03:48:26 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 03 03:48:29 Trading-Agent python[2005927]: [DRY_RUN] CLOSE STEEMUSDT @ 0.0630225 (trailing_stop)
Oct 03 03:48:31 Trading-Agent python[2005927]: [learning] filtrati 8/243 trade (esplorativi: 8)
Oct 03 03:48:32 Trading-Agent python[2005927]: [main] pesi ricalcolati: 153 coppie strat×regime da 243 trade (30g)
Oct 03 03:48:33 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 03:48:35 Trading-Agent python[2005927]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=bmtusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/penguusdt@bookTicker/qusdt@bookTicker/saharausdt@bookTicker/uselessusdt@bookTicker
Oct 03 03:49:03 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 6322 (rifiutati 3106 · controllo 1302 · registro 1225 · trade 361 · pesi 110 · memoria 86 · deriva 39 · referti 39) — quota gratuita 50000/giorno
Oct 03 03:49:03 Tr

[... 1122 caratteri omessi (testa e coda conservate) ...]

pre comunque)
Oct 03 04:02:55 Trading-Agent python[2005927]: [DRY_RUN] OPEN long BANKUSDT qty=3188.3131 @ 0.02913 lev=1.0x SL=0.0289 TP=0.0295
Oct 03 04:02:55 Trading-Agent python[2005927]: [esplorativa] BANKUSDT gen_87fce2d2 long size x0.25
Oct 03 04:03:06 Trading-Agent python[2005927]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/penguusdt@bookTicker/qusdt@bookTicker/saharausdt@bookTicker/uselessusdt@bookTicker
Oct 03 04:04:00 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 03 04:17:55 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 04:17:55 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 04:17:56 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_87fce2d2 long: posizione gia' aperta su questa coin
Oct 03 04:18:27 Trading-Agent python[2005927]: [DRY_RUN] CLOSE PENGUUSDT @ 0.008910999999999999 (trailing_stop)
Oct 03 04:18:32 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 03 04:18:32 Trading-Agent python[2005927]: [learning] filtrati 8/244 trade (esplorativi: 8)
Oct 03 04:18:33 Trading-Agent python[2005927]: [main] pesi ricalcolati: 154 coppie strat×regime da 244 trade (30g)
Oct 03 04:18:34 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 04:18:34 Trading-Agent python[2005927]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/qusdt@bookTicker/saharausdt@bookTicker/uselessusdt@bookTicker
Oct 03 04:32:40 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 04:32:40 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 04:32:40 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_87fce2d2 long: posizione gia' aperta su questa coin
Oct 03 04:42:30 Trading-Agent python[2005927]: [DRY_RUN] CLOSE SAHARAUSDT @ 0.00913525 (scale_out)
Oct 03 04:42:35 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 03 04:42:35 Trading-Agent python[2005927]: [learning] filtrati 8/245 trade (esplorativi: 8)
Oct 03 04:42:35 Trading-Agent python[2005927]: [main] pesi ricalcolati: 155 coppie strat×regime da 245 trade (30g)
Oct 03 04:42:36 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 04:42:36 Trading-Agent python[2005927]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/qusdt@bookTicker/uselessusdt@bookTicker
Oct 03 04:49:06 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 6555 (rifiutati 3198 · controllo 1364 · registro 1281 · trade 365 · pesi 117 · memoria 90 · deriva 42 · referti 42) — quota gratuita 50000/giorno
Oct 03 04:49:06 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 04:49:06 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 04:49:06 Trading-Agent python[2005927]: [learning] filtrati 8/245 trade (esplorativi: 8)
Oct 03 04:49:06 Trading-Agent python[2005927]: [main] pesi ricalcolati: 155 coppie strat×regime da 245 trade (30g)
Oct 03 04:49:07 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 04:49:09 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1654 ms
Oct 03 04:57:49 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 04:57:49 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 04:57:52 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 03 05:03:58 Trading-Agent python[2005927]: [DRY_RUN] CLOSE USELESSUSDT @ 0.21557882905756506 (stop_loss)
Oct 03 05:03:58 Trading-Agent python[2005927]: [referto] USELESSUSDT gen_194e2514: a favore fino a 0.40R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 03 05:04:00 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 05:04:00 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 05:04:03 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 03 05:04:03 Trading-Agent python[2005927]: [learning] filtrati 8/246 trade (esplorativi: 8)
Oct 03 05:04:03 Trading-Agent python[2005927]: [main] pesi ricalcolati: 156 coppie strat×regime da 246 trade (30g)
Oct 03 05:04:04 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 05:04:05 Trading-Agent python[2005927]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/qusdt@bookTicker
Oct 03 05:17:28 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 05:17:28 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 05:19:36 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 03 05:32:34 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 05:32:34 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 05:33:04 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 03 05:47:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 05:47:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 05:49:18 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 6832 (rifiutati 3336 · controllo 1426 · registro 1338 · trade 371 · pesi 122 · memoria 94 · deriva 44 · referti 44) — quota gratuita 50000/giorno
Oct 03 05:49:18 Trading-Agent python[2005927]: [learning] filtrati 8/246 trade (esplorativi: 8)
Oct 03 05:49:18 Trading-Agent python[2005927]: [main] pesi ricalcolati: 156 coppie strat×regime da 246 trade (30g)
Oct 03 05:49:19 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 03 05:49:22 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 2367 ms
Oct 03 05:49:59 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 03 05:49:59 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 05:49:59 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 03 06:02:25 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 03 06:02:25 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
```
