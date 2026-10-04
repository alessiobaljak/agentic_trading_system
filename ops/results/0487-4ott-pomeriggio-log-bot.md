# 0487-4ott-pomeriggio-log-bot.req

_eseguito: 2026-10-04 16:01 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 04 12:48:15 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=steemusdt@bookTicker/syrupusdt@bookTicker/zorausdt@bookTicker
Oct 04 12:57:03 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7759 (rifiutati 4147 · controllo 1426 · registro 1418 · trade 425 · pesi 115 · memoria 96 · deriva 39 · referti 39) — quota gratuita 50000/giorno
Oct 04 12:57:03 Trading-Agent python[2005927]: [learning] filtrati 11/269 trade (esplorativi: 11)
Oct 04 12:57:03 Trading-Agent python[2005927]: [main] pesi ricalcolati: 167 coppie strat×regime da 269 trade (30g)
Oct 04 12:57:05 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 12:57:07 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1889 ms
Oct 04 13:02:40 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 13:02:40 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 13:03:44 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 3 trade paper
Oct 04 13:17:36 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 13:17:36 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 13:17:38 Trading-Agent python[2005927]: [selettore] TAUSDT gen_543186c5 long p=0.57 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 04 13:17:38 Trading-Agent python[2005927]: [DRY_RUN] OPEN long TAUSDT qty=1854.7172 @ 0.05047 lev=1.0x SL=0.0500 TP=0.0519
Oct 04 13:17:44 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=steemusdt@bookTicker/syrupusdt@bookTicker/tausdt@bookTicker/zorausdt@bookTicker
Oct 04 13:19:13 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 13:24:30 Trading-Agent python[2005927]: [DRY_RUN] CLOSE ZORAUSDT @ 0.007797500000000001 (trailing_stop)
Oct 04 13:24:33 Trading-Agent python[2005927]: [learning] filtrati 11/270 trade (esplorativi: 11)
Oct 04 13:24:33 Trading-Agent python[2005927]: [main] pesi ricalcolati: 167 coppie strat×regime da 270 trade (30g)
Oct 04 13:24:34 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 13:24:37 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=steemusdt@bookTicker/syrupusdt@bookTicker/tausdt@bookTicker
Oct 04 13:26:38 Trading-Agent python[2005927]: [DRY_RUN] CLOSE SYRUPUSDT @ 0.2517800031219839 (stop_loss)
Oct 04 13:26:38 Trading-Agent python[2005927]: [referto] SYRUPUSDT gen_4c6df481: a favore fino a 0.81R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 04 13:26:41 Trading-Agent python[2005927]: [learning] filtrati 11/271 trade (esplorativi: 11)
Oct 04 13:26:42 Trading-Agent python[2005927]: [main] pesi ricalcolati: 167 coppie strat×regime da 271 trade (30g)
Oct 04 13:26:43 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 13:26:46 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=steemusdt@bookTicker/tausdt@bookTicker
Oct 04 13:32:42 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 13:32:42 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 13:32:43 Trading-Agent python[2005927]: [selettore] PLUMEUSDT gen_e94b056d short p=0.59 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 04 13:32:43 Trading-Agent python[2005927]: [DRY_RUN] OPEN short PLUMEUSDT qty=5019.9398 @ 0.01859 lev=1.0x SL=0.0188 TP=0.0183
Oct 04 13:32:44 Trading-Agent python[2005927]: [selettore] GPSUSDT gen_8a66a70b short p=0.58 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 04 13:32:44 Trading-Agent python[2005927]: [DRY_RUN] OPEN short GPSUSDT qty=8858.9977 @ 0.010534 lev=1.0x SL=0.0106 TP=0.0104
Oct 04 13:32:44 Trading-Agent python[2005927]: [declassata] GPSUSDT gen_8a66a70b short size x0.25
Oct 04 13:32:50 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/plumeusdt@bookTicker/steemusdt@bookTicker/tausdt@bookTicker
Oct 04 13:42:13 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 13:42:13 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 13:42:14 Trading-Agent python[2005927]: [rifiutati] 2 segnali rifiutati valutati
Oct 04 13:47:49 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 13:47:49 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 13:47:49 Trading-Agent python[2005927]: [scarti] 2 esplorativa dietro una validata
Oct 04 13:47:49 Trading-Agent python[2005927]: [rifiuto] TAUSDT gen_543186c5 long: posizione gia' aperta su questa coin
Oct 04 13:47:51 Trading-Agent python[2005927]: [selettore] HEMIUSDT gen_f001d778 short p=0.56 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 04 13:47:51 Trading-Agent python[2005927]: [DRY_RUN] OPEN short HEMIUSDT qty=24666.0464 @ 0.005931 lev=2.0x SL=0.0060 TP=0.0058
Oct 04 13:47:51 Trading-Agent python[2005927]: [declassata] HEMIUSDT gen_f001d778 short size x0.25
Oct 04 13:47:57 Trading-Agent python[2005927]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/hemiusdt@bookTicker/plumeusdt@bookTicker/steemusdt@bookTicker/tausdt@bookTicker
Oct 04 13:57:25 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 13:57:26 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7830 (rifiutati 4205 · controllo 1426 · registro 1419 · trade 429 · pesi 117 · memoria 96 · deriva 40 · referti 40) — quota gratuita 50000/giorno
Oct 04 13:57:26 Trading-Agent python[2005927]: [learning] filtrati 11/271 trade (esplorativi: 11)
Oct 04 13:57:26 Trading-Agent python[2005927]: [main] pesi ricalcolati: 167 coppie strat×regime da 271 trade (30g)
Oct 04 13:57:27 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 13:57:29 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1866 ms
Oct 04 14:02:35 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 14:02:35 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 14:17:48 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 14:17:48 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 14:35:11 Trading-Agent python[2005927]: [DRY_RUN] CLOSE PLUMEUSDT @ 0.018813898502498958 (stop_loss)
Oct 04 14:35:11 Trading-Agent python[2005927]: [referto] PLUMEUSDT gen_e94b056d: a favore fino a 0.38R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
Oct 04 14:35:12 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using

