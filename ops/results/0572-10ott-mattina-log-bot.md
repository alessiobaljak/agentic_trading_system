# 0572-10ott-mattina-log-bot.req

_eseguito: 2026-10-10 03:47 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.2s

```
Oct 09 23:49:55 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 09 23:49:55 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 10 00:02:38 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 00:02:38 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 00:10:18 Trading-Agent python[2005927]: [DRY_RUN] CLOSE PUNDIXUSDT @ 0.11329522960296791 (stop_loss)
Oct 10 00:10:18 Trading-Agent python[2005927]: [referto] PUNDIXUSDT gen_96c1ed1b: mai andato a favore (mfe 0.00R): direzione sbagliata
Oct 10 00:10:18 Trading-Agent python[2005927]: [main] strategia gen_96c1ed1b: 3 stop consecutivi (panchina spenta in parita': continua a operare)
Oct 10 00:10:20 Trading-Agent python[2005927]: [learning] filtrati 21/438 trade (esplorativi: 18 · short_duration: 3)
Oct 10 00:10:21 Trading-Agent python[2005927]: [main] pesi ricalcolati: 251 coppie strat×regime da 438 trade (30g)
Oct 10 00:10:21 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 10 00:10:22 Trading-Agent python[2005927]: [referti] 11 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 10 00:17:52 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 00:17:52 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 00:25:28 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 10 00:32:59 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 00:32:59 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 00:33:00 Trading-Agent python[2005927]: [selettore] AVAAIUSDT gen_8b91ba18 short p=0.68 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 10 00:33:00 Trading-Agent python[2005927]: [DRY_RUN] OPEN short AVAAIUSDT qty=8236.7086 @ 0.008786 lev=2.0x SL=0.0090 TP=0.0084
Oct 10 00:33:00 Trading-Agent python[2005927]: [esplorativa] AVAAIUSDT gen_8b91ba18 short size x0.25
Oct 10 00:33:01 Trading-Agent python[2005927]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker
Oct 10 00:33:09 Trading-Agent python[2005927]: [selettore] CATIUSDT gen_b3e46005 long p=0.64 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 10 00:33:09 Trading-Agent python[2005927]: [DRY_RUN] OPEN long CATIUSDT qty=2762.4055 @ 0.06462 lev=2.0x SL=0.0639 TP=0.0657
Oct 10 00:33:16 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker/catiusdt@bookTicker
Oct 10 00:39:18 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 16630 (rifiutati 13065 · registro 1346 · controllo 1302 · trade 539 · pesi 142 · memoria 95 · deriva 43 · referti 43) — quota gratuita 50000/giorno
Oct 10 00:39:18 Trading-Agent python[2005927]: [learning] filtrati 21/438 trade (esplorativi: 18 · short_duration: 3)
Oct 10 00:39:19 Trading-Agent python[2005927]: [main] pesi ricalcolati: 251 coppie strat×regime da 438 trade (30g)
Oct 10 00:39:19 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 10 00:39:20 Trading-Agent python[2005927]: [referti] 11 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 10 00:39:22 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 1 anomalie, 1713 ms
Oct 10 00:40:58 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 10 00:40:58 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 00:40:58 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 00:47:37 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 00:47:37 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 00:47:38 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 10 00:47:39 Trading-Agent python[2005927]: [selettore] XPINUSDT gen_f311acf9 short p=0.73 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 10 00:47:39 Trading-Agent python[2005927]: [DRY_RUN] OPEN short XPINUSDT qty=105500.3798 @ 0.000846 lev=1.0x SL=0.0009 TP=0.0008
Oct 10 00:47:46 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker/catiusdt@bookTicker/xpinusdt@bookTicker
Oct 10 01:02:39 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 01:02:39 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 01:03:10 Trading-Agent python[2005927]: [DRY_RUN] CLOSE XPINUSDT @ 0.0008424249999999999 (trailing_stop)
Oct 10 01:03:13 Trading-Agent python[2005927]: [learning] filtrati 21/439 trade (esplorativi: 18 · short_duration: 3)
Oct 10 01:03:13 Trading-Agent python[2005927]: [main] pesi ricalcolati: 252 coppie strat×regime da 439 trade (30g)
Oct 10 01:03:14 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 10 01:03:14 Trading-Agent python[2005927]: [referti] 11 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 10 01:03:17 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=avaaiusdt@bookTicker/catiusdt@bookTicker
Oct 10 01:10:25 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 10 01:18:05 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 

[... 5522 caratteri omessi (testa e coda conservate) ...]

/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 01:47:53 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 01:48:56 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 10 02:02:47 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 02:02:47 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 02:04:22 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 2 trade paper
Oct 10 02:17:39 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 02:17:39 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 02:33:04 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 02:33:04 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 02:33:05 Trading-Agent python[2005927]: [selettore] BULLAUSDT gen_7ac562e3 short p=0.66 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 10 02:33:05 Trading-Agent python[2005927]: [DRY_RUN] OPEN short BULLAUSDT qty=668.5066 @ 0.08517 lev=2.0x SL=0.0867 TP=0.0822
Oct 10 02:33:05 Trading-Agent python[2005927]: [declassata] BULLAUSDT gen_7ac562e3 short size x0.25
Oct 10 02:33:12 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/avaaiusdt@bookTicker/bullausdt@bookTicker
Oct 10 02:39:52 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 16641 (rifiutati 13071 · registro 1357 · controllo 1302 · trade 538 · pesi 140 · memoria 95 · deriva 42 · referti 42) — quota gratuita 50000/giorno
Oct 10 02:39:52 Trading-Agent python[2005927]: [learning] filtrati 21/440 trade (esplorativi: 18 · short_duration: 3)
Oct 10 02:39:52 Trading-Agent python[2005927]: [main] pesi ricalcolati: 252 coppie strat×regime da 440 trade (30g)
Oct 10 02:39:53 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 10 02:39:54 Trading-Agent python[2005927]: [referti] 11 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 10 02:39:56 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 2 anomalie, 1584 ms
Oct 10 02:47:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 02:47:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 02:47:44 Trading-Agent python[2005927]: [scarti] 5 secondo segnale stessa coin
Oct 10 02:47:45 Trading-Agent python[2005927]: [selettore] UBUSDT gen_0d7be682 long p=0.57 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 10 02:47:45 Trading-Agent python[2005927]: [DRY_RUN] OPEN long UBUSDT qty=553.3056 @ 0.14207 lev=1.0x SL=0.1400 TP=0.1462
Oct 10 02:47:45 Trading-Agent python[2005927]: [declassata] UBUSDT gen_0d7be682 long size x0.25
Oct 10 02:47:51 Trading-Agent python[2005927]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=asterusdt@bookTicker/avaaiusdt@bookTicker/bullausdt@bookTicker/ubusdt@bookTicker
Oct 10 03:02:51 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 03:02:51 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 03:02:52 Trading-Agent python[2005927]: [scarti] 5 secondo segnale stessa coin
Oct 10 03:02:52 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_0d7be682 long: posizione gia' aperta su questa coin
Oct 10 03:04:56 Trading-Agent python[2005927]: [main] market scan...
Oct 10 03:07:18 Trading-Agent python[2005927]: [scanner] 7 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 10 03:07:18 Trading-Agent python[2005927]: [main] valutate 77 coin validate (77 nel registro): ['GALAUSDT', 'NEIROUSDT', 'TRUMPUSDT', 'AKTUSDT', 'GUNUSDT', 'WALUSDT', 'QUSDT', 'AINUSDT', 'BRUSDT', 'DOTUSDT', '1000PEPEUSDT', 'HYPEUSDT', 'ENAUSDT', 'VETUSDT', '1000BONKUSDT', 'PNUTUSDT', 'MYXUSDT', 'HUMAUSDT', 'SUIUSDT', 'ASTERUSDT', 'OPENUSDT', 'AIOUSDT', 'USELESSUSDT', 'TAOUSDT', 'CVCUSDT', 'SKYAIUSDT', 'STXUSDT', 'HEIUSDT', 'PARTIUSDT', 'SAHARAUSDT', 'ARKMUSDT', 'SYRUPUSDT', 'BMTUSDT', 'PUMPUSDT', 'MUBARAKUSDT', 'SUPERUSDT', 'FORMUSDT', 'GRASSUSDT', 'JUPUSDT', 'THEUSDT', 'MAVIAUSDT', 'GPSUSDT', 'ORCAUSDT', 'RENDERUSDT', 'BIOUSDT', 'FLOCKUSDT', 'KERNELUSDT', 'PLUMEUSDT', 'HEMIUSDT', 'AVAAIUSDT', 'ZECUSDT', '0GUSDT', 'ZORAUSDT', 'RAYSOLUSDT', 'MTLUSDT', 'SCRUSDT', 'BULLAUSDT', 'CATIUSDT', 'XPINUSDT', 'CROSSUSDT', 'GRIFFAINUSDT', 'RUNEUSDT', 'IDOLUSDT', 'DEXEUSDT', 'PUNDIXUSDT', 'BSVUSDT', 'MITOUSDT', 'SOPHUSDT', 'PTBUSDT', 'UBUSDT', 'BANKUSDT', 'BTRUSDT', 'IDUSDT', 'STEEMUSDT', 'HUSDT', 'ONGUSDT', 'TAUSDT']
Oct 10 03:07:52 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 10 03:07:52 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 03:07:52 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 03:17:42 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 03:17:42 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 03:22:58 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 10 03:32:52 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 10 03:32:52 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 10 03:40:16 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 16811 (rifiutati 13241 · registro 1358 · controllo 1302 · trade 541 · pesi 138 · memoria 95 · deriva 41 · referti 41) — quota gratuita 50000/giorno
Oct 10 03:40:16 Trading-Agent python[2005927]: [learning] filtrati 21/440 trade (esplorativi: 18 · short_duration: 3)
Oct 10 03:40:16 Trading-Agent python[2005927]: [main] pesi ricalcolati: 252 coppie strat×regime da 440 trade (30g)
Oct 10 03:40:17 Trading-Agent python[2005927]: [drift] 1 coppie in deriva confermata -> size/leva frenate, evidenza al gate alla prossima passata
Oct 10 03:40:18 Trading-Agent python[2005927]: [referti] 11 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3) | gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3) | gen_bf2be656: solo_short — long 3/3 persi (campione 3) | gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5) | gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3) | gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4) | gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4) | gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3) | gen_fa304106: solo_long — short 5/5 persi (campione 5) | gen_fa304106: solo_short — long 6/6 persi (campione 6) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 10 03:40:20 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 2 anomalie, 1735 ms
```
