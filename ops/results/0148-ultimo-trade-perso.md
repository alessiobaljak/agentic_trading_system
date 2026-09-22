# 0148-ultimo-trade-perso.req

_eseguito: 2026-09-22 12:52 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
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
Sep 22 06:35:33 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 06:35:33 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 06:35:33 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 06:35:33 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 06:35:34 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 07:01:27 Trading-Agent python[1535908]: [ai-shadow] ok in 9.8s · 789+454 token
Sep 22 07:35:42 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 07:35:42 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 07:35:42 Trading-Agent python[1535908]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Sep 22 07:35:42 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 35 trade (30g)
Sep 22 07:35:43 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 07:48:19 Trading-Agent python[1535908]: [main] market scan...
Sep 22 07:49:09 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 07:49:09 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 07:49:10 Trading-Agent python[1535908]: [main] valutate 26 coin validate (26 nel registro): ['TUTUSDT', 'HEIUSDT', 'USELESSUSDT', 'SKYAIUSDT', 'DOTUSDT', 'MUBARAKUSDT', 'SEIUSDT', 'JASMYUSDT', 'ZKUSDT', 'GPSUSDT', 'HEMIUSDT', 'VETUSDT', 'STXUSDT', 'SYRUPUSDT', 'TRUMPUSDT', 'NEIROUSDT', 'EGLDUSDT', 'ORCAUSDT', 'SAHARAUSDT', 'SPXUSDT', 'JTOUSDT', 'BICOUSDT', 'DEXEUSDT', 'PROMUSDT', 'SCRUSDT', 'QUSDT']
Sep 22 08:08:20 Trading-Agent python[1535908]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.056150000000000005 (trailing_stop)
Sep 22 08:08:29 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 08:08:29 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 08:08:30 Trading-Agent python[1535908]: [learning] solo 36 trade validi (servono 50): pesi INVARIATI
Sep 22 08:08:30 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 36 trade (30g)
Sep 22 08:08:30 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 08:16:23 Trading-Agent python[1535908]: [DRY_RUN] OPEN short USELESSUSDT qty=649.0068 @ 0.3014 lev=2.0x SL=0.3152 TP=0.2738
Sep 22 08:16:24 Trading-Agent python[1535908]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=uselessusdt@bookTicker
Sep 22 08:16:33 Trading-Agent python[1535908]: [ai-shadow] ok in 9.7s · 789+504 token
Sep 22 09:08:32 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 09:08:32 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 09:08:33 Trading-Agent python[1535908]: [learning] solo 36 trade validi (servono 50): pesi INVARIATI
Sep 22 09:08:33 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 36 trade (30g)
Sep 22 09:08:33 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 10:08:37 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 10:08:37 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 10:08:38 Trading-Agent python[1535908]: [learning] solo 36 trade validi (servono 50): pesi INVARIATI
Sep 22 10:08:38 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 36 trade (30g)
Sep 22 10:08:38 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 10:09:39 Trading-Agent python[1535908]: [main] verdetto trailing assegnato a 1 trade paper
Sep 22 11:09:03 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 11:09:03 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 11:09:03 Trading-Agent python[1535908]: [learning] solo 36 trade validi (servono 50): pesi INVARIATI
Sep 22 11:09:03 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 36 trade (30g)
Sep 22 11:09:04 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 11:48:48 Trading-Agent python[1535908]: [main] market scan...
Sep 22 11:49:41 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 11:49:41 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 11:49:41 Trading-Agent python[1535908]: [main] valutate 27 coin validate (27 nel registro): ['PROMUSDT', 'STXUSDT', 'USELESSUSDT', 'MUBARAKUSDT', 'TUTUSDT', 'DEXEUSDT', 'BULLAUSDT', 'SPXUSDT', 'JTOUSDT', 'NEIROUSDT', 'TRUMPUSDT', 'VETUSDT', 'SEIUSDT', 'DOTUSDT', 'BICOUSDT', 'ZKUSDT', 'HEMIUSDT', 'EGLDUSDT', 'HEIUSDT', 'JASMYUSDT', 'SCRUSDT', 'ORCAUSDT', 'SYRUPUSDT', 'GPSUSDT', 'SKYAIUSDT', 'SAHARAUSDT', 'QUSDT']
Sep 22 11:49:41 Trading-Agent python[1535908]: [DRY_RUN] CLOSE USELESSUSDT @ 0.31519818887789375 (stop_loss)
Sep 22 11:49:42 Trading-Agent python[1535908]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 11:49:42 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 11:49:43 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 12:50:13 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 12:50:13 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 12:50:13 Trading-Agent python[1535908]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 12:50:13 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 12:50:14 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
```
