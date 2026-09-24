# 0179-check-24set-log-bot.req

_eseguito: 2026-09-24 06:13 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 23 20:10:04 Trading-Agent python[1595061]: [learning] solo 42 trade validi (servono 50): pesi INVARIATI
Sep 23 20:10:04 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 42 trade (30g)
Sep 23 20:10:05 Trading-Agent python[1595061]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 20:10:05 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 23 20:11:06 Trading-Agent python[1595061]: [main] market scan...
Sep 23 20:11:56 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 20:11:56 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 23 20:11:56 Trading-Agent python[1595061]: [main] valutate 27 coin validate (27 nel registro): ['SPXUSDT', 'NEIROUSDT', 'QUSDT', 'SKYAIUSDT', 'JTOUSDT', 'ZKUSDT', 'SCRUSDT', 'VETUSDT', 'EGLDUSDT', 'DEXEUSDT', 'JASMYUSDT', 'USELESSUSDT', 'SYRUPUSDT', 'STXUSDT', 'TRUMPUSDT', 'DOTUSDT', 'BULLAUSDT', 'GPSUSDT', 'HEMIUSDT', 'BICOUSDT', 'TUTUSDT', 'SAHARAUSDT', 'MUBARAKUSDT', 'ORCAUSDT', 'SEIUSDT', 'PROMUSDT', 'HEIUSDT']
Sep 23 21:10:33 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 21:10:33 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 23 21:10:33 Trading-Agent python[1595061]: [learning] solo 42 trade validi (servono 50): pesi INVARIATI
Sep 23 21:10:33 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 42 trade (30g)
Sep 23 21:10:33 Trading-Agent python[1595061]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 21:10:33 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 23 22:10:37 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 22:10:37 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 23 22:10:37 Trading-Agent python[1595061]: [learning] solo 42 trade validi (servono 50): pesi INVARIATI
Sep 23 22:10:37 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 42 trade (30g)
Sep 23 22:10:38 Trading-Agent python[1595061]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 22:10:38 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 23 23:10:40 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 23 23:10:40 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 23 23:10:40 Trading-Agent python[1595061]: [learning] solo 42 trade validi (servono 50): pesi INVARIATI
Sep 23 23:10:40 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 42 trade (30g)
Sep 23 23:10:40 Trading-Agent python[1595061]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 23 23:10:40 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 00:10:48 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 00:10:48 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 00:10:48 Trading-Agent python[1595061]: [learning] solo 42 trade validi (servono 50): pesi INVARIATI
Sep 24 00:10:48 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 42 trade (30g)
Sep 24 00:10:49 Trading-Agent python[1595061]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 24 00:10:49 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 00:11:19 Trading-Agent python[1595061]: [main] market scan...
Sep 24 00:12:10 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 00:12:10 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 00:12:11 Trading-Agent python[1595061]: [main] valutate 27 coin validate (27 nel registro): ['BICOUSDT', 'MUBARAKUSDT', 'JTOUSDT', 'SPXUSDT', 'EGLDUSDT', 'DEXEUSDT', 'TUTUSDT', 'HEIUSDT', 'USELESSUSDT', 'BULLAUSDT', 'SYRUPUSDT', 'PROMUSDT', 'SKYAIUSDT', 'HEMIUSDT', 'ZKUSDT', 'NEIROUSDT', 'VETUSDT', 'STXUSDT', 'GPSUSDT', 'SCRUSDT', 'ORCAUSDT', 'DOTUSDT', 'SAHARAUSDT', 'TRUMPUSDT', 'JASMYUSDT', 'SEIUSDT', 'QUSDT']
Sep 24 00:12:21 Trading-Agent python[1595061]: [price_agent] GET /fapi/v1/premiumIndex fallito: 429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/premiumIndex?symbol=QUSDT
Sep 24 00:16:01 Trading-Agent python[1595061]: [DRY_RUN] OPEN short DEXEUSDT qty=50.4646 @ 1.885 lev=1.0x SL=1.9124 TP=1.8439
Sep 24 00:16:08 Trading-Agent python[1595061]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/dotusdt@bookTicker/qusdt@bookTicker
Sep 24 00:16:18 Trading-Agent python[1595061]: [ai-shadow] ok in 16.4s · 785+1117 token
Sep 24 01:11:17 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 01:11:17 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 01:11:18 Trading-Agent python[1595061]: [learning] solo 42 trade validi (servono 50): pesi INVARIATI
Sep 24 01:11:18 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 42 trade (30g)
Sep 24 01:11:18 Trading-Agent python[1595061]: [calibrazione] flat: nessuna relazione tra confidenza ed esito: influenza ridotta -> influenza confidenza x0.50
Sep 24 01:11:18 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 01:26:15 Trading-Agent python[1595061]: [DRY_RUN] CLOSE QUSDT @ 0.02695 (trailing_stop)
Sep 24 01:26:16 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 01:26:16 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 01:26:16 Trading-Agent python[1595061]: [learning] solo 43 trade validi (servono 50): pesi INVARIATI
Sep 24 01:26:16 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 43 trade (30g)
Sep 24 01:26:17 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 01:26:21 Trading-Agent python[1595061]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/dotusdt@bookTicker
Sep 24 02:26:18 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 02:26:18 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 02:26:18 Trading-Agent python[1595061]: [learning] solo 43 trade validi (servono 50): pesi INVARIATI
Sep 24 02:26:18 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 43 trade (30g)
Sep 24 02:26:18 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 03:26:24 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 03:26:24 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 03:26:24 Trading-Agent python[1595061]: [learning] solo 43 trade validi (servono 50): pesi INVARIATI
Sep 24 03:26:24 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 43 trade (30g)
Sep 24 03:26:24 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 04:11:39 Trading-Agent python[1595061]: [main] market scan...
Sep 24 04:12:27 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 04:12:27 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 04:12:28 Trading-Agent python[1595061]: [main] valutate 27 coin validate (27 nel registro): ['SPXUSDT', 'JASMYUSDT', 'MUBARAKUSDT', 'DOTUSDT', 'USELESSUSDT', 'DEXEUSDT', 'ZKUSDT', 'HEIUSDT', 'TUTUSDT', 'VETUSDT', 'BICOUSDT', 'TRUMPUSDT', 'JTOUSDT', 'ORCAUSDT', 'PROMUSDT', 'NEIROUSDT', 'SCRUSDT', 'SEIUSDT', 'HEMIUSDT', 'SYRUPUSDT', 'STXUSDT', 'EGLDUSDT', 'SKYAIUSDT', 'BULLAUSDT', 'SAHARAUSDT', 'QUSDT', 'GPSUSDT']
Sep 24 04:26:43 Trading-Agent python[1595061]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 04:26:43 Trading-Agent python[1595061]:   return query.where(field_path, op_string, value)
Sep 24 04:26:43 Trading-Agent python[1595061]: [learning] solo 43 trade validi (servono 50): pesi INVARIATI
Sep 24 04:26:43 Trading-Agent python[1595061]: [main] pesi ricalcolati: 24 coppie strat×regime da 43 trade (30g)
Sep 24 04:26:43 Trading-Agent python[1595061]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 05:20:01 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 24 05:20:01 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 24 05:20:01 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 24 05:20:01 Trading-Agent systemd[1]: trading-bot.service: Consumed 20min 42.552s CPU time.
Sep 24 05:20:01 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 24 05:20:03 Trading-Agent python[1621711]: [firebase] connesso (Firestore + RTDB)
Sep 24 05:20:04 Trading-Agent python[1621711]: [execution] ricaricate 2 posizioni aperte da Firebase (no orfani al riavvio): ['DEXEUSDT', 'DOTUSDT']
Sep 24 05:20:04 Trading-Agent python[1621711]: [main] avvio bot @ 2026-09-24T05:20:04.296038+00:00 DRY_RUN=True
Sep 24 05:20:04 Trading-Agent python[1621711]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 05:20:04 Trading-Agent python[1621711]:   return query.where(field_path, op_string, value)
Sep 24 05:20:04 Trading-Agent python[1621711]: [main] equity riconciliata: 952.35 (base 1000.00 + realizzato -47.65 + fette aperte +0.00)
Sep 24 05:20:04 Trading-Agent python[1621711]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 24 05:20:05 Trading-Agent python[1621711]: [learning] solo 43 trade validi (servono 50): pesi INVARIATI
Sep 24 05:20:05 Trading-Agent python[1621711]: [main] pesi ricalcolati: 24 coppie strat×regime da 43 trade (30g)
Sep 24 05:20:05 Trading-Agent python[1621711]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=dexeusdt@bookTicker/dotusdt@bookTicker
Sep 24 05:20:05 Trading-Agent python[1621711]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 3/3 persi (campione 3)
Sep 24 05:20:08 Trading-Agent python[1621711]: [main] market scan...
Sep 24 05:21:00 Trading-Agent python[1621711]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 05:21:00 Trading-Agent python[1621711]:   return query.where(field_path, op_string, value)
Sep 24 05:21:00 Trading-Agent python[1621711]: [main] valutate 27 coin validate (27 nel registro): ['ZKUSDT', 'DOTUSDT', 'NEIROUSDT', 'SEIUSDT', 'TRUMPUSDT', 'USELESSUSDT', 'JTOUSDT', 'SCRUSDT', 'STXUSDT', 'VETUSDT', 'DEXEUSDT', 'PROMUSDT', 'SKYAIUSDT', 'TUTUSDT', 'HEMIUSDT', 'ORCAUSDT', 'BICOUSDT', 'MUBARAKUSDT', 'EGLDUSDT', 'HEIUSDT', 'JASMYUSDT', 'GPSUSDT', 'QUSDT', 'SPXUSDT', 'SAHARAUSDT', 'BULLAUSDT', 'SYRUPUSDT']
Sep 24 05:30:06 Trading-Agent python[1621711]: [DRY_RUN] CLOSE DEXEUSDT @ 1.9124105144172476 (stop_loss)
Sep 24 05:30:06 Trading-Agent python[1621711]: [referto] DEXEUSDT gen_fa304106: a favore fino a 0.64R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Sep 24 05:30:13 Trading-Agent python[1621711]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=dotusdt@bookTicker
Sep 24 05:31:04 Trading-Agent python[1621711]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 05:31:04 Trading-Agent python[1621711]:   return query.where(field_path, op_string, value)
Sep 24 05:31:04 Trading-Agent python[1621711]: [learning] solo 44 trade validi (servono 50): pesi INVARIATI
Sep 24 05:31:04 Trading-Agent python[1621711]: [main] pesi ricalcolati: 24 coppie strat×regime da 44 trade (30g)
Sep 24 05:31:05 Trading-Agent python[1621711]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 06:12:06 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 24 06:12:06 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 24 06:12:06 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 24 06:12:06 Trading-Agent systemd[1]: trading-bot.service: Consumed 1min 16.678s CPU time.
Sep 24 06:12:06 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 24 06:12:08 Trading-Agent python[1623011]: [firebase] connesso (Firestore + RTDB)
Sep 24 06:12:09 Trading-Agent python[1623011]: [execution] ricaricate 1 posizioni aperte da Firebase (no orfani al riavvio): ['DOTUSDT']
Sep 24 06:12:09 Trading-Agent python[1623011]: [main] avvio bot @ 2026-09-24T06:12:09.468796+00:00 DRY_RUN=True
Sep 24 06:12:09 Trading-Agent python[1623011]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 06:12:09 Trading-Agent python[1623011]:   return query.where(field_path, op_string, value)
Sep 24 06:12:09 Trading-Agent python[1623011]: [main] equity riconciliata: 950.85 (base 1000.00 + realizzato -49.15 + fette aperte +0.00)
Sep 24 06:12:09 Trading-Agent python[1623011]: [main] cooldown ricaricati: 1 coin, 0 strategie in panchina
Sep 24 06:12:10 Trading-Agent python[1623011]: [learning] solo 44 trade validi (servono 50): pesi INVARIATI
Sep 24 06:12:10 Trading-Agent python[1623011]: [main] pesi ricalcolati: 24 coppie strat×regime da 44 trade (30g)
Sep 24 06:12:10 Trading-Agent python[1623011]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=dotusdt@bookTicker
Sep 24 06:12:10 Trading-Agent python[1623011]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 06:12:13 Trading-Agent python[1623011]: [main] market scan...
Sep 24 06:13:04 Trading-Agent python[1623011]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 06:13:04 Trading-Agent python[1623011]:   return query.where(field_path, op_string, value)
Sep 24 06:13:04 Trading-Agent python[1623011]: [main] valutate 27 coin validate (27 nel registro): ['TUTUSDT', 'GPSUSDT', 'HEMIUSDT', 'SCRUSDT', 'PROMUSDT', 'USELESSUSDT', 'VETUSDT', 'ORCAUSDT', 'EGLDUSDT', 'DEXEUSDT', 'JASMYUSDT', 'TRUMPUSDT', 'BICOUSDT', 'DOTUSDT', 'NEIROUSDT', 'ZKUSDT', 'JTOUSDT', 'MUBARAKUSDT', 'STXUSDT', 'SEIUSDT', 'HEIUSDT', 'SPXUSDT', 'SYRUPUSDT', 'BULLAUSDT', 'SAHARAUSDT', 'SKYAIUSDT', 'QUSDT']
```
