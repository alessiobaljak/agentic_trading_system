# 0111-verifica-riavvio.req

_eseguito: 2026-09-20 07:40 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.8s

```
Sep 19 17:01:06 Trading-Agent python[1454358]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker/dexeusdt@bookTicker
Sep 19 17:01:11 Trading-Agent python[1454358]: [ai-shadow] ok in 10.5s · 787+504 token
Sep 19 17:06:49 Trading-Agent python[1454358]: [DRY_RUN] CLOSE DEXEUSDT @ 1.870041799023192 (stop_loss)
Sep 19 17:06:51 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 17:06:51 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 17:06:51 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 17:06:51 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 19 17:06:56 Trading-Agent python[1454358]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker
Sep 19 18:06:59 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 18:06:59 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 18:06:59 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 18:06:59 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 19 18:31:31 Trading-Agent python[1454358]: [DRY_RUN] SCALE-OUT 2746.7270 BICOUSDT @ 0.02091963854239197 (netto +1.3625, residuo 6409.0296)
Sep 19 19:07:06 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 19:07:06 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 19:07:06 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 19:07:06 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 19 20:07:18 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 20:07:18 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 20:07:18 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 20:07:18 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 19 20:11:23 Trading-Agent python[1454358]: [main] market scan...
Sep 19 20:12:09 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 20:12:09 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 20:12:09 Trading-Agent python[1454358]: [main] valutate 24 coin validate (24 nel registro): ['JASMYUSDT', 'SEIUSDT', 'USELESSUSDT', 'TUTUSDT', 'STXUSDT', 'JTOUSDT', 'QUSDT', 'SKYAIUSDT', 'VETUSDT', 'EGLDUSDT', 'HEMIUSDT', 'DEXEUSDT', 'ZKUSDT', 'NEIROUSDT', 'DOTUSDT', 'GPSUSDT', 'HEIUSDT', 'PROMUSDT', 'SYRUPUSDT', 'SAHARAUSDT', 'ORCAUSDT', 'SPXUSDT', 'MUBARAKUSDT', 'BICOUSDT']
Sep 19 20:31:08 Trading-Agent python[1454358]: [DRY_RUN] OPEN long DEXEUSDT qty=104.7847 @ 1.873 lev=2.0x SL=1.8473 TP=1.9500
Sep 19 20:31:15 Trading-Agent python[1454358]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker/dexeusdt@bookTicker
Sep 19 20:31:18 Trading-Agent python[1454358]: [ai-shadow] ok in 8.8s · 784+499 token
Sep 19 20:46:08 Trading-Agent python[1454358]: [ai-shadow] ok in 10.8s · 784+543 token
Sep 19 21:01:30 Trading-Agent python[1454358]: [ai-shadow] ok in 9.5s · 786+479 token
Sep 19 21:07:39 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 21:07:39 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 21:07:39 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 21:07:39 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 19 22:07:49 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 22:07:49 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 22:07:50 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 22:07:50 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 19 22:32:31 Trading-Agent python[1454358]: [DRY_RUN] SCALE-OUT 31.4354 DEXEUSDT @ 1.9114828120015959 (netto +1.1155, residuo 73.3493)
Sep 19 22:46:09 Trading-Agent python[1454358]: [DRY_RUN] OPEN short PROMUSDT qty=37.1708 @ 5.286 lev=2.0x SL=5.3546 TP=5.1831
Sep 19 22:46:16 Trading-Agent python[1454358]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker/dexeusdt@bookTicker/promusdt@bookTicker
Sep 19 22:46:27 Trading-Agent python[1454358]: [ai-shadow] ok in 9.6s · 786+472 token
Sep 19 23:07:56 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 23:07:56 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 19 23:07:56 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 19 23:07:56 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 20 00:03:45 Trading-Agent python[1454358]: [price_agent] GET /fapi/v1/premiumIndex fallito: 429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BICOUSDT
Sep 20 00:03:55 Trading-Agent python[1454358]: [price_agent] GET /fapi/v1/premiumIndex fallito: 429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/premiumIndex?symbol=DEXEUSDT
Sep 20 00:08:10 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 00:08:10 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 00:08:10 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 20 00:08:10 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 20 00:11:49 Trading-Agent python[1454358]: [main] market scan...
Sep 20 00:12:35 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 00:12:35 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 00:12:35 Trading-Agent python[1454358]: [main] valutate 24 coin validate (24 nel registro): ['VETUSDT', 'ORCAUSDT', 'JTOUSDT', 'USELESSUSDT', 'EGLDUSDT', 'STXUSDT', 'ZKUSDT', 'GPSUSDT', 'HEIUSDT', 'SAHARAUSDT', 'TUTUSDT', 'QUSDT', 'MUBARAKUSDT', 'DEXEUSDT', 'BICOUSDT', 'PROMUSDT', 'DOTUSDT', 'HEMIUSDT', 'NEIROUSDT', 'JASMYUSDT', 'SEIUSDT', 'SYRUPUSDT', 'SPXUSDT', 'SKYAIUSDT']
Sep 20 01:08:35 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 01:08:35 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 01:08:35 Trading-Agent python[1454358]: [learning] solo 13 trade validi (servono 50): pesi INVARIATI
Sep 20 01:08:35 Trading-Agent python[1454358]: [main] pesi ricalcolati: 10 coppie strat×regime da 13 trade (30g)
Sep 20 01:10:41 Trading-Agent python[1454358]: [DRY_RUN] CLOSE DEXEUSDT @ 1.873 (scale_out)
Sep 20 01:10:43 Trading-Agent python[1454358]: [learning] solo 14 trade validi (servono 50): pesi INVARIATI
Sep 20 01:10:43 Trading-Agent python[1454358]: [main] pesi ricalcolati: 11 coppie strat×regime da 14 trade (30g)
Sep 20 01:10:48 Trading-Agent python[1454358]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker/promusdt@bookTicker
Sep 20 01:41:06 Trading-Agent python[1454358]: [main] verdetto trailing assegnato a 1 trade paper
Sep 20 02:10:55 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 02:10:55 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 02:10:55 Trading-Agent python[1454358]: [learning] solo 14 trade validi (servono 50): pesi INVARIATI
Sep 20 02:10:55 Trading-Agent python[1454358]: [main] pesi ricalcolati: 11 coppie strat×regime da 14 trade (30g)
Sep 20 03:01:17 Trading-Agent python[1454358]: [DRY_RUN] OPEN long SPXUSDT qty=424.6430 @ 0.4626 lev=2.0x SL=0.4520 TP=0.4785
Sep 20 03:01:23 Trading-Agent python[1454358]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker/promusdt@bookTicker/spxusdt@bookTicker
Sep 20 03:01:28 Trading-Agent python[1454358]: [ai-shadow] ok in 10.9s · 829+487 token
Sep 20 03:11:18 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 03:11:18 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 03:11:18 Trading-Agent python[1454358]: [learning] solo 14 trade validi (servono 50): pesi INVARIATI
Sep 20 03:11:18 Trading-Agent python[1454358]: [main] pesi ricalcolati: 11 coppie strat×regime da 14 trade (30g)
Sep 20 03:42:26 Trading-Agent python[1454358]: [DRY_RUN] SCALE-OUT 11.1512 PROMUSDT @ 5.148808235855375 (netto +1.4562, residuo 26.0196)
Sep 20 03:48:21 Trading-Agent python[1454358]: [DRY_RUN] CLOSE BICOUSDT @ 0.02145 (scale_out)
Sep 20 03:48:28 Trading-Agent python[1454358]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker/spxusdt@bookTicker
Sep 20 03:48:31 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 03:48:31 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 03:48:31 Trading-Agent python[1454358]: [learning] solo 15 trade validi (servono 50): pesi INVARIATI
Sep 20 03:48:31 Trading-Agent python[1454358]: [main] pesi ricalcolati: 12 coppie strat×regime da 15 trade (30g)
Sep 20 04:11:54 Trading-Agent python[1454358]: [main] market scan...
Sep 20 04:12:40 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 04:12:40 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 04:12:41 Trading-Agent python[1454358]: [main] valutate 25 coin validate (25 nel registro): ['ZKUSDT', 'BICOUSDT', 'JTOUSDT', 'SPXUSDT', 'EGLDUSDT', 'TRUMPUSDT', 'DOTUSDT', 'STXUSDT', 'USELESSUSDT', 'VETUSDT', 'NEIROUSDT', 'SEIUSDT', 'MUBARAKUSDT', 'HEMIUSDT', 'PROMUSDT', 'SYRUPUSDT', 'HEIUSDT', 'SAHARAUSDT', 'JASMYUSDT', 'SKYAIUSDT', 'DEXEUSDT', 'ORCAUSDT', 'TUTUSDT', 'QUSDT', 'GPSUSDT']
Sep 20 04:48:57 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 04:48:57 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 04:48:57 Trading-Agent python[1454358]: [learning] solo 15 trade validi (servono 50): pesi INVARIATI
Sep 20 04:48:57 Trading-Agent python[1454358]: [main] pesi ricalcolati: 12 coppie strat×regime da 15 trade (30g)
Sep 20 05:49:14 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 05:49:14 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 05:49:14 Trading-Agent python[1454358]: [learning] solo 15 trade validi (servono 50): pesi INVARIATI
Sep 20 05:49:14 Trading-Agent python[1454358]: [main] pesi ricalcolati: 12 coppie strat×regime da 15 trade (30g)
Sep 20 06:49:30 Trading-Agent python[1454358]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 06:49:30 Trading-Agent python[1454358]:   return query.where(field_path, op_string, value)
Sep 20 06:49:31 Trading-Agent python[1454358]: [learning] solo 15 trade validi (servono 50): pesi INVARIATI
Sep 20 06:49:31 Trading-Agent python[1454358]: [main] pesi ricalcolati: 12 coppie strat×regime da 15 trade (30g)
Sep 20 06:57:14 Trading-Agent python[1454358]: [DRY_RUN] SCALE-OUT 11.1512 PROMUSDT @ 5.0116164717107505 (netto +2.9860, residuo 14.8683)
Sep 20 07:21:33 Trading-Agent python[1454358]: [main] verdetto trailing assegnato a 1 trade paper
Sep 20 07:39:12 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 20 07:39:12 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 20 07:39:12 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 20 07:39:12 Trading-Agent systemd[1]: trading-bot.service: Consumed 10min 50.490s CPU time.
Sep 20 07:39:12 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 20 07:39:14 Trading-Agent python[1473997]: [firebase] connesso (Firestore + RTDB)
Sep 20 07:39:14 Trading-Agent python[1473997]: [execution] ricaricate 2 posizioni aperte da Firebase (no orfani al riavvio): ['PROMUSDT', 'SPXUSDT']
Sep 20 07:39:14 Trading-Agent python[1473997]: [main] avvio bot @ 2026-09-20T07:39:14.836281+00:00 DRY_RUN=True
Sep 20 07:39:14 Trading-Agent python[1473997]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 07:39:14 Trading-Agent python[1473997]:   return query.where(field_path, op_string, value)
Sep 20 07:39:15 Trading-Agent python[1473997]: [main] equity riconciliata: 986.45 (base 1000.00 + realizzato -17.99 + fette aperte +4.44)
Sep 20 07:39:15 Trading-Agent python[1473997]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 20 07:39:15 Trading-Agent python[1473997]: [learning] solo 15 trade validi (servono 50): pesi INVARIATI
Sep 20 07:39:15 Trading-Agent python[1473997]: [main] pesi ricalcolati: 12 coppie strat×regime da 15 trade (30g)
Sep 20 07:39:15 Trading-Agent python[1473997]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=promusdt@bookTicker/spxusdt@bookTicker
Sep 20 07:39:18 Trading-Agent python[1473997]: [main] market scan...
Sep 20 07:40:04 Trading-Agent python[1473997]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 20 07:40:04 Trading-Agent python[1473997]:   return query.where(field_path, op_string, value)
Sep 20 07:40:04 Trading-Agent python[1473997]: [main] valutate 25 coin validate (25 nel registro): ['PROMUSDT', 'EGLDUSDT', 'TUTUSDT', 'USELESSUSDT', 'HEMIUSDT', 'JTOUSDT', 'NEIROUSDT', 'SPXUSDT', 'HEIUSDT', 'VETUSDT', 'GPSUSDT', 'ZKUSDT', 'TRUMPUSDT', 'SEIUSDT', 'DOTUSDT', 'SYRUPUSDT', 'STXUSDT', 'DEXEUSDT', 'SAHARAUSDT', 'QUSDT', 'BICOUSDT', 'JASMYUSDT', 'ORCAUSDT', 'SKYAIUSDT', 'MUBARAKUSDT']
```
