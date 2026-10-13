# 0617-13ott-log-bot-avvio-nuovo-codice.req

_eseguito: 2026-10-13 18:12 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.2s

```
Oct 13 15:33:05 Trading-Agent python[2005927]: [scarti] 7 secondo segnale stessa coin
Oct 13 15:33:06 Trading-Agent python[2005927]: [selettore] BULLAUSDT gen_99c9c036 long p=0.53 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 13 15:33:06 Trading-Agent python[2005927]: [DRY_RUN] OPEN long BULLAUSDT qty=1085.2269 @ 0.07967 lev=1.0x SL=0.0766 TP=0.0873
Oct 13 15:33:07 Trading-Agent python[2005927]: [selettore] PTBUSDT gen_e7a69c97 short p=0.65 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 13 15:33:07 Trading-Agent python[2005927]: [DRY_RUN] OPEN short PTBUSDT qty=74660.5670 @ 0.0008243 lev=1.0x SL=0.0008 TP=0.0008
Oct 13 15:33:07 Trading-Agent python[2005927]: [esplorativa] PTBUSDT gen_e7a69c97 short size x0.25
Oct 13 15:33:08 Trading-Agent python[2005927]: [selettore] SKYAIUSDT gen_eb2ece0c short p=0.60 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 13 15:33:08 Trading-Agent python[2005927]: [DRY_RUN] OPEN short SKYAIUSDT qty=2652.1480 @ 0.0326 lev=1.0x SL=0.0331 TP=0.0316
Oct 13 15:33:12 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=bullausdt@bookTicker/ptbusdt@bookTicker/scrusdt@bookTicker/skyaiusdt@bookTicker
Oct 13 15:35:45 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 13 15:41:41 Trading-Agent python[2005927]: [DRY_RUN] CLOSE PTBUSDT @ 0.0008184500000000001 (trailing_stop)
Oct 13 15:41:45 Trading-Agent python[2005927]: [learning] filtrati 45/570 trade (esplorativi: 31 · short_duration: 3 · wrong_timeframe: 11)
Oct 13 15:41:46 Trading-Agent python[2005927]: [main] pesi ricalcolati: 315 coppie strat×regime da 570 trade (30g)
Oct 13 15:41:46 Trading-Agent python[2005927]: [drift] 3 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 13 15:41:47 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bullausdt@bookTicker/scrusdt@bookTicker/skyaiusdt@bookTicker
Oct 13 15:41:47 Trading-Agent python[2005927]: [referti] 16 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_01fbe76f: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_4c6df481: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.79 R) (campione 3) | gen_871647b8: conferma_trend — 3 perdite controtrend (campione 3) | gen_871647b8: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_8b91ba18: scala_stretta — 4 perdite sotto il primo gradino (mfe mediana 0.64 R) (campione 4) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_c647ead7: conferma_trend — 3 perdite controtrend (campione 3) | gen_c647ead7: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.74 R) (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e50a9211: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.45 R) (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 13 15:48:06 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 15:48:06 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 15:48:08 Trading-Agent python[2005927]: [selettore] AINUSDT gen_ef115241 long p=0.61 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 13 15:48:08 Trading-Agent python[2005927]: [DRY_RUN] OPEN long AINUSDT qty=399.4064 @ 0.04367 lev=1.0x SL=0.0417 TP=0.0475
Oct 13 15:48:08 Trading-Agent python[2005927]: [declassata] AINUSDT gen_ef115241 long size x0.25
Oct 13 15:48:15 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/bullausdt@bookTicker/scrusdt@bookTicker/skyaiusdt@bookTicker
Oct 13 15:59:19 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 13 16:03:04 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 16:03:04 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 16:03:05 Trading-Agent python[2005927]: [rifiuto] QUSDT gen_5905e08d short: cooldown dopo stop (78m)
Oct 13 16:03:05 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: posizione gia' aperta su questa coin
Oct 13 16:05:42 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 11798 (rifiutati 7849 · controllo 1364 · registro 1356 · trade 699 · pesi 185 · memoria 93 · deriva 76 · referti 76) — quota gratuita 50000/giorno
Oct 13 16:05:43 Trading-Agent python[2005927]: [learning] filtrati 45/570 trade (esplorativi: 31 · short_duration: 3 · wrong_timeframe: 11)
Oct 13 16:05:43 Trading-Agent python[2005927]: [main] pesi ricalcolati: 315 coppie strat×regime da 570 trade (30g)
Oct 13 16:05:44 Trading-Agent python[2005927]: [drift] 3 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 13 16:05:46 Trading-Agent python[2005927]: [referti] 16 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_01fbe76f: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_4c6df481: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.79 R) (campione 3) | gen_871647b8: conferma_trend — 3 perdite controtrend (campione 3) | gen_871647b8: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_8b91ba18: scala_stretta — 4 perdite sotto il primo gradino (mfe mediana 0.64 R) (campione 4) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_c647ead7: conferma_trend — 3 perdite controtrend (campione 3) | gen_c647ead7: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.74 R) (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e50a9211: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.45 R) (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 13 16:05:54 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 2 anomalie, 7627 ms
Oct 13 16:12:21 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 16:12:21 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 16:12:28 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 13 16:17:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 16:17:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 16:17:46 Trading-Agent python[2005927]: [selettore] AIOUSDT gen_6191df86 short p=0.70 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 13 16:17:46 Trading-Agent python[2005927]: [DRY_RUN] OPEN short AIOUSDT qty=2411.3147 @ 0.03587 lev=1.0x SL=0.0367 TP=0.0334
Oct 13 16:17:56 Trading-Agent python[2005927]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/aiousdt@bookTicker/bullausdt@bookTicker/scrusdt@bookTicker/skyaiusdt@bookTicker
Oct 13 16:42:56 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 16:42:56 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 16:42:59 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 13 16:47:53 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: posizione gia' aperta su questa coin
Oct 13 16:58:00 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 16:58:00 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 16:58:04 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 13 17:02:59 Trading-Agent python[2005927]: [rifiuto] QUSDT gen_5905e08d short:

[... 4632 caratteri omessi (testa e coda conservate) ...]

]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 17:28:32 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 17:28:36 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 13 17:32:53 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 13 17:32:53 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: posizione gia' aperta su questa coin
Oct 13 17:32:53 Trading-Agent python[2005927]: [rifiuto] MUBARAKUSDT gen_2053cba6 long: posizione gia' aperta su questa coin
Oct 13 17:43:43 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 17:43:43 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 17:48:03 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: posizione gia' aperta su questa coin
Oct 13 17:58:54 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 17:58:54 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 18:02:46 Trading-Agent python[2005927]: [selettore] QUSDT gen_5905e08d short p=0.70 soglia=0.40 -> avrebbe aperto (ombra: apre comunque)
Oct 13 18:02:46 Trading-Agent python[2005927]: [DRY_RUN] OPEN short QUSDT qty=429.2407 @ 0.041782 lev=1.0x SL=0.0436 TP=0.0391
Oct 13 18:02:46 Trading-Agent python[2005927]: [declassata] QUSDT gen_5905e08d short size x0.25
Oct 13 18:02:46 Trading-Agent python[2005927]: [rifiuto] JTOUSDT gen_94062d5f long: posizione gia' aperta su questa coin
Oct 13 18:02:46 Trading-Agent python[2005927]: [rifiuto] AINUSDT gen_ef115241 long: posizione gia' aperta su questa coin
Oct 13 18:02:54 Trading-Agent python[2005927]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/aiousdt@bookTicker/bullausdt@bookTicker/jtousdt@bookTicker/mubarakusdt@bookTicker/qusdt@bookTicker/scrusdt@bookTicker/skyaiusdt@bookTicker
Oct 13 18:06:36 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 12218 (rifiutati 8301 · controllo 1364 · registro 1343 · trade 698 · pesi 176 · memoria 93 · deriva 72 · referti 72) — quota gratuita 50000/giorno
Oct 13 18:06:36 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 18:06:36 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 13 18:06:36 Trading-Agent python[2005927]: [learning] filtrati 45/570 trade (esplorativi: 31 · short_duration: 3 · wrong_timeframe: 11)
Oct 13 18:06:37 Trading-Agent python[2005927]: [main] pesi ricalcolati: 315 coppie strat×regime da 570 trade (30g)
Oct 13 18:06:38 Trading-Agent python[2005927]: [drift] 3 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 13 18:06:39 Trading-Agent python[2005927]: [referti] 16 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_01fbe76f: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_4c6df481: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.79 R) (campione 3) | gen_871647b8: conferma_trend — 3 perdite controtrend (campione 3) | gen_871647b8: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_8b91ba18: scala_stretta — 4 perdite sotto il primo gradino (mfe mediana 0.64 R) (campione 4) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_c647ead7: conferma_trend — 3 perdite controtrend (campione 3) | gen_c647ead7: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.74 R) (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e50a9211: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.45 R) (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 13 18:06:41 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 1 anomalie, 1923 ms
Oct 13 18:10:02 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Oct 13 18:10:02 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Oct 13 18:10:02 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Oct 13 18:10:02 Trading-Agent systemd[1]: trading-bot.service: Consumed 11h 4min 11.035s CPU time.
Oct 13 18:10:02 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Oct 13 18:10:05 Trading-Agent python[2564596]: [firebase] connesso (Firestore + RTDB)
Oct 13 18:10:07 Trading-Agent python[2564596]: [execution] ricaricate 8 posizioni aperte da Firebase (no orfani al riavvio): ['AINUSDT', 'AIOUSDT', 'BULLAUSDT', 'JTOUSDT', 'MUBARAKUSDT', 'QUSDT', 'SCRUSDT', 'SKYAIUSDT']
Oct 13 18:10:07 Trading-Agent python[2564596]: [main] avvio bot @ 2026-10-13T18:10:07.347923+00:00 DRY_RUN=True
Oct 13 18:10:08 Trading-Agent python[2564596]: [main] equity riconciliata: 864.94 (base 1000.00 + realizzato -135.06 + fette aperte +0.00)
Oct 13 18:10:09 Trading-Agent python[2564596]: [main] versione dell'avvio: commit d5939a7, config a3508539a199
Oct 13 18:10:09 Trading-Agent python[2564596]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina (spenta in parita': non si applica)
Oct 13 18:10:09 Trading-Agent python[2564596]: [selettore] modello caricato: 150015 righe, soglia 0.40, verdetto NON BATTE, stato ombra, generato 2026-10-12T17:49:35.922866+00:00 -> solo ombra, non decide
Oct 13 18:10:10 Trading-Agent python[2564596]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=ainusdt@bookTicker/aiousdt@bookTicker/bullausdt@bookTicker/jtousdt@bookTicker/mubarakusdt@bookTicker/qusdt@bookTicker/scrusdt@bookTicker/skyaiusdt@bookTicker
Oct 13 18:10:21 Trading-Agent python[2564596]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 18:10:21 Trading-Agent python[2564596]:   return query.where(field_path, op_string, value)
Oct 13 18:10:24 Trading-Agent python[2564596]: [firebase] letture ultime 24 h: 704 (trade 570 · rifiutati 127 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Oct 13 18:10:24 Trading-Agent python[2564596]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 13 18:10:24 Trading-Agent python[2564596]:   q = q.where(order_by, "<=", max_value)
Oct 13 18:10:24 Trading-Agent python[2564596]: [learning] filtrati 45/570 trade (esplorativi: 31 · short_duration: 3 · wrong_timeframe: 11)
Oct 13 18:10:25 Trading-Agent python[2564596]: [main] pesi ricalcolati: 315 coppie strat×regime da 570 trade (30g)
Oct 13 18:10:25 Trading-Agent python[2564596]: [drift] 3 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 13 18:10:26 Trading-Agent python[2564596]: [referti] 16 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_01fbe76f: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_4c6df481: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.79 R) (campione 3) | gen_871647b8: conferma_trend — 3 perdite controtrend (campione 3) | gen_871647b8: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_8b91ba18: scala_stretta — 4 perdite sotto il primo gradino (mfe mediana 0.64 R) (campione 4) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_c647ead7: conferma_trend — 3 perdite controtrend (campione 3) | gen_c647ead7: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.74 R) (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e50a9211: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.45 R) (campione 3) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 13 18:10:29 Trading-Agent python[2564596]: [controllo] pubblicato: sistema verde, paper giallo, 1 anomalie, 2067 ms
Oct 13 18:10:29 Trading-Agent python[2564596]: [giorni] riga del 2026-10-12: cicli None/96, aperti None, rifiutati None, riavvii 0
Oct 13 18:10:32 Trading-Agent python[2564596]: [main] market scan...
```
