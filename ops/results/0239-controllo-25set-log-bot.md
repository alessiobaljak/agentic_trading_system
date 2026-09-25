# 0239-controllo-25set-log-bot.req

_eseguito: 2026-09-25 06:10 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 24 15:02:05 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 52 trade (30g)
Sep 24 15:02:05 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 15:02:10 Trading-Agent python[1626778]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/heiusdt@bookTicker
Sep 24 15:16:56 Trading-Agent python[1626778]: [main] market scan...
Sep 24 15:17:49 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 15:17:49 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 15:17:49 Trading-Agent python[1626778]: [main] valutate 27 coin validate (27 nel registro): ['BULLAUSDT', 'SEIUSDT', 'SCRUSDT', 'JASMYUSDT', 'JTOUSDT', 'STXUSDT', 'TRUMPUSDT', 'EGLDUSDT', 'GPSUSDT', 'DOTUSDT', 'SKYAIUSDT', 'SPXUSDT', 'MUBARAKUSDT', 'SYRUPUSDT', 'ORCAUSDT', 'NEIROUSDT', 'ZKUSDT', 'HEIUSDT', 'BICOUSDT', 'HEMIUSDT', 'VETUSDT', 'DEXEUSDT', 'SAHARAUSDT', 'USELESSUSDT', 'TUTUSDT', 'PROMUSDT', 'QUSDT']
Sep 24 15:17:50 Trading-Agent python[1626778]: [DRY_RUN] CLOSE GPSUSDT @ 0.01143075 (trailing_stop)
Sep 24 15:17:51 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 15:17:52 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 15:17:58 Trading-Agent python[1626778]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker
Sep 24 16:18:04 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 16:18:04 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 16:18:05 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 16:18:06 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 16:18:38 Trading-Agent python[1626778]: [main] verdetto trailing assegnato a 1 trade paper
Sep 24 17:18:23 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 17:18:23 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 17:18:24 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 17:18:24 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 18:18:27 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 18:18:27 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 18:18:27 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 18:18:28 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 19:17:07 Trading-Agent python[1626778]: [main] market scan...
Sep 24 19:17:57 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 19:17:57 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 19:17:57 Trading-Agent python[1626778]: [main] valutate 27 coin validate (27 nel registro): ['JTOUSDT', 'MUBARAKUSDT', 'SYRUPUSDT', 'TRUMPUSDT', 'DOTUSDT', 'BULLAUSDT', 'SKYAIUSDT', 'PROMUSDT', 'EGLDUSDT', 'TUTUSDT', 'SPXUSDT', 'SEIUSDT', 'QUSDT', 'HEIUSDT', 'USELESSUSDT', 'STXUSDT', 'HEMIUSDT', 'VETUSDT', 'NEIROUSDT', 'BICOUSDT', 'JASMYUSDT', 'SAHARAUSDT', 'ZKUSDT', 'GPSUSDT', 'SCRUSDT', 'ORCAUSDT', 'DEXEUSDT']
Sep 24 19:18:29 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 19:18:29 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 20:18:40 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 20:18:40 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 20:18:40 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 20:18:41 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 21:18:46 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 21:18:46 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 21:18:47 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 21:18:47 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 22:18:53 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 22:18:53 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 22:18:54 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 22:18:54 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 23:17:32 Trading-Agent python[1626778]: [main] market scan...
Sep 24 23:19:05 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 23:19:05 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 23:19:06 Trading-Agent python[1626778]: [main] valutate 50 coin validate (50 nel registro): ['PHAUSDT', 'HEMIUSDT', 'XPLUSDT', 'MUBARAKUSDT', 'PENGUUSDT', 'PROMUSDT', 'USELESSUSDT', 'ENAUSDT', 'HEIUSDT', 'DEXEUSDT', 'SPXUSDT', 'TUTUSDT', 'BULLAUSDT', 'RSRUSDT', 'XMRUSDT', 'STXUSDT', 'SKYAIUSDT', 'GPSUSDT', 'EPICUSDT', 'XRPUSDT', 'ZKUSDT', 'JASMYUSDT', 'PLUMEUSDT', 'EGLDUSDT', 'RAYSOLUSDT', 'BTRUSDT', 'TSTUSDT', 'TRUMPUSDT', 'SYRUPUSDT', 'SUIUSDT', 'ARCUSDT', 'PNUTUSDT', 'HOMEUSDT', 'B2USDT', 'VETUSDT', 'JTOUSDT', 'SEIUSDT', 'ZORAUSDT', 'BICOUSDT', 'SAHARAUSDT', 'DOTUSDT', 'RENDERUSDT', 'JUPUSDT', 'ATOMUSDT', 'AVAAIUSDT', 'AXSUSDT', 'SCRUSDT', 'NEIROUSDT', 'ORCAUSDT', 'QUSDT']
Sep 24 23:19:37 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 24 23:19:37 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 23:46:49 Trading-Agent python[1626778]: [DRY_RUN] OPEN short XPLUSDT qty=553.7330 @ 0.11185 lev=1.0x SL=0.1180 TP=0.0995
Sep 24 23:46:56 Trading-Agent python[1626778]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/xplusdt@bookTicker
Sep 24 23:47:05 Trading-Agent python[1626778]: [ai-shadow] ok in 7.8s · 830+445 token
Sep 25 00:17:13 Trading-Agent python[1626778]: [ai-shadow] ok in 7.1s · 787+370 token
Sep 25 00:19:46 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 00:19:46 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 00:19:46 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31

