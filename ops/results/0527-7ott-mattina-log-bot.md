# 0527-7ott-mattina-log-bot.req

_eseguito: 2026-10-07 06:05 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 07 03:25:01 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 07 03:33:06 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 03:33:06 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 03:33:06 Trading-Agent python[2005927]: [scarti] 6 secondo segnale stessa coin
Oct 07 03:33:06 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 03:33:06 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 03:33:06 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b2f350ff long: posizione gia' aperta su questa coin
Oct 07 03:48:05 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 03:48:05 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 03:48:06 Trading-Agent python[2005927]: [scarti] 6 secondo segnale stessa coin
Oct 07 03:48:06 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 03:48:06 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 03:55:04 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 07 03:58:43 Trading-Agent python[2005927]: [DRY_RUN] CLOSE KERNELUSDT @ 0.0512213766835754 (stop_loss)
Oct 07 03:58:43 Trading-Agent python[2005927]: [referto] KERNELUSDT gen_c647ead7: a favore fino a 0.75R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
Oct 07 03:58:48 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 07 03:58:48 Trading-Agent python[2005927]: [learning] filtrati 15/340 trade (esplorativi: 12 · short_duration: 3)
Oct 07 03:58:48 Trading-Agent python[2005927]: [main] pesi ricalcolati: 200 coppie strat×regime da 340 trade (30g)
Oct 07 03:58:49 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 07 03:58:50 Trading-Agent python[2005927]: [price_stream] connesso · 14 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/bmtusdt@bookTicker/cvcusdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/heiusdt@bookTicker/hemiusdt@bookTicker/jasmyusdt@bookTicker/jupusdt@bookTicker/promusdt@bookTicker/rsrusdt@bookTicker/scrusdt@bookTicker/vetusdt@bookTicker/xpinusdt@bookTicker
Oct 07 03:58:50 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 07 04:03:12 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 04:03:12 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 04:03:13 Trading-Agent python[2005927]: [scarti] 6 secondo segnale stessa coin
Oct 07 04:03:13 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:03:13 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:18:15 Trading-Agent python[2005927]: [scarti] 6 secondo segnale stessa coin
Oct 07 04:18:15 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:18:15 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:18:45 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 8591 (rifiutati 4936 · controllo 1426 · registro 1345 · trade 462 · pesi 140 · memoria 94 · deriva 53 · referti 53) — quota gratuita 50000/giorno
Oct 07 04:18:45 Trading-Agent python[2005927]: [learning] filtrati 15/340 trade (esplorativi: 12 · short_duration: 3)
Oct 07 04:18:46 Trading-Agent python[2005927]: [main] pesi ricalcolati: 200 coppie strat×regime da 340 trade (30g)
Oct 07 04:18:46 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 07 04:18:47 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 07 04:18:49 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1766 ms
Oct 07 04:29:18 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 04:29:18 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 04:29:20 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 07 04:33:17 Trading-Agent python[2005927]: [scarti] 6 secondo segnale stessa coin
Oct 07 04:33:17 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 04:33:17 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 04:35:33 Trading-Agent python[2005927]: [DRY_RUN] CLOSE JUPUSDT @ 0.32502797613440504 (stop_loss)
Oct 07 04:35:33 Trading-Agent python[2005927]: [referto] JUPUSDT gen_938d15dc: a favore fino a 0.33R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Oct 07 04:35:33 Trading-Agent python[2005927]: [DRY_RUN] CLOSE CVCUSDT @ 0.0291016225336769 (stop_loss)
Oct 07 04:35:33 Trading-Agent python[2005927]: [referto] CVCUSDT gen_4c4dac5f: a favore fino a 0.30R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
Oct 07 04:35:37 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 04:35:37 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 04:35:40 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 07 04:35:40 Trading-Agent python[2005927]: [learning] filtrati 16/342 trade (esplorativi: 13 · short_duration: 3)
Oct 07 04:35:40 Trading-Agent python[2005927]: [main] pesi ricalcolati: 201 coppie strat×regime da 342 trade (30g)
Oct 07 04:35:40 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 07 04:35:41 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 07 04:35:42 Trading-Agent python[2005927]: [price_stream] connesso · 12 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/heiusdt@bookTicker/hemiusdt@bookTicker/jasmyusdt@bookTicker/promusdt@bookTicker/rsrusdt@bookTicker/scrusdt@bookTicker/vetusdt@bookTicker/xpinusdt@bookTicker
Oct 07 04:47:59 Trading-Agent python[2005927]: /root/agentic_trading_system

[... 3474 caratteri omessi (testa e coda conservate) ...]

