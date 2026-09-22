# 0146-log-bot-cooldown.req

_eseguito: 2026-09-22 06:02 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.5s

```
Sep 21 16:02:47 Trading-Agent python[1524589]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 16:02:47 Trading-Agent python[1524589]:   return query.where(field_path, op_string, value)
Sep 21 16:02:48 Trading-Agent python[1524589]: [learning] solo 33 trade validi (servono 50): pesi INVARIATI
Sep 21 16:02:48 Trading-Agent python[1524589]: [main] pesi ricalcolati: 22 coppie strat×regime da 33 trade (30g)
Sep 21 16:02:48 Trading-Agent python[1524589]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 16:03:51 Trading-Agent python[1524589]: [main] verdetto trailing assegnato a 1 trade paper
Sep 21 16:34:22 Trading-Agent python[1524589]: [main] verdetto trailing assegnato a 1 trade paper
Sep 21 16:44:08 Trading-Agent python[1524589]: [main] market scan...
Sep 21 16:44:56 Trading-Agent python[1524589]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 16:44:56 Trading-Agent python[1524589]:   return query.where(field_path, op_string, value)
Sep 21 16:44:57 Trading-Agent python[1524589]: [main] valutate 26 coin validate (26 nel registro): ['TUTUSDT', 'MUBARAKUSDT', 'USELESSUSDT', 'SPXUSDT', 'NEIROUSDT', 'DOTUSDT', 'GPSUSDT', 'TRUMPUSDT', 'JASMYUSDT', 'DEXEUSDT', 'ORCAUSDT', 'SEIUSDT', 'JTOUSDT', 'ZKUSDT', 'VETUSDT', 'EGLDUSDT', 'QUSDT', 'SCRUSDT', 'HEMIUSDT', 'PROMUSDT', 'STXUSDT', 'SKYAIUSDT', 'SYRUPUSDT', 'BICOUSDT', 'SAHARAUSDT', 'HEIUSDT']
Sep 21 17:02:01 Trading-Agent python[1524589]: [price_stream] disconnesso (sent 1011 (internal error) keepalive ping timeout; no close frame received) · riprovo in 5s
Sep 21 17:02:22 Trading-Agent python[1524589]: [price_stream] disconnesso () · riprovo in 10s
Sep 21 17:03:00 Trading-Agent python[1524589]: [price_stream] disconnesso () · riprovo in 30s
Sep 21 17:03:32 Trading-Agent python[1524589]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker/promusdt@bookTicker
Sep 21 17:03:32 Trading-Agent python[1524589]: [price_stream] riconnesso dopo 91s di buco (3 tentativi)
Sep 21 17:04:53 Trading-Agent python[1524589]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 17:04:53 Trading-Agent python[1524589]:   return query.where(field_path, op_string, value)
Sep 21 17:04:54 Trading-Agent python[1524589]: [learning] solo 33 trade validi (servono 50): pesi INVARIATI
Sep 21 17:04:54 Trading-Agent python[1524589]: [main] pesi ricalcolati: 22 coppie strat×regime da 33 trade (30g)
Sep 21 17:04:54 Trading-Agent python[1524589]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 17:04:55 Trading-Agent python[1524589]: [main] stream ripreso dopo 91s (0 candele perse): nessuna nuova posizione per 2 candele
Sep 21 18:05:13 Trading-Agent python[1524589]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 18:05:13 Trading-Agent python[1524589]:   return query.where(field_path, op_string, value)
Sep 21 18:05:13 Trading-Agent python[1524589]: [learning] solo 33 trade validi (servono 50): pesi INVARIATI
Sep 21 18:05:13 Trading-Agent python[1524589]: [main] pesi ricalcolati: 22 coppie strat×regime da 33 trade (30g)
Sep 21 18:05:13 Trading-Agent python[1524589]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 18:50:35 Trading-Agent python[1524589]: [DRY_RUN] CLOSE PROMUSDT @ 5.035775611877497 (stop_loss)
Sep 21 18:50:36 Trading-Agent python[1524589]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 18:50:36 Trading-Agent python[1524589]:   return query.where(field_path, op_string, value)
Sep 21 18:50:36 Trading-Agent python[1524589]: [learning] solo 34 trade validi (servono 50): pesi INVARIATI
Sep 21 18:50:36 Trading-Agent python[1524589]: [main] pesi ricalcolati: 22 coppie strat×regime da 34 trade (30g)
Sep 21 18:50:37 Trading-Agent python[1524589]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 18:50:43 Trading-Agent python[1524589]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker
Sep 21 19:20:52 Trading-Agent python[1524589]: [main] verdetto trailing assegnato a 1 trade paper
Sep 21 19:47:36 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 21 19:47:36 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 21 19:47:36 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 21 19:47:36 Trading-Agent systemd[1]: trading-bot.service: Consumed 13min 20.139s CPU time.
Sep 21 19:47:36 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 21 19:47:38 Trading-Agent python[1535908]: [firebase] connesso (Firestore + RTDB)
Sep 21 19:47:38 Trading-Agent python[1535908]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['BICOUSDT']
Sep 21 19:47:38 Trading-Agent python[1535908]: [main] avvio bot @ 2026-09-21T19:47:38.787440+00:00 DRY_RUN=True
Sep 21 19:47:38 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 19:47:38 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 19:47:39 Trading-Agent python[1535908]: [main] equity riconciliata: 967.73 (base 1000.00 + realizzato -34.38 + fette aperte +2.11)
Sep 21 19:47:39 Trading-Agent python[1535908]: [main] cooldown ricaricati: 1 coin, 0 strategie in panchina
Sep 21 19:47:39 Trading-Agent python[1535908]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=bicousdt@bookTicker
Sep 21 19:47:39 Trading-Agent python[1535908]: [learning] solo 34 trade validi (servono 50): pesi INVARIATI
Sep 21 19:47:39 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 34 trade (30g)
Sep 21 19:47:40 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 19:47:42 Trading-Agent python[1535908]: [main] market scan...
Sep 21 19:48:31 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 19:48:31 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 19:48:31 Trading-Agent python[1535908]: [main] valutate 26 coin validate (26 nel registro): ['PROMUSDT', 'VETUSDT', 'SKYAIUSDT', 'USELESSUSDT', 'ZKUSDT', 'QUSDT', 'STXUSDT', 'EGLDUSDT', 'SEIUSDT', 'DOTUSDT', 'TUTUSDT', 'TRUMPUSDT', 'NEIROUSDT', 'SPXUSDT', 'HEIUSDT', 'ORCAUSDT', 'JASMYUSDT', 'SYRUPUSDT', 'JTOUSDT', 'BICOUSDT', 'GPSUSDT', 'HEMIUSDT', 'MUBARAKUSDT', 'DEXEUSDT', 'SCRUSDT', 'SAHARAUSDT']
Sep 21 20:33:08 Trading-Agent python[1535908]: [DRY_RUN] CLOSE BICOUSDT @ 0.0227525 (scale_out)
Sep 21 20:33:10 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 20:33:10 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 20:33:11 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 21 20:33:11 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 21 20:33:11 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 21:04:04 Trading-Agent python[1535908]: [main] verdetto trailing assegnato a 1 trade paper
Sep 21 21:33:28 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 21:33:28 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 21:33:29 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 21 21:33:29 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 21 21:33:29 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 22:33:53 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 22:33:53 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 22:33:53 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 21 22:33:53 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 21 22:33:53 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 23:34:14 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 23:34:14 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 23:34:15 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 21 23:34:15 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 21 23:34:15 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 21 23:47:39 Trading-Agent python[1535908]: [main] market scan...
Sep 21 23:48:27 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 21 23:48:27 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 21 23:48:27 Trading-Agent python[1535908]: [main] valutate 26 coin validate (26 nel registro): ['SCRUSDT', 'VETUSDT', 'DOTUSDT', 'EGLDUSDT', 'SEIUSDT', 'TRUMPUSDT', 'SYRUPUSDT', 'STXUSDT', 'DEXEUSDT', 'ZKUSDT', 'HEMIUSDT', 'PROMUSDT', 'JTOUSDT', 'JASMYUSDT', 'MUBARAKUSDT', 'HEIUSDT', 'GPSUSDT', 'SPXUSDT', 'NEIROUSDT', 'USELESSUSDT', 'SKYAIUSDT', 'TUTUSDT', 'SAHARAUSDT', 'ORCAUSDT', 'BICOUSDT', 'QUSDT']
Sep 22 00:34:17 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 00:34:17 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 00:34:17 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 00:34:17 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 00:34:17 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 01:25:40 Trading-Agent python[1535908]: [main] verdetto trailing assegnato a 1 trade paper
Sep 22 01:34:33 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 01:34:33 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 01:34:33 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 01:34:33 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 01:34:33 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 02:34:52 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 02:34:52 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 02:34:52 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 02:34:52 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 02:34:52 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 02:42:25 Trading-Agent python[1535908]: [main] verdetto trailing assegnato a 1 trade paper
Sep 22 03:35:01 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 03:35:01 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 03:35:01 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 03:35:01 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 03:35:02 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 03:47:59 Trading-Agent python[1535908]: [main] market scan...
Sep 22 03:48:49 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 03:48:49 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 03:48:49 Trading-Agent python[1535908]: [main] valutate 26 coin validate (26 nel registro): ['MUBARAKUSDT', 'USELESSUSDT', 'HEMIUSDT', 'SYRUPUSDT', 'ZKUSDT', 'SEIUSDT', 'NEIROUSDT', 'TRUMPUSDT', 'VETUSDT', 'PROMUSDT', 'SPXUSDT', 'TUTUSDT', 'JTOUSDT', 'DOTUSDT', 'HEIUSDT', 'QUSDT', 'GPSUSDT', 'STXUSDT', 'EGLDUSDT', 'JASMYUSDT', 'BICOUSDT', 'SCRUSDT', 'DEXEUSDT', 'SKYAIUSDT', 'SAHARAUSDT', 'ORCAUSDT']
Sep 22 04:35:05 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 04:35:05 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 04:35:05 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 04:35:05 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 04:35:05 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 05:35:19 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 05:35:19 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 05:35:20 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 05:35:20 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 05:35:20 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 06:01:12 Trading-Agent python[1535908]: [DRY_RUN] OPEN short MUBARAKUSDT qty=1946.9463 @ 0.05965 lev=2.0x SL=0.0632 TP=0.0491
Sep 22 06:01:14 Trading-Agent python[1535908]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker
Sep 22 06:01:21 Trading-Agent python[1535908]: [ai-shadow] ok in 8.9s · 789+417 token
```