[... 1208 caratteri omessi (testa e coda conservate) ...]

 [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 01:32:27 Trading-Agent python[1626778]: [ai-shadow] ok in 15.4s · 831+444 token
Sep 25 01:47:13 Trading-Agent python[1626778]: [ai-shadow] ok in 9.0s · 831+437 token
Sep 25 02:06:28 Trading-Agent python[1626778]: [DRY_RUN] CLOSE BULLAUSDT @ 0.10420750000000001 (trailing_stop)
Sep 25 02:06:30 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 02:06:30 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 02:06:30 Trading-Agent python[1626778]: [main] pesi ricalcolati: 32 coppie strat×regime da 54 trade (30g)
Sep 25 02:06:30 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 02:06:34 Trading-Agent python[1626778]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/xplusdt@bookTicker
Sep 25 02:16:50 Trading-Agent python[1626778]: [DRY_RUN] OPEN long PROMUSDT qty=17.4191 @ 5.473 lev=1.0x SL=5.3447 TP=5.6654
Sep 25 02:16:56 Trading-Agent python[1626778]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/xplusdt@bookTicker
Sep 25 02:16:58 Trading-Agent python[1626778]: [ai-shadow] ok in 7.7s · 789+404 token
Sep 25 02:47:11 Trading-Agent python[1626778]: [DRY_RUN] OPEN short TUTUSDT qty=7075.5512 @ 0.02598 lev=2.0x SL=0.0268 TP=0.0247
Sep 25 02:47:19 Trading-Agent python[1626778]: [ai-shadow] ok in 8.1s · 789+407 token
Sep 25 02:47:20 Trading-Agent python[1626778]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 03:06:44 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 03:06:44 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 03:06:44 Trading-Agent python[1626778]: [main] pesi ricalcolati: 32 coppie strat×regime da 54 trade (30g)
Sep 25 03:06:45 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 03:17:50 Trading-Agent python[1626778]: [main] market scan...
Sep 25 03:19:27 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 03:19:27 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 03:19:27 Trading-Agent python[1626778]: [main] valutate 50 coin validate (50 nel registro): ['MUBARAKUSDT', 'TUTUSDT', 'PLUMEUSDT', 'DEXEUSDT', 'RAYSOLUSDT', 'TSTUSDT', 'PENGUUSDT', 'USELESSUSDT', 'ENAUSDT', 'SCRUSDT', 'SKYAIUSDT', 'JASMYUSDT', 'GPSUSDT', 'RSRUSDT', 'DOTUSDT', 'HEIUSDT', 'BULLAUSDT', 'AXSUSDT', 'RENDERUSDT', 'HEMIUSDT', 'SUIUSDT', 'AVAAIUSDT', 'XRPUSDT', 'PHAUSDT', 'SEIUSDT', 'JTOUSDT', 'STXUSDT', 'NEIROUSDT', 'BTRUSDT', 'TRUMPUSDT', 'PROMUSDT', 'XPLUSDT', 'EPICUSDT', 'B2USDT', 'PNUTUSDT', 'ZKUSDT', 'ORCAUSDT', 'SPXUSDT', 'JUPUSDT', 'VETUSDT', 'SYRUPUSDT', 'BICOUSDT', 'ZORAUSDT', 'ARCUSDT', 'SAHARAUSDT', 'HOMEUSDT', 'ATOMUSDT', 'XMRUSDT', 'EGLDUSDT', 'QUSDT']
Sep 25 04:06:45 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 04:06:45 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 04:06:46 Trading-Agent python[1626778]: [main] pesi ricalcolati: 32 coppie strat×regime da 54 trade (30g)
Sep 25 04:06:46 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 05:06:52 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 05:06:52 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 05:06:52 Trading-Agent python[1626778]: [main] pesi ricalcolati: 32 coppie strat×regime da 54 trade (30g)
Sep 25 05:06:53 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 05:24:50 Trading-Agent python[1626778]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 05:57:57 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 25 05:57:57 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 25 05:57:57 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 25 05:57:57 Trading-Agent systemd[1]: trading-bot.service: Consumed 40min 12.830s CPU time, 99.8M memory peak, 0B memory swap peak.
Sep 25 05:57:57 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 25 05:57:59 Trading-Agent python[1664220]: [firebase] connesso (Firestore + RTDB)
Sep 25 05:58:00 Trading-Agent python[1664220]: [execution] ricaricate 4 posizioni aperte da Firebase (no orfani al riavvio): ['HEIUSDT', 'PROMUSDT', 'TUTUSDT', 'XPLUSDT']
Sep 25 05:58:00 Trading-Agent python[1664220]: [main] avvio bot @ 2026-09-25T05:58:00.108513+00:00 DRY_RUN=True
Sep 25 05:58:00 Trading-Agent python[1664220]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 05:58:00 Trading-Agent python[1664220]:   return query.where(field_path, op_string, value)
Sep 25 05:58:00 Trading-Agent python[1664220]: [main] equity riconciliata: 953.35 (base 1000.00 + realizzato -46.65 + fette aperte +0.00)
Sep 25 05:58:00 Trading-Agent python[1664220]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 25 05:58:01 Trading-Agent python[1664220]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 05:58:01 Trading-Agent python[1664220]: [main] pesi ricalcolati: 32 coppie strat×regime da 54 trade (30g)
Sep 25 05:58:02 Trading-Agent python[1664220]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 05:58:04 Trading-Agent python[1664220]: [main] market scan...
Sep 25 05:59:45 Trading-Agent python[1664220]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 05:59:45 Trading-Agent python[1664220]:   return query.where(field_path, op_string, value)
Sep 25 05:59:45 Trading-Agent python[1664220]: [main] valutate 52 coin validate (52 nel registro): ['PHAUSDT', 'BTRUSDT', 'EGLDUSDT', 'TUTUSDT', 'VETUSDT', 'USELESSUSDT', 'JUPUSDT', 'XPLUSDT', 'RAYSOLUSDT', 'PENGUUSDT', 'ATOMUSDT', 'XRPUSDT', 'ENAUSDT', 'ARCUSDT', 'AXSUSDT', 'ZKUSDT', 'TRUMPUSDT', 'MUBARAKUSDT', 'TSTUSDT', 'SEIUSDT', 'JTOUSDT', 'SUIUSDT', 'SYRUPUSDT', 'B2USDT', 'BULLAUSDT', 'ZORAUSDT', 'PLUMEUSDT', 'NEIROUSDT', 'RENDERUSDT', 'SPXUSDT', 'GALAUSDT', 'PROMUSDT', 'HUMAUSDT', 'DOTUSDT', 'SAHARAUSDT', 'BICOUSDT', 'XMRUSDT', 'JASMYUSDT', 'PNUTUSDT', 'EPICUSDT', 'HOMEUSDT', 'STXUSDT', 'GPSUSDT', 'RSRUSDT', 'SCRUSDT', 'ORCAUSDT', 'AVAAIUSDT', 'HEIUSDT', 'SKYAIUSDT', 'HEMIUSDT', 'DEXEUSDT', 'QUSDT']
Sep 25 06:09:08 Trading-Agent python[1664220]: [DRY_RUN] CLOSE XPLUSDT @ 0.11800683846600449 (stop_loss)
Sep 25 06:09:08 Trading-Agent python[1664220]: [referto] XPLUSDT gen_a220b439: a favore fino a 0.67R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
Sep 25 06:09:09 Trading-Agent python[1664220]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 06:09:09 Trading-Agent python[1664220]:   return query.where(field_path, op_string, value)
Sep 25 06:09:09 Trading-Agent python[1664220]: [main] pesi ricalcolati: 33 coppie strat×regime da 55 trade (30g)
Sep 25 06:09:10 Trading-Agent python[1664220]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 06:09:18 Trading-Agent python[1664220]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/tutusdt@bookTicker
```
