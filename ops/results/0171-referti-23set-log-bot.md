# 0171-referti-23set-log-bot.req

_eseguito: 2026-09-23 11:48 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
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
Sep 23 06:38:29 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 06:38:29 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 06:38:30 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 06:38:30 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 06:38:30 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 07:38:51 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 07:38:51 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 07:38:51 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 07:38:51 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 07:38:52 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 08:39:07 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 08:39:07 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 08:39:07 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 08:39:07 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 08:39:08 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 09:36:42 Trading-Agent python[1570164]: [main] market scan...
Sep 23 09:37:36 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 09:37:36 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 09:37:36 Trading-Agent python[1570164]: [main] valutate 27 coin validate (27 nel registro): ['EGLDUSDT', 'SPXUSDT', 'QUSDT', 'USELESSUSDT', 'PROMUSDT', 'DOTUSDT', 'TRUMPUSDT', 'DEXEUSDT', 'ZKUSDT', 'MUBARAKUSDT', 'NEIROUSDT', 'JTOUSDT', 'GPSUSDT', 'STXUSDT', 'SKYAIUSDT', 'HEMIUSDT', 'BULLAUSDT', 'VETUSDT', 'ORCAUSDT', 'JASMYUSDT', 'BICOUSDT', 'TUTUSDT', 'SEIUSDT', 'SAHARAUSDT', 'SYRUPUSDT', 'HEIUSDT', 'SCRUSDT']
Sep 23 09:39:09 Trading-Agent python[1570164]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Sep 23 09:39:09 Trading-Agent python[1570164]: [main] pesi ricalcolati: 22 coppie strat×regime da 37 trade (30g)
Sep 23 09:39:09 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 09:46:47 Trading-Agent python[1570164]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.059514249761481175 (stop_loss)
Sep 23 09:46:48 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 09:46:48 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 09:46:48 Trading-Agent python[1570164]: [learning] solo 38 trade validi (servono 50): pesi INVARIATI
Sep 23 09:46:48 Trading-Agent python[1570164]: [main] pesi ricalcolati: 23 coppie strat×regime da 38 trade (30g)
Sep 23 09:46:48 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 09:46:57 Trading-Agent python[1570164]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=vetusdt@bookTicker
Sep 23 10:31:09 Trading-Agent python[1570164]: [DRY_RUN] OPEN long SPXUSDT qty=387.2572 @ 0.4953 lev=2.0x SL=0.4845 TP=0.5115
Sep 23 10:31:15 Trading-Agent python[1570164]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=spxusdt@bookTicker/vetusdt@bookTicker
Sep 23 10:31:26 Trading-Agent python[1570164]: [ai-shadow] ok in 16.4s · 830+883 token
Sep 23 10:46:28 Trading-Agent python[1570164]: [ai-shadow] ok in 14.0s · 830+805 token
Sep 23 10:46:59 Trading-Agent python[1570164]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 10:46:59 Trading-Agent python[1570164]:   return query.where(field_path, op_string, value)
Sep 23 10:46:59 Trading-Agent python[1570164]: [learning] solo 38 trade validi (servono 50): pesi INVARIATI
Sep 23 10:46:59 Trading-Agent python[1570164]: [main] pesi ricalcolati: 23 coppie strat×regime da 38 trade (30g)
Sep 23 10:47:00 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 10:48:02 Trading-Agent python[1570164]: [DRY_RUN] CLOSE SPXUSDT @ 0.48450916208869416 (stop_loss)
Sep 23 10:48:03 Trading-Agent python[1570164]: [learning] solo 39 trade validi (servono 50): pesi INVARIATI
Sep 23 10:48:03 Trading-Agent python[1570164]: [main] pesi ricalcolati: 23 coppie strat×regime da 39 trade (30g)
Sep 23 10:48:04 Trading-Agent python[1570164]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 10:48:13 Trading-Agent python[1570164]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=vetusdt@bookTicker
Sep 23 11:01:27 Trading-Agent python[1570164]: [ai-shadow] ok in 17.8s · 830+960 token
Sep 23 11:06:36 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 23 11:06:36 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 23 11:06:36 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 23 11:06:36 Trading-Agent systemd[1]: trading-bot.service: Consumed 25min 9.442s CPU time.
Sep 23 11:06:36 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 23 11:06:37 Trading-Agent python[1592585]: [firebase] connesso (Firestore + RTDB)
Sep 23 11:06:38 Trading-Agent python[1592585]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['VETUSDT']
Sep 23 11:06:38 Trading-Agent python[1592585]: [main] avvio bot @ 2026-09-23T11:06:38.778090+00:00 DRY_RUN=True
Sep 23 11:06:38 Trading-Agent python[1592585]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 11:06:38 Trading-Agent python[1592585]:   return query.where(field_path, op_string, value)
Sep 23 11:06:39 Trading-Agent python[1592585]: [main] equity riconciliata: 954.62 (base 1000.00 + realizzato -45.38 + fette aperte +0.00)
Sep 23 11:06:39 Trading-Agent python[1592585]: [main] cooldown ricaricati: 1 coin, 0 strategie in panchina
Sep 23 11:06:39 Trading-Agent python[1592585]: [learning] solo 39 trade validi (servono 50): pesi INVARIATI
Sep 23 11:06:39 Trading-Agent python[1592585]: [main] pesi ricalcolati: 23 coppie strat×regime da 39 trade (30g)
Sep 23 11:06:39 Trading-Agent python[1592585]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 11:06:40 Trading-Agent python[1592585]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=vetusdt@bookTicker
Sep 23 11:06:42 Trading-Agent python[1592585]: [main] market scan...
Sep 23 11:07:33 Trading-Agent python[1592585]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 11:07:33 Trading-Agent python[1592585]:   return query.where(field_path, op_string, value)
Sep 23 11:07:33 Trading-Agent python[1592585]: [main] valutate 27 coin validate (27 nel registro): ['SPXUSDT', 'QUSDT', 'MUBARAKUSDT', 'USELESSUSDT', 'BICOUSDT', 'PROMUSDT', 'TRUMPUSDT', 'VETUSDT', 'JASMYUSDT', 'DOTUSDT', 'STXUSDT', 'TUTUSDT', 'ORCAUSDT', 'EGLDUSDT', 'JTOUSDT', 'GPSUSDT', 'NEIROUSDT', 'SYRUPUSDT', 'ZKUSDT', 'HEIUSDT', 'SEIUSDT', 'SCRUSDT', 'HEMIUSDT', 'DEXEUSDT', 'BULLAUSDT', 'SAHARAUSDT', 'SKYAIUSDT']
Sep 23 11:08:45 Trading-Agent python[1592585]: [ai-shadow] ok in 18.6s · 830+978 token
Sep 23 11:16:16 Trading-Agent python[1592585]: [DRY_RUN] OPEN long QUSDT qty=7224.0617 @ 0.026429 lev=2.0x SL=0.0257 TP=0.0279
Sep 23 11:16:22 Trading-Agent python[1592585]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=qusdt@bookTicker/vetusdt@bookTicker
Sep 23 11:16:37 Trading-Agent python[1592585]: [ai-shadow] risposta senza JSON valido -> ignorata
Sep 23 11:35:29 Trading-Agent python[1592585]: [DRY_RUN] CLOSE QUSDT @ 0.025709961050840318 (stop_loss)
Sep 23 11:35:29 Trading-Agent python[1592585]: [referto] QUSDT gen_18c839a0: a favore fino a 0.32R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Sep 23 11:35:30 Trading-Agent python[1592585]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 11:35:30 Trading-Agent python[1592585]:   return query.where(field_path, op_string, value)
Sep 23 11:35:30 Trading-Agent python[1592585]: [learning] solo 40 trade validi (servono 50): pesi INVARIATI
Sep 23 11:35:30 Trading-Agent python[1592585]: [main] pesi ricalcolati: 24 coppie strat×regime da 40 trade (30g)
Sep 23 11:35:30 Trading-Agent python[1592585]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 11:35:36 Trading-Agent python[1592585]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=vetusdt@bookTicker
```
