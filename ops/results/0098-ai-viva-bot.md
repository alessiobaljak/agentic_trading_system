# 0098-ai-viva-bot.req

_eseguito: 2026-09-19 14:50 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 19 03:34:22 Trading-Agent python[1190071]: [main] pesi ricalcolati: 7 coppie strat×regime da 9 trade (30g)
Sep 19 04:16:15 Trading-Agent python[1190071]: [DRY_RUN] OPEN short VETUSDT qty=23961.9030 @ 0.008292 lev=2.0x SL=0.0085 TP=0.0080
Sep 19 04:16:16 Trading-Agent python[1190071]: [ai-shadow] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011CfC9iaJxe61LvGfJVeT5g'}) -> proseguo senza AI
Sep 19 04:16:22 Trading-Agent python[1190071]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/stxusdt@bookTicker/vetusdt@bookTicker
Sep 19 04:34:44 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 04:34:44 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 04:34:44 Trading-Agent python[1190071]: [learning] solo 9 trade validi (servono 50): pesi INVARIATI
Sep 19 04:34:44 Trading-Agent python[1190071]: [main] pesi ricalcolati: 7 coppie strat×regime da 9 trade (30g)
Sep 19 04:45:07 Trading-Agent python[1190071]: [main] market scan...
Sep 19 04:45:52 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 04:45:52 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 04:45:52 Trading-Agent python[1190071]: [main] valutate 24 coin validate (24 nel registro): ['VETUSDT', 'PROMUSDT', 'JASMYUSDT', 'DOTUSDT', 'SPXUSDT', 'USELESSUSDT', 'HEIUSDT', 'MUBARAKUSDT', 'EGLDUSDT', 'HEMIUSDT', 'SEIUSDT', 'NEIROUSDT', 'ORCAUSDT', 'QUSDT', 'JTOUSDT', 'TUTUSDT', 'BICOUSDT', 'SAHARAUSDT', 'SKYAIUSDT', 'STXUSDT', 'ZKUSDT', 'SYRUPUSDT', 'DEXEUSDT', 'GPSUSDT']
Sep 19 05:00:57 Trading-Agent python[1190071]: [ai-shadow] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011CfCD8Fgo87EAqeBMWMPn5'}) -> proseguo senza AI
Sep 19 05:35:11 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 05:35:11 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 05:35:11 Trading-Agent python[1190071]: [learning] solo 9 trade validi (servono 50): pesi INVARIATI
Sep 19 05:35:11 Trading-Agent python[1190071]: [main] pesi ricalcolati: 7 coppie strat×regime da 9 trade (30g)
Sep 19 05:46:55 Trading-Agent python[1190071]: [DRY_RUN] CLOSE STXUSDT @ 0.2795380734617427 (stop_loss)
Sep 19 05:46:56 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 05:46:56 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 05:46:56 Trading-Agent python[1190071]: [learning] solo 10 trade validi (servono 50): pesi INVARIATI
Sep 19 05:46:56 Trading-Agent python[1190071]: [main] pesi ricalcolati: 8 coppie strat×regime da 10 trade (30g)
Sep 19 05:47:01 Trading-Agent python[1190071]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/vetusdt@bookTicker
Sep 19 06:08:46 Trading-Agent python[1190071]: [DRY_RUN] CLOSE DEXEUSDT @ 1.8434669423562575 (stop_loss)
Sep 19 06:08:52 Trading-Agent python[1190071]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=vetusdt@bookTicker
Sep 19 06:08:55 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 06:08:55 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 06:08:55 Trading-Agent python[1190071]: [learning] solo 11 trade validi (servono 50): pesi INVARIATI
Sep 19 06:08:55 Trading-Agent python[1190071]: [main] pesi ricalcolati: 9 coppie strat×regime da 11 trade (30g)
Sep 19 06:48:52 Trading-Agent python[1190071]: [DRY_RUN] CLOSE VETUSDT @ 0.008511675210952483 (stop_loss)
Sep 19 06:48:52 Trading-Agent python[1190071]: [main] strategia gen_6d06dca0 in panchina dopo 3 stop consecutivi
Sep 19 06:48:52 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 06:48:52 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 06:48:52 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 06:48:52 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 06:48:53 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 07:49:22 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 07:49:22 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 07:49:22 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 07:49:22 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 07:49:22 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 08:45:09 Trading-Agent python[1190071]: [main] market scan...
Sep 19 08:45:57 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 08:45:57 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 08:45:57 Trading-Agent python[1190071]: [main] valutate 24 coin validate (24 nel registro): ['HEIUSDT', 'EGLDUSDT', 'PROMUSDT', 'ORCAUSDT', 'VETUSDT', 'USELESSUSDT', 'STXUSDT', 'DOTUSDT', 'TUTUSDT', 'HEMIUSDT', 'NEIROUSDT', 'GPSUSDT', 'SYRUPUSDT', 'JTOUSDT', 'SPXUSDT', 'MUBARAKUSDT', 'DEXEUSDT', 'ZKUSDT', 'SEIUSDT', 'BICOUSDT', 'SAHARAUSDT', 'SKYAIUSDT', 'QUSDT', 'JASMYUSDT']
Sep 19 08:49:47 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 08:49:47 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 08:49:47 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 08:49:47 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 08:49:47 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 09:50:13 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 09:50:13 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 09:50:14 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 09:50:14 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 09:50:14 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 10:50:16 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 10:50:16 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 10:50:16 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 10:50:16 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 10:50:16 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 11:15:58 Trading-Agent python[1190071]: [DRY_RUN] OPEN short DEXEUSDT qty=105.9283 @ 1.854 lev=2.0x SL=1.8700 TP=1.8299
Sep 19 11:15:58 Trading-Agent python[1190071]: [ai-shadow] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011CfChiu4JfLDa9fENPgV2L'}) -> proseguo senza AI
Sep 19 11:16:00 Trading-Agent python[1190071]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker
Sep 19 11:50:39 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 11:50:39 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 11:50:39 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 11:50:39 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 11:50:39 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 12:45:21 Trading-Agent python[1190071]: [main] market scan...
Sep 19 12:46:05 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 12:46:05 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 12:46:05 Trading-Agent python[1190071]: [main] valutate 24 coin validate (24 nel registro): ['STXUSDT', 'VETUSDT', 'MUBARAKUSDT', 'USELESSUSDT', 'SAHARAUSDT', 'TUTUSDT', 'JTOUSDT', 'SEIUSDT', 'BICOUSDT', 'HEMIUSDT', 'DOTUSDT', 'EGLDUSDT', 'NEIROUSDT', 'JASMYUSDT', 'HEIUSDT', 'SKYAIUSDT', 'SPXUSDT', 'ZKUSDT', 'SYRUPUSDT', 'PROMUSDT', 'ORCAUSDT', 'GPSUSDT', 'QUSDT', 'DEXEUSDT']
Sep 19 12:50:54 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 12:50:54 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 12:50:54 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 12:50:54 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 12:50:54 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 13:50:54 Trading-Agent python[1190071]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 13:50:54 Trading-Agent python[1190071]:   return query.where(field_path, op_string, value)
Sep 19 13:50:55 Trading-Agent python[1190071]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 13:50:55 Trading-Agent python[1190071]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 13:50:55 Trading-Agent python[1190071]: [drift] calcolo saltato: 'int' object has no attribute 'get'
Sep 19 14:39:18 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 19 14:39:18 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 19 14:39:18 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 19 14:39:18 Trading-Agent systemd[1]: trading-bot.service: Consumed 2h 5min 4.185s CPU time, 129.7M memory peak, 0B memory swap peak.
Sep 19 14:39:18 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 19 14:39:19 Trading-Agent python[1449923]: [firebase] connesso (Firestore + RTDB)
Sep 19 14:39:20 Trading-Agent python[1449923]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['DEXEUSDT']
Sep 19 14:39:20 Trading-Agent python[1449923]: [main] avvio bot @ 2026-09-19T14:39:20.745522+00:00 DRY_RUN=True
Sep 19 14:39:20 Trading-Agent python[1449923]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 14:39:20 Trading-Agent python[1449923]:   return query.where(field_path, op_string, value)
Sep 19 14:39:20 Trading-Agent python[1449923]: [main] equity riconciliata: 981.95 (base 1000.00 + realizzato -18.05 + fette aperte +0.00)
Sep 19 14:39:21 Trading-Agent python[1449923]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 19 14:39:21 Trading-Agent python[1449923]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 14:39:21 Trading-Agent python[1449923]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 14:39:21 Trading-Agent python[1449923]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker
Sep 19 14:39:24 Trading-Agent python[1449923]: [main] market scan...
Sep 19 14:40:09 Trading-Agent python[1449923]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 14:40:09 Trading-Agent python[1449923]:   return query.where(field_path, op_string, value)
Sep 19 14:40:10 Trading-Agent python[1449923]: [main] valutate 24 coin validate (24 nel registro): ['JTOUSDT', 'USELESSUSDT', 'SEIUSDT', 'SKYAIUSDT', 'STXUSDT', 'VETUSDT', 'BICOUSDT', 'SAHARAUSDT', 'TUTUSDT', 'QUSDT', 'JASMYUSDT', 'DEXEUSDT', 'DOTUSDT', 'PROMUSDT', 'ZKUSDT', 'HEIUSDT', 'MUBARAKUSDT', 'EGLDUSDT', 'NEIROUSDT', 'HEMIUSDT', 'GPSUSDT', 'SYRUPUSDT', 'SPXUSDT', 'ORCAUSDT']
Sep 19 14:47:52 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 19 14:47:52 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 19 14:47:52 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 19 14:47:52 Trading-Agent systemd[1]: trading-bot.service: Consumed 17.553s CPU time.
Sep 19 14:47:52 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 19 14:47:53 Trading-Agent python[1450180]: [firebase] connesso (Firestore + RTDB)
Sep 19 14:47:54 Trading-Agent python[1450180]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['DEXEUSDT']
Sep 19 14:47:54 Trading-Agent python[1450180]: [main] avvio bot @ 2026-09-19T14:47:54.474690+00:00 DRY_RUN=True
Sep 19 14:47:54 Trading-Agent python[1450180]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 14:47:54 Trading-Agent python[1450180]:   return query.where(field_path, op_string, value)
Sep 19 14:47:54 Trading-Agent python[1450180]: [main] equity riconciliata: 981.95 (base 1000.00 + realizzato -18.05 + fette aperte +0.00)
Sep 19 14:47:54 Trading-Agent python[1450180]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 19 14:47:55 Trading-Agent python[1450180]: [learning] solo 12 trade validi (servono 50): pesi INVARIATI
Sep 19 14:47:55 Trading-Agent python[1450180]: [main] pesi ricalcolati: 10 coppie strat×regime da 12 trade (30g)
Sep 19 14:47:55 Trading-Agent python[1450180]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker
Sep 19 14:47:57 Trading-Agent python[1450180]: [main] market scan...
Sep 19 14:48:42 Trading-Agent python[1450180]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 19 14:48:42 Trading-Agent python[1450180]:   return query.where(field_path, op_string, value)
Sep 19 14:48:43 Trading-Agent python[1450180]: [main] valutate 24 coin validate (24 nel registro): ['JTOUSDT', 'DOTUSDT', 'QUSDT', 'VETUSDT', 'USELESSUSDT', 'BICOUSDT', 'STXUSDT', 'SEIUSDT', 'EGLDUSDT', 'TUTUSDT', 'SAHARAUSDT', 'MUBARAKUSDT', 'SPXUSDT', 'GPSUSDT', 'HEMIUSDT', 'SKYAIUSDT', 'ZKUSDT', 'JASMYUSDT', 'PROMUSDT', 'DEXEUSDT', 'HEIUSDT', 'NEIROUSDT', 'ORCAUSDT', 'SYRUPUSDT']
```
