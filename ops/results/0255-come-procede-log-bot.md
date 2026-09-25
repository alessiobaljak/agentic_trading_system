# 0255-come-procede-log-bot.req

_eseguito: 2026-09-25 19:38 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 25 13:47:15 Trading-Agent python[1682472]: [selettore] ZORAUSDT gen_2c248ee9 long p=0.61 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 13:47:15 Trading-Agent python[1682472]: [DRY_RUN] OPEN long ZORAUSDT qty=10589.3045 @ 0.008816 lev=1.0x SL=0.0087 TP=0.0091
Sep 25 13:47:15 Trading-Agent python[1682472]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (34m)
Sep 25 13:47:17 Trading-Agent python[1682472]: [selettore] SUIUSDT gen_490a90e5 short p=0.79 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 13:47:17 Trading-Agent python[1682472]: [DRY_RUN] OPEN short SUIUSDT qty=69.7082 @ 1.1272 lev=2.0x SL=1.1624 TP=1.0743
Sep 25 13:47:24 Trading-Agent python[1682472]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=suiusdt@bookTicker/uselessusdt@bookTicker/zorausdt@bookTicker
Sep 25 13:47:29 Trading-Agent python[1682472]: [ai-shadow] ok in 12.3s · 875+609 token
Sep 25 14:08:46 Trading-Agent python[1682472]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 14:08:46 Trading-Agent python[1682472]:   return query.where(field_path, op_string, value)
Sep 25 14:08:47 Trading-Agent python[1682472]: [main] pesi ricalcolati: 47 coppie strat×regime da 76 trade (30g)
Sep 25 14:08:47 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 14:08:52 Trading-Agent python[1682472]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 4718 ms
Sep 25 14:12:05 Trading-Agent python[1682472]: [DRY_RUN] CLOSE SUIUSDT @ 1.1101 (trailing_stop)
Sep 25 14:12:09 Trading-Agent python[1682472]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 14:12:09 Trading-Agent python[1682472]:   return query.where(field_path, op_string, value)
Sep 25 14:12:09 Trading-Agent python[1682472]: [main] pesi ricalcolati: 47 coppie strat×regime da 77 trade (30g)
Sep 25 14:12:10 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 14:12:14 Trading-Agent python[1682472]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=uselessusdt@bookTicker/zorausdt@bookTicker
Sep 25 14:17:04 Trading-Agent python[1682472]: [selettore] XMRUSDT gen_35632db9 long p=0.65 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 14:17:04 Trading-Agent python[1682472]: [DRY_RUN] OPEN long XMRUSDT qty=0.1703 @ 548.93 lev=1.0x SL=537.2111 TP=566.5084
Sep 25 14:17:11 Trading-Agent python[1682472]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=uselessusdt@bookTicker/xmrusdt@bookTicker/zorausdt@bookTicker
Sep 25 14:17:13 Trading-Agent python[1682472]: [ai-shadow] ok in 9.1s · 782+442 token
Sep 25 14:32:30 Trading-Agent python[1682472]: [DRY_RUN] CLOSE USELESSUSDT @ 0.3004375 (trailing_stop)
Sep 25 14:32:34 Trading-Agent python[1682472]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 14:32:34 Trading-Agent python[1682472]:   return query.where(field_path, op_string, value)
Sep 25 14:32:35 Trading-Agent python[1682472]: [main] pesi ricalcolati: 48 coppie strat×regime da 78 trade (30g)
Sep 25 14:32:35 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 14:32:37 Trading-Agent python[1682472]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=xmrusdt@bookTicker/zorausdt@bookTicker
Sep 25 14:40:51 Trading-Agent python[1682472]: [DRY_RUN] CLOSE ZORAUSDT @ 0.008862695 (trailing_stop)
Sep 25 14:40:57 Trading-Agent python[1682472]: [main] pesi ricalcolati: 49 coppie strat×regime da 79 trade (30g)
Sep 25 14:40:57 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 14:40:58 Trading-Agent python[1682472]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=xmrusdt@bookTicker
Sep 25 14:47:17 Trading-Agent python[1682472]: [selettore] MUBARAKUSDT gen_1f7ead60 short p=0.68 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 14:47:17 Trading-Agent python[1682472]: [DRY_RUN] OPEN short MUBARAKUSDT qty=1838.9893 @ 0.05094 lev=1.0x SL=0.0528 TP=0.0453
Sep 25 14:47:23 Trading-Agent python[1682472]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/xmrusdt@bookTicker
Sep 25 14:47:34 Trading-Agent python[1682472]: [ai-shadow] ok in 8.5s · 792+419 token
Sep 25 15:08:55 Trading-Agent python[1682472]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 15:08:55 Trading-Agent python[1682472]:   return query.where(field_path, op_string, value)
Sep 25 15:08:56 Trading-Agent python[1682472]: [main] pesi ricalcolati: 49 coppie strat×regime da 79 trade (30g)
Sep 25 15:08:56 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 15:09:04 Trading-Agent python[1682472]: [controllo] pubblicato: sistema giallo, paper giallo, 5 anomalie, 7350 ms
Sep 25 15:25:23 Trading-Agent python[1682472]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.05281263850577525 (stop_loss)
Sep 25 15:25:23 Trading-Agent python[1682472]: [referto] MUBARAKUSDT gen_1f7ead60: mai andato a favore (mfe 0.21R): direzione sbagliata
Sep 25 15:25:29 Trading-Agent python[1682472]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=xmrusdt@bookTicker
Sep 25 15:25:35 Trading-Agent python[1682472]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 15:25:35 Trading-Agent python[1682472]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 15:25:35 Trading-Agent python[1682472]:   return query.where(field_path, op_string, value)
Sep 25 15:25:36 Trading-Agent python[1682472]: [main] pesi ricalcolati: 49 coppie strat×regime da 80 trade (30g)
Sep 25 15:25:36 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 15:31:50 Trading-Agent python[1682472]: [rifiuto] MUBARAKUSDT gen_1f7ead60 short: cooldown dopo stop (55m)
Sep 25 15:31:59 Trading-Agent python[1682472]: [ai-shadow] ok in 8.8s · 793+432 token
Sep 25 16:08:42 Trading-Agent python[1682472]: [main] market scan...
Sep 25 16:10:19 Trading-Agent python[1682472]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 16:10:19 Trading-Agent python[1682472]:   return query.where(field_path, op_string, value)
Sep 25 16:10:19 Trading-Agent python[1682472]: [main] valutate 52 coin validate (52 nel registro): ['SCRUSDT', 'ENAUSDT', 'PLUMEUSDT', 'MUBARAKUSDT', 'PROMUSDT', 'SEIUSDT', 'AXSUSDT', 'BTRUSDT', 'ZKUSDT', 'HUMAUSDT', 'HEIUSDT', 'PHAUSDT', 'XPLUSDT', 'USELESSUSDT', 'PENGUUSDT', 'JUPUSDT', 'SPXUSDT', 'QUSDT', 'XRPUSDT', 'ARCUSDT', 'SUIUSDT', 'AVAAIUSDT', 'RAYSOLUSDT', 'XMRUSDT', 'JTOUSDT', 'ATOMUSDT', 'SAHARAUSDT', 'B2USDT', 'EPICUSDT', 'TSTUSDT', 'DOTUSDT', 'DEXEUSDT', 'GALAUSDT', 'TRUMPUSDT', 'TUTUSDT', 'RENDERUSDT', 'VETUSDT', 'ZORAUSDT', 'BULLAUSDT', 'HEMIUSDT', 'PNUTUSDT', 'EGLDUSDT', 'SYRUPUSDT', 'NEIROUSDT', 'STXUSDT', 'GPSUSDT', 'JASMYUSDT', 'RSRUSDT', 'ORCAUSDT', 'SKYAIUSDT', 'BICOUSDT', 'HOMEUSDT']
Sep 25 16:10:54 Trading-Agent python[1682472]: [main] pesi ricalcolati: 49 coppie strat×regime da 80 trade (30g)
Sep 25 16:10:55 Trading-Agent python[1682472]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 16:10:58 Trading-Agent python[1682472]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 2993 ms
Sep 25 16:16:50 Trading-Agent python[1682472]: [rifiuto] MUBARAKUSDT gen_2053cba6 short: cooldown dopo stop (10m)
Sep 25 16:16:59 Trading-Agent python[1682472]: [ai-shadow] ok in 9.5s · 839+559 token
Sep 25 16:26:15 Trading-Agent python[1682472]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 16:29:26 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 25 16:29:26 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 25 16:29:26 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 25 16:29:26 Trading-Agent systemd[1]: trading-bot.service: Consumed 19min 38.046s CPU time.
Sep 25 16:29:26 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 25 16:29:28 Trading-Agent python[1688981]: [firebase] connesso (Firestore + RTDB)
Sep 25 16:29:29 Trading-Agent python[1688981]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['XMRUSDT']
Sep 25 16:29:29 Trading-Agent python[1688981]: [main] avvio bot @ 2026-09-25T16:29:29.054282+00:00 DRY_RUN=True
Sep 25 16:29:29 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 16:29:29 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 16:29:29 Trading-Agent python[1688981]: [main] equity riconciliata: 933.24 (base 1000.00 + realizzato -66.76 + fette aperte +0.00)
Sep 25 16:29:29 Trading-Agent python[1688981]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 25 16:29:29 Trading-Agent python[1688981]: [selettore] modello caricato: 41404 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-09-25T12:08:12.711365+00:00 -> solo ombra, non decide
Sep 25 16:29:30 Trading-Agent python[1688981]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=xmrusdt@bookTicker
Sep 25 16:29:41 Trading-Agent python[1688981]: [main] pesi ricalcolati: 49 coppie strat×regime da 80 trade (30g)
Sep 25 16:29:41 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 16:29:43 Trading-Agent python[1688981]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1580 ms
Sep 25 16:29:46 Trading-Agent python[1688981]: [main] market scan...
Sep 25 16:31:26 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 16:31:26 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 16:31:27 Trading-Agent python[1688981]: [main] valutate 52 coin validate (52 nel registro): ['MUBARAKUSDT', 'PROMUSDT', 'ENAUSDT', 'ZKUSDT', 'SYRUPUSDT', 'AXSUSDT', 'HEMIUSDT', 'BTRUSDT', 'PLUMEUSDT', 'XPLUSDT', 'PHAUSDT', 'SCRUSDT', 'SEIUSDT', 'JTOUSDT', 'HUMAUSDT', 'GALAUSDT', 'TRUMPUSDT', 'PENGUUSDT', 'JUPUSDT', 'AVAAIUSDT', 'SUIUSDT', 'ARCUSDT', 'NEIROUSDT', 'HEIUSDT', 'QUSDT', 'XMRUSDT', 'XRPUSDT', 'BICOUSDT', 'RAYSOLUSDT', 'SPXUSDT', 'ATOMUSDT', 'PNUTUSDT', 'DOTUSDT', 'B2USDT', 'EGLDUSDT', 'USELESSUSDT', 'STXUSDT', 'RENDERUSDT', 'ORCAUSDT', 'VETUSDT', 'TUTUSDT', 'RSRUSDT', 'BULLAUSDT', 'DEXEUSDT', 'ZORAUSDT', 'TSTUSDT', 'SAHARAUSDT', 'JASMYUSDT', 'HOMEUSDT', 'GPSUSDT', 'EPICUSDT', 'SKYAIUSDT']
Sep 25 16:33:11 Trading-Agent python[1688981]: [selettore] MUBARAKUSDT gen_49c2f657 short p=0.67 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 16:33:11 Trading-Agent python[1688981]: [DRY_RUN] OPEN short MUBARAKUSDT qty=1285.1122 @ 0.05372 lev=1.0x SL=0.0563 TP=0.0459
Sep 25 16:33:18 Trading-Agent python[1688981]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/xmrusdt@bookTicker
Sep 25 16:33:21 Trading-Agent python[1688981]: [ai-shadow] ok in 9.5s · 792+443 token
Sep 25 16:35:36 Trading-Agent python[1688981]: [rifiuto] MUBARAKUSDT gen_49c2f657 short: posizione gia' aperta su questa coin
Sep 25 16:35:44 Trading-Agent python[1688981]: [ai-shadow] ok in 8.1s · 792+421 token
Sep 25 16:48:23 Trading-Agent python[1688981]: [DRY_RUN] CLOSE XMRUSDT @ 553.8525 (trailing_stop)
Sep 25 16:48:32 Trading-Agent python[1688981]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker
Sep 25 16:48:36 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 16:48:36 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 16:48:36 Trading-Agent python[1688981]: [main] pesi ricalcolati: 50 coppie strat×regime da 81 trade (30g)
Sep 25 16:48:37 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 17:14:54 Trading-Agent python[1688981]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.051657499999999995 (trailing_stop)
Sep 25 17:14:58 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 17:14:58 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 17:14:59 Trading-Agent python[1688981]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 17:14:59 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 17:29:48 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 17:29:48 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 17:29:48 Trading-Agent python[1688981]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 17:29:49 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 17:29:51 Trading-Agent python[1688981]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1826 ms
Sep 25 18:29:54 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 18:29:54 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 18:29:55 Trading-Agent python[1688981]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 18:29:55 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 18:29:57 Trading-Agent python[1688981]: [controllo] pubblicato: sistema giallo, paper giallo, 5 anomalie, 1679 ms
Sep 25 19:01:55 Trading-Agent python[1688981]: [selettore] QUSDT gen_bf2be656 long p=0.71 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 19:01:55 Trading-Agent python[1688981]: [DRY_RUN] OPEN long QUSDT qty=3822.2048 @ 0.024503 lev=1.0x SL=0.0240 TP=0.0261
Sep 25 19:01:56 Trading-Agent python[1688981]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=qusdt@bookTicker
Sep 25 19:02:03 Trading-Agent python[1688981]: [ai-shadow] ok in 7.6s · 789+382 token
Sep 25 19:19:41 Trading-Agent python[1688981]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 19:30:23 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 19:30:23 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 19:30:23 Trading-Agent python[1688981]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 19:30:24 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 19:30:26 Trading-Agent python[1688981]: [controllo] pubblicato: sistema giallo, paper giallo, 5 anomalie, 1714 ms
Sep 25 19:34:48 Trading-Agent python[1688981]: [main] verdetto trailing assegnato a 1 trade paper
```
