# 0512-6ott-mattina-log-bot.req

_eseguito: 2026-10-06 06:05 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 06 02:14:40 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 06 02:14:40 Trading-Agent python[2005927]: [learning] filtrati 12/305 trade (esplorativi: 12)
Oct 06 02:14:40 Trading-Agent python[2005927]: [main] pesi ricalcolati: 185 coppie strat×regime da 305 trade (30g)
Oct 06 02:14:41 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 02:14:42 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 02:14:43 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=raysolusdt@bookTicker/skyaiusdt@bookTicker
Oct 06 02:29:57 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 02:29:57 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 02:30:00 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 06 02:30:00 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 02:32:59 Trading-Agent python[2005927]: [selettore] PTBUSDT gen_684d7623 long p=0.73 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 06 02:32:59 Trading-Agent python[2005927]: [DRY_RUN] OPEN long PTBUSDT qty=98159.3067 @ 0.0009401 lev=1.0x SL=0.0009 TP=0.0010
Oct 06 02:33:05 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=ptbusdt@bookTicker/raysolusdt@bookTicker/skyaiusdt@bookTicker
Oct 06 02:45:25 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 02:45:25 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 02:45:28 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 06 02:45:28 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 02:45:28 Trading-Agent python[2005927]: [main] market scan...
Oct 06 02:47:54 Trading-Agent python[2005927]: [scanner] 3 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 06 02:47:54 Trading-Agent python[2005927]: [main] valutate 77 coin validate (77 nel registro): ['PARTIUSDT', 'HUMAUSDT', 'PTBUSDT', 'GALAUSDT', 'XPLUSDT', 'NEIROUSDT', 'ONGUSDT', 'PNUTUSDT', 'SCRUSDT', 'XPINUSDT', 'AIOUSDT', 'MYXUSDT', 'PHAUSDT', 'JASMYUSDT', 'PLUMEUSDT', 'MITOUSDT', 'DEXEUSDT', 'PENGUUSDT', 'CROSSUSDT', 'TUTUSDT', 'ZKUSDT', '1000BONKUSDT', 'PUNDIXUSDT', 'QUSDT', 'HEMIUSDT', 'TAUSDT', 'VETUSDT', 'SEIUSDT', 'SOPHUSDT', 'ORCAUSDT', 'TSTUSDT', 'SPXUSDT', 'FORMUSDT', 'ZORAUSDT', 'TRUMPUSDT', 'BANKUSDT', 'EPICUSDT', 'SUIUSDT', 'PUMPUSDT', 'GRIFFAINUSDT', 'GPSUSDT', 'AXSUSDT', 'HOMEUSDT', 'STXUSDT', 'MUBARAKUSDT', 'SYRUPUSDT', 'UBUSDT', 'HEIUSDT', 'CVCUSDT', 'ENAUSDT', 'WALUSDT', 'USELESSUSDT', 'OPENUSDT', 'DOTUSDT', 'BULLAUSDT', 'RAYSOLUSDT', 'SAHARAUSDT', 'ARCUSDT', 'AVAAIUSDT', 'ATOMUSDT', 'BMTUSDT', 'SUPERUSDT', 'RSRUSDT', 'THEUSDT', 'MTLUSDT', 'BRUSDT', 'FLOCKUSDT', 'JUPUSDT', 'IDUSDT', 'RENDERUSDT', 'STEEMUSDT', 'BTRUSDT', 'SKYAIUSDT', 'B2USDT', 'AINUSDT', 'CATIUSDT', 'PROMUSDT']
Oct 06 02:59:13 Trading-Agent python[2005927]: [DRY_RUN] CLOSE SKYAIUSDT @ 0.0351525 (trailing_stop)
Oct 06 02:59:19 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=ptbusdt@bookTicker/raysolusdt@bookTicker
Oct 06 02:59:22 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 02:59:22 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 02:59:24 Trading-Agent python[2005927]: [learning] filtrati 12/306 trade (esplorativi: 12)
Oct 06 02:59:24 Trading-Agent python[2005927]: [main] pesi ricalcolati: 186 coppie strat×regime da 306 trade (30g)
Oct 06 02:59:24 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 02:59:25 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 03:08:33 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 8297 (rifiutati 4690 · controllo 1426 · registro 1403 · trade 426 · pesi 120 · memoria 93 · deriva 41 · referti 41) — quota gratuita 50000/giorno
Oct 06 03:08:33 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 03:08:33 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 03:08:34 Trading-Agent python[2005927]: [learning] filtrati 12/306 trade (esplorativi: 12)
Oct 06 03:08:34 Trading-Agent python[2005927]: [main] pesi ricalcolati: 186 coppie strat×regime da 306 trade (30g)
Oct 06 03:08:34 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 03:08:35 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 03:08:37 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1611 ms
Oct 06 03:14:49 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 03:14:49 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 03:14:52 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 03:17:49 Trading-Agent python[2005927]: [rifiuto] PTBUSDT gen_684d7623 long: posizione gia' aperta su questa coin
Oct 06 03:30:09 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 03:30:09 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 03:47:31 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 03:47:31 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 03:47:31 Trading-Agent python[2005927]: [scarti] 2 secondo segnale stessa coin, 1 esplorativa dietro una validata
Oct 06 03:47:32 Trading-Agent python[2005927]: [selettore] FORMUSDT gen_c647ead7 long p=0.75 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 06 03:47:32 Trading-Agent python[2005927]: [DRY_RUN] OPEN long FORMUSDT qty=335.6335 @ 0.2751 lev=1.0x SL=0.2732 TP=0.2779
Oct 06 03:47:33 Trading-Agent python[2005927]: [selettore] HEIUSDT gen_9a383fff long p=0.56 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 06 03:47:33 Trading-Agent python[2005927]: [DRY_RUN] OPEN long HEIUSDT qty=718.1350 @ 0.13485 lev=2.0x SL=0.1334 TP=0.1392
Oct 06 03:47:33 Trading-Agent python[2005927]: [declassata] HEIUSDT gen_9a383fff long size x0.25
Oct 06 03:47:39 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=formusdt@bookTicker/heiusdt@bookTicker/ptbusdt@bookTicker/raysolusdt@bookTicker
Oct 06 03:48:06 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 04:00:22 Trading-Agent python[2005927]: [onchain_agent] GET https://api.alternative.me/fng/ fallito: HTTPSConnectionPool(host='api.alternative.me', port=443): Read

