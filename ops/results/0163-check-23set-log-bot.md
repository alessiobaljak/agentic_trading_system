# 0163-check-23set-log-bot.req

_eseguito: 2026-09-23 06:02 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 22 14:51:03 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 15:49:04 Trading-Agent python[1535908]: [main] market scan...
Sep 22 15:49:57 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 15:49:57 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 15:49:58 Trading-Agent python[1535908]: [main] valutate 27 coin validate (27 nel registro): ['PROMUSDT', 'SCRUSDT', 'SEIUSDT', 'BULLAUSDT', 'SAHARAUSDT', 'GPSUSDT', 'TRUMPUSDT', 'HEMIUSDT', 'MUBARAKUSDT', 'SKYAIUSDT', 'SPXUSDT', 'JTOUSDT', 'DOTUSDT', 'JASMYUSDT', 'TUTUSDT', 'SYRUPUSDT', 'USELESSUSDT', 'BICOUSDT', 'VETUSDT', 'NEIROUSDT', 'EGLDUSDT', 'STXUSDT', 'ORCAUSDT', 'ZKUSDT', 'QUSDT', 'DEXEUSDT', 'HEIUSDT']
Sep 22 15:51:29 Trading-Agent python[1535908]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 15:51:29 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 15:51:29 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 16:51:35 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 16:51:35 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 16:51:35 Trading-Agent python[1535908]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 16:51:35 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 16:51:35 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 17:52:04 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 17:52:04 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 17:52:04 Trading-Agent python[1535908]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 17:52:04 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 17:52:04 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 18:52:27 Trading-Agent python[1535908]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 18:52:27 Trading-Agent python[1535908]:   return query.where(field_path, op_string, value)
Sep 22 18:52:28 Trading-Agent python[1535908]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 18:52:28 Trading-Agent python[1535908]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 18:52:28 Trading-Agent python[1535908]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 19:11:16 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 22 19:11:16 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 22 19:11:16 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 22 19:11:16 Trading-Agent systemd[1]: trading-bot.service: Consumed 19min 16.505s CPU time.
Sep 22 19:11:16 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 22 19:11:17 Trading-Agent python[1567003]: [firebase] connesso (Firestore + RTDB)
Sep 22 19:11:18 Trading-Agent python[1567003]: [main] avvio bot @ 2026-09-22T19:11:18.695243+00:00 DRY_RUN=True
Sep 22 19:11:18 Trading-Agent python[1567003]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 19:11:18 Trading-Agent python[1567003]:   return query.where(field_path, op_string, value)
Sep 22 19:11:18 Trading-Agent python[1567003]: [main] equity riconciliata: 968.91 (base 1000.00 + realizzato -31.09 + fette aperte +0.00)
Sep 22 19:11:18 Trading-Agent python[1567003]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 22 19:11:27 Trading-Agent python[1567003]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 19:11:27 Trading-Agent python[1567003]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 19:11:27 Trading-Agent python[1567003]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 19:11:30 Trading-Agent python[1567003]: [main] market scan...
Sep 22 19:12:21 Trading-Agent python[1567003]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 19:12:21 Trading-Agent python[1567003]:   return query.where(field_path, op_string, value)
Sep 22 19:12:21 Trading-Agent python[1567003]: [main] valutate 27 coin validate (27 nel registro): ['JTOUSDT', 'TUTUSDT', 'PROMUSDT', 'GPSUSDT', 'EGLDUSDT', 'USELESSUSDT', 'MUBARAKUSDT', 'VETUSDT', 'STXUSDT', 'NEIROUSDT', 'DEXEUSDT', 'SPXUSDT', 'HEMIUSDT', 'TRUMPUSDT', 'HEIUSDT', 'SEIUSDT', 'SCRUSDT', 'SAHARAUSDT', 'DOTUSDT', 'JASMYUSDT', 'SKYAIUSDT', 'QUSDT', 'ORCAUSDT', 'ZKUSDT', 'BULLAUSDT', 'BICOUSDT', 'SYRUPUSDT']
Sep 22 20:11:39 Trading-Agent python[1567003]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 20:11:39 Trading-Agent python[1567003]:   return query.where(field_path, op_string, value)
Sep 22 20:11:39 Trading-Agent python[1567003]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 20:11:39 Trading-Agent python[1567003]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 20:11:40 Trading-Agent python[1567003]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 21:12:05 Trading-Agent python[1567003]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 21:12:05 Trading-Agent python[1567003]:   return query.where(field_path, op_string, value)
Sep 22 21:12:05 Trading-Agent python[1567003]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 21:12:05 Trading-Agent python[1567003]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 21:12:05 Trading-Agent python[1567003]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 21:35:53 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 22 21:35:53 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 22 21:35:53 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 22 21:35:53 Trading-Agent systemd[1]: trading-bot.service: Consumed 56.952s CPU time.
Sep 22 21:35:53 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 22 21:35:55 Trading-Agent python[1570164]: [firebase] connesso (Firestore + RTDB)
Sep 22 21:35:56 Trading-Agent python[1570164]: [main] avvio bot @ 2026-09-22T21:35:56.103430+00:00 DRY_RUN=True
Sep 22 21:35:56 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 21:35:56 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 22 21:35:56 Trading-Agent python[1570164]: [main] equity riconciliata: 968.91 (base 1000.00 + realizzato -31.09 + fette aperte +0.00)
Sep 22 21:35:56 Trading-Agent python[1570164]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 22 21:35:56 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 21:35:56 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 21:35:57 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 21:35:59 Trading-Agent python[1570164]: [main] market scan...
Sep 22 21:36:50 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 21:36:50 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 22 21:36:51 Trading-Agent python[1570164]: [main] valutate 27 coin validate (27 nel registro): ['TUTUSDT', 'USELESSUSDT', 'ORCAUSDT', 'JTOUSDT', 'JASMYUSDT', 'PROMUSDT', 'GPSUSDT', 'SAHARAUSDT', 'NEIROUSDT', 'SEIUSDT', 'DOTUSDT', 'TRUMPUSDT', 'VETUSDT', 'DEXEUSDT', 'SPXUSDT', 'SYRUPUSDT', 'MUBARAKUSDT', 'BULLAUSDT', 'HEIUSDT', 'STXUSDT', 'EGLDUSDT', 'BICOUSDT', 'SKYAIUSDT', 'SCRUSDT', 'ZKUSDT', 'QUSDT', 'HEMIUSDT']
Sep 22 22:35:59 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 22:35:59 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 22 22:35:59 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 22:35:59 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 22:36:00 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 22 23:36:20 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 22 23:36:20 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 22 23:36:20 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 22 23:36:20 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 22 23:36:20 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 00:36:40 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 00:36:40 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 00:36:40 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 00:36:40 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 00:36:40 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 01:36:05 Trading-Agent python[1570164]: [main] market scan...
Sep 23 01:36:54 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 01:36:54 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 01:36:55 Trading-Agent python[1570164]: [main] valutate 27 coin validate (27 nel registro): ['VETUSDT', 'SAHARAUSDT', 'EGLDUSDT', 'DEXEUSDT', 'TUTUSDT', 'TRUMPUSDT', 'JTOUSDT', 'SCRUSDT', 'HEIUSDT', 'GPSUSDT', 'SEIUSDT', 'BICOUSDT', 'NEIROUSDT', 'PROMUSDT', 'BULLAUSDT', 'DOTUSDT', 'USELESSUSDT', 'JASMYUSDT', 'SPXUSDT', 'ORCAUSDT', 'MUBARAKUSDT', 'ZKUSDT', 'STXUSDT', 'SYRUPUSDT', 'HEMIUSDT', 'SKYAIUSDT', 'QUSDT']
Sep 23 01:37:25 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 01:37:25 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 01:37:25 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 02:37:53 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 02:37:53 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 02:37:53 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 02:37:53 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 02:37:53 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 03:38:17 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 03:38:17 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 03:38:17 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 03:38:17 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 03:38:17 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 03:46:18 Trading-Agent python[1570164]: [DRY_RUN] OPEN short VETUSDT qty=19950.8424 @ 0.009713 lev=2.0x SL=0.0099 TP=0.0094
Sep 23 03:46:19 Trading-Agent python[1570164]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=vetusdt@bookTicker
Sep 23 03:46:28 Trading-Agent python[1570164]: [ai-shadow] ok in 9.8s · 783+638 token
Sep 23 04:38:25 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 04:38:25 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 04:38:25 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 04:38:25 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 04:38:26 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 05:01:03 Trading-Agent python[1570164]: [DRY_RUN] OPEN long MUBARAKUSDT qty=915.3240 @ 0.07022 lev=2.0x SL=0.0595 TP=0.0916
Sep 23 05:01:10 Trading-Agent python[1570164]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/vetusdt@bookTicker
Sep 23 05:01:23 Trading-Agent python[1570164]: [ai-shadow] ok in 19.5s · 838+1151 token
Sep 23 05:36:33 Trading-Agent python[1570164]: [main] market scan...
Sep 23 05:37:25 Trading-Agent python[1570164]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 23 05:37:25 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 05:37:25 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 05:37:25 Trading-Agent python[1570164]: [main] valutate 27 coin validate (27 nel registro): ['MUBARAKUSDT', 'JTOUSDT', 'USELESSUSDT', 'DEXEUSDT', 'VETUSDT', 'GPSUSDT', 'TUTUSDT', 'ZKUSDT', 'DOTUSDT', 'SPXUSDT', 'TRUMPUSDT', 'SAHARAUSDT', 'SKYAIUSDT', 'HEMIUSDT', 'NEIROUSDT', 'HEIUSDT', 'STXUSDT', 'SEIUSDT', 'JASMYUSDT', 'PROMUSDT', 'BULLAUSDT', 'EGLDUSDT', 'ORCAUSDT', 'SCRUSDT', 'SYRUPUSDT', 'QUSDT', 'BICOUSDT']
Sep 23 05:38:27 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 05:38:27 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 05:38:27 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
```