ng-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 07 05:03:00 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 05:03:00 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 05:03:01 Trading-Agent python[2005927]: [scarti] 6 secondo segnale stessa coin, 1 esplorativa dietro una validata
Oct 07 05:03:01 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_60c9259a long: posizione gia' aperta su questa coin
Oct 07 05:03:01 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_96efce1b long: posizione gia' aperta su questa coin
Oct 07 05:03:34 Trading-Agent python[2005927]: [DRY_RUN] CLOSE PROMUSDT @ 5.386292648644407 (stop_loss)
Oct 07 05:03:34 Trading-Agent python[2005927]: [referto] PROMUSDT gen_cd5c842f: a favore fino a 0.46R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 07 05:03:38 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 07 05:03:38 Trading-Agent python[2005927]: [learning] filtrati 16/344 trade (esplorativi: 13 · short_duration: 3)
Oct 07 05:03:39 Trading-Agent python[2005927]: [main] pesi ricalcolati: 202 coppie strat×regime da 344 trade (30g)
Oct 07 05:03:39 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 07 05:03:40 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 07 05:03:43 Trading-Agent python[2005927]: [price_stream] connesso · 12 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/heiusdt@bookTicker/hemiusdt@bookTicker/jasmyusdt@bookTicker/pundixusdt@bookTicker/rsrusdt@bookTicker/scrusdt@bookTicker/vetusdt@bookTicker/xpinusdt@bookTicker
Oct 07 05:07:00 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 07 05:18:18 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 05:18:18 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 05:18:52 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 07 05:18:57 Trading-Agent python[2005927]: [rifiutati] 2 segnali rifiutati valutati
Oct 07 05:18:57 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 8674 (rifiutati 4995 · controllo 1426 · registro 1358 · trade 460 · pesi 146 · memoria 94 · deriva 55 · referti 55) — quota gratuita 50000/giorno
Oct 07 05:18:57 Trading-Agent python[2005927]: [learning] filtrati 16/344 trade (esplorativi: 13 · short_duration: 3)
Oct 07 05:18:58 Trading-Agent python[2005927]: [main] pesi ricalcolati: 202 coppie strat×regime da 344 trade (30g)
Oct 07 05:18:58 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 07 05:18:59 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 07 05:19:01 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1964 ms
Oct 07 05:33:05 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 05:33:05 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 05:33:09 Trading-Agent python[2005927]: [selettore] BULLAUSDT gen_5a52c06b long p=0.65 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 07 05:33:09 Trading-Agent python[2005927]: [DRY_RUN] OPEN long BULLAUSDT qty=1104.9942 @ 0.08275 lev=1.0x SL=0.0816 TP=0.0850
Oct 07 05:33:15 Trading-Agent python[2005927]: [price_stream] connesso · 13 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/bmtusdt@bookTicker/bullausdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/heiusdt@bookTicker/hemiusdt@bookTicker/jasmyusdt@bookTicker/pundixusdt@bookTicker/rsrusdt@bookTicker/scrusdt@bookTicker/vetusdt@bookTicker/xpinusdt@bookTicker
Oct 07 05:34:30 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 07 05:48:08 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 05:48:08 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 05:48:09 Trading-Agent python[2005927]: [selettore] SYRUPUSDT gen_f3b97917 long p=0.58 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 07 05:48:09 Trading-Agent python[2005927]: [DRY_RUN] OPEN long SYRUPUSDT qty=693.0903 @ 0.23877 lev=2.0x SL=0.2346 TP=0.2514
Oct 07 05:48:09 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 07 05:48:15 Trading-Agent python[2005927]: [price_stream] connesso · 14 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/bmtusdt@bookTicker/bullausdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/heiusdt@bookTicker/hemiusdt@bookTicker/jasmyusdt@bookTicker/pundixusdt@bookTicker/rsrusdt@bookTicker/scrusdt@bookTicker/syrupusdt@bookTicker/vetusdt@bookTicker/xpinusdt@bookTicker
Oct 07 05:49:52 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 07 06:03:08 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 07 06:03:08 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 07 06:03:08 Trading-Agent python[2005927]: [rifiuto] SYRUPUSDT gen_f3b97917 long: posizione gia' aperta su questa coin
Oct 07 06:03:08 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 07 06:04:15 Trading-Agent python[2005927]: [DRY_RUN] CLOSE BMTUSDT @ 0.01863119380612018 (stop_loss)
Oct 07 06:04:15 Trading-Agent python[2005927]: [referto] BMTUSDT gen_571cdda2: a favore fino a 0.55R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Oct 07 06:04:22 Trading-Agent python[2005927]: [learning] filtrati 16/345 trade (esplorativi: 13 · short_duration: 3)
Oct 07 06:04:22 Trading-Agent python[2005927]: [price_stream] connesso · 13 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/bullausdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/heiusdt@bookTicker/hemiusdt@bookTicker/jasmyusdt@bookTicker/pundixusdt@bookTicker/rsrusdt@bookTicker/scrusdt@bookTicker/syrupusdt@bookTicker/vetusdt@bookTicker/xpinusdt@bookTicker
Oct 07 06:04:22 Trading-Agent python[2005927]: [main] pesi ricalcolati: 202 coppie strat×regime da 345 trade (30g)
Oct 07 06:04:23 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 07 06:04:24 Trading-Agent python[2005927]: [referti] 9 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4) | gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
```