[... 2160 caratteri omessi (testa e coda conservate) ...]

giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 04:08:57 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 8418 (rifiutati 4825 · controllo 1426 · registro 1391 · trade 429 · pesi 117 · memoria 93 · deriva 40 · referti 40) — quota gratuita 50000/giorno
Oct 06 04:08:57 Trading-Agent python[2005927]: [learning] filtrati 12/307 trade (esplorativi: 12)
Oct 06 04:08:57 Trading-Agent python[2005927]: [main] pesi ricalcolati: 187 coppie strat×regime da 307 trade (30g)
Oct 06 04:08:58 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 04:08:59 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 04:09:01 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1686 ms
Oct 06 04:17:50 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 04:17:50 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 04:32:56 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 04:32:56 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 04:33:26 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 06 04:38:46 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 04:47:31 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 04:47:31 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 04:48:01 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 06 04:53:51 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 06 05:02:34 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 05:02:34 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 05:08:53 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 06 05:09:26 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 8444 (rifiutati 4843 · controllo 1426 · registro 1400 · trade 431 · pesi 116 · memoria 93 · deriva 39 · referti 39) — quota gratuita 50000/giorno
Oct 06 05:09:26 Trading-Agent python[2005927]: [learning] filtrati 12/307 trade (esplorativi: 12)
Oct 06 05:09:26 Trading-Agent python[2005927]: [main] pesi ricalcolati: 187 coppie strat×regime da 307 trade (30g)
Oct 06 05:09:27 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 05:09:27 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 05:09:29 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1699 ms
Oct 06 05:17:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 05:17:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 05:28:17 Trading-Agent python[2005927]: [DRY_RUN] CLOSE PLUMEUSDT @ 0.01911515 (trailing_stop)
Oct 06 05:28:19 Trading-Agent python[2005927]: [learning] filtrati 12/308 trade (esplorativi: 12)
Oct 06 05:28:19 Trading-Agent python[2005927]: [main] pesi ricalcolati: 188 coppie strat×regime da 308 trade (30g)
Oct 06 05:28:20 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 05:28:21 Trading-Agent python[2005927]: [referti] 6 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 06 05:28:23 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/ptbusdt@bookTicker/raysolusdt@bookTicker
Oct 06 05:32:50 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 05:32:50 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 05:32:52 Trading-Agent python[2005927]: [selettore] ZORAUSDT gen_2c248ee9 short p=0.65 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 06 05:32:52 Trading-Agent python[2005927]: [DRY_RUN] OPEN short ZORAUSDT qty=24004.8736 @ 0.007697 lev=2.0x SL=0.0078 TP=0.0075
Oct 06 05:32:53 Trading-Agent python[2005927]: [declassata] ZORAUSDT gen_2c248ee9 short size x0.25
Oct 06 05:33:00 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/ptbusdt@bookTicker/raysolusdt@bookTicker/zorausdt@bookTicker
Oct 06 05:43:26 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 05:58:32 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 06 05:58:32 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 06 05:58:34 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 06 05:58:34 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 06 06:03:10 Trading-Agent python[2005927]: [DRY_RUN] CLOSE RAYSOLUSDT @ 2.121431637069837 (stop_loss)
Oct 06 06:03:10 Trading-Agent python[2005927]: [referto] RAYSOLUSDT gen_fa304106: mai andato a favore (mfe 0.15R): direzione sbagliata
Oct 06 06:03:17 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/ptbusdt@bookTicker/zorausdt@bookTicker
Oct 06 06:03:19 Trading-Agent python[2005927]: [main] strategia gen_fa304106: 3 stop consecutivi (panchina spenta in parita': continua a operare)
Oct 06 06:03:23 Trading-Agent python[2005927]: [learning] filtrati 12/309 trade (esplorativi: 12)
Oct 06 06:03:23 Trading-Agent python[2005927]: [main] pesi ricalcolati: 189 coppie strat×regime da 309 trade (30g)
Oct 06 06:03:24 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 06 06:03:24 Trading-Agent python[2005927]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 9 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
```