[... 1652 caratteri omessi (testa e coda conservate) ...]

e: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 14:43:21 Trading-Agent python[2005927]: [main] market scan...
Oct 04 14:45:43 Trading-Agent python[2005927]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 04 14:45:43 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 14:45:43 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 14:45:44 Trading-Agent python[2005927]: [main] valutate 76 coin validate (76 nel registro): ['MUBARAKUSDT', 'BRUSDT', 'SKYAIUSDT', 'ATOMUSDT', 'STXUSDT', 'MYXUSDT', 'SUIUSDT', 'PLUMEUSDT', 'OPENUSDT', 'RENDERUSDT', 'AIOUSDT', 'PTBUSDT', 'WALUSDT', 'SEIUSDT', 'CATIUSDT', 'PHAUSDT', 'JASMYUSDT', 'THEUSDT', 'FLOCKUSDT', 'BULLAUSDT', 'SYRUPUSDT', 'CVCUSDT', 'GALAUSDT', 'TAUSDT', 'SOPHUSDT', 'PROMUSDT', 'SUPERUSDT', 'TSTUSDT', 'ZKUSDT', 'BANKUSDT', 'USELESSUSDT', 'PUMPUSDT', 'TRUMPUSDT', 'ENAUSDT', 'CROSSUSDT', 'ARCUSDT', 'NEIROUSDT', 'DEXEUSDT', 'JUPUSDT', 'HEIUSDT', 'SPXUSDT', 'DOTUSDT', 'QUSDT', 'HEMIUSDT', 'PENGUUSDT', 'AXSUSDT', 'RSRUSDT', 'AVAAIUSDT', 'B2USDT', 'PUNDIXUSDT', 'TUTUSDT', 'SCRUSDT', 'XPLUSDT', 'PARTIUSDT', 'GRIFFAINUSDT', 'HUMAUSDT', 'ONGUSDT', 'UBUSDT', 'ORCAUSDT', 'RAYSOLUSDT', 'PNUTUSDT', 'GPSUSDT', 'STEEMUSDT', 'BMTUSDT', 'ZORAUSDT', 'VETUSDT', 'MITOUSDT', 'XPINUSDT', 'MTLUSDT', 'IDUSDT', 'SAHARAUSDT', 'HOMEUSDT', 'EPICUSDT', 'FORMUSDT', 'BTRUSDT', 'AINUSDT']
Oct 04 14:48:40 Trading-Agent python[2005927]: [rifiuto] PLUMEUSDT gen_902fb1fd short: cooldown dopo stop (48m)
Oct 04 14:52:49 Trading-Agent python[2005927]: [DRY_RUN] CLOSE TAUSDT @ 0.04998266876501391 (stop_loss)
Oct 04 14:52:49 Trading-Agent python[2005927]: [referto] TAUSDT gen_543186c5: a favore fino a 0.28R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 04 14:52:50 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 14:52:50 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 14:52:53 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 04 14:52:53 Trading-Agent python[2005927]: [learning] filtrati 11/274 trade (esplorativi: 11)
Oct 04 14:52:53 Trading-Agent python[2005927]: [main] pesi ricalcolati: 170 coppie strat×regime da 274 trade (30g)
Oct 04 14:52:55 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 14:52:56 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/steemusdt@bookTicker
Oct 04 14:57:32 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7758 (rifiutati 4116 · controllo 1426 · registro 1421 · trade 432 · pesi 123 · memoria 96 · deriva 43 · referti 43) — quota gratuita 50000/giorno
Oct 04 14:57:32 Trading-Agent python[2005927]: [learning] filtrati 11/274 trade (esplorativi: 11)
Oct 04 14:57:33 Trading-Agent python[2005927]: [main] pesi ricalcolati: 170 coppie strat×regime da 274 trade (30g)
Oct 04 14:57:34 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 14:57:36 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1909 ms
Oct 04 15:02:39 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 15:02:39 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 15:07:17 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 04 15:08:22 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 15:08:22 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 04 15:08:23 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 04 15:17:32 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 15:17:32 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 15:17:32 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 04 15:17:35 Trading-Agent python[2005927]: [selettore] OPENUSDT gen_2bb283ca long p=0.70 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 04 15:17:35 Trading-Agent python[2005927]: [DRY_RUN] OPEN long OPENUSDT qty=806.1460 @ 0.1155 lev=1.0x SL=0.1106 TP=0.1301
Oct 04 15:17:41 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/openusdt@bookTicker/steemusdt@bookTicker
Oct 04 15:18:05 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 04 15:32:33 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 15:32:33 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 15:32:34 Trading-Agent python[2005927]: [selettore] MUBARAKUSDT gen_1f7ead60 short p=0.61 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 04 15:32:34 Trading-Agent python[2005927]: [DRY_RUN] OPEN short MUBARAKUSDT qty=340.6844 @ 0.07695 lev=1.0x SL=0.0794 TP=0.0696
Oct 04 15:32:34 Trading-Agent python[2005927]: [declassata] MUBARAKUSDT gen_1f7ead60 short size x0.25
Oct 04 15:32:40 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/mubarakusdt@bookTicker/openusdt@bookTicker/steemusdt@bookTicker
Oct 04 15:47:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 04 15:47:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 04 15:48:16 Trading-Agent python[2005927]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.07526250000000001 (trailing_stop)
Oct 04 15:48:19 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 04 15:48:19 Trading-Agent python[2005927]: [learning] filtrati 11/275 trade (esplorativi: 11)
Oct 04 15:48:19 Trading-Agent python[2005927]: [main] pesi ricalcolati: 171 coppie strat×regime da 275 trade (30g)
Oct 04 15:48:21 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 15:48:22 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=hemiusdt@bookTicker/openusdt@bookTicker/steemusdt@bookTicker
Oct 04 15:57:41 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 7731 (rifiutati 4080 · controllo 1426 · registro 1421 · trade 435 · pesi 125 · memoria 96 · deriva 44 · referti 44) — quota gratuita 50000/giorno
Oct 04 15:57:42 Trading-Agent python[2005927]: [learning] filtrati 11/275 trade (esplorativi: 11)
Oct 04 15:57:42 Trading-Agent python[2005927]: [main] pesi ricalcolati: 171 coppie strat×regime da 275 trade (30g)
Oct 04 15:57:43 Trading-Agent python[2005927]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 04 15:57:45 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1793 ms
```
