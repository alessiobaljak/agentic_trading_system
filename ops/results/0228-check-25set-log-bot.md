# 0228-check-25set-log-bot.req

_eseguito: 2026-09-25 05:10 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.6s

```
Sep 24 12:32:41 Trading-Agent python[1626778]: [main] pesi ricalcolati: 29 coppie strat×regime da 50 trade (30g)
Sep 24 12:32:42 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 12:32:42 Trading-Agent python[1626778]: [DRY_RUN] CLOSE JTOUSDT @ 0.45852499999999996 (trailing_stop)
Sep 24 12:32:44 Trading-Agent python[1626778]: [main] pesi ricalcolati: 30 coppie strat×regime da 51 trade (30g)
Sep 24 12:32:45 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 12:32:50 Trading-Agent python[1626778]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker
Sep 24 13:16:15 Trading-Agent python[1626778]: [DRY_RUN] OPEN long GPSUSDT qty=8390.6675 @ 0.011326 lev=1.0x SL=0.0111 TP=0.0118
Sep 24 13:16:22 Trading-Agent python[1626778]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/heiusdt@bookTicker
Sep 24 13:16:27 Trading-Agent python[1626778]: [ai-shadow] ok in 11.4s · 788+508 token
Sep 24 13:18:33 Trading-Agent python[1626778]: [main] verdetto trailing assegnato a 1 trade paper
Sep 24 13:32:50 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 13:32:50 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 13:32:51 Trading-Agent python[1626778]: [main] pesi ricalcolati: 30 coppie strat×regime da 51 trade (30g)
Sep 24 13:32:51 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 13:33:54 Trading-Agent python[1626778]: [main] verdetto trailing assegnato a 1 trade paper
Sep 24 14:20:00 Trading-Agent python[1626778]: [main] verdetto trailing assegnato a 1 trade paper
Sep 24 14:31:14 Trading-Agent python[1626778]: [DRY_RUN] OPEN short JTOUSDT qty=196.0245 @ 0.4848 lev=1.0x SL=0.4959 TP=0.4682
Sep 24 14:31:21 Trading-Agent python[1626778]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/heiusdt@bookTicker/jtousdt@bookTicker
Sep 24 14:31:24 Trading-Agent python[1626778]: [ai-shadow] ok in 8.9s · 785+466 token
Sep 24 14:32:57 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 14:32:57 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 24 14:32:57 Trading-Agent python[1626778]: [main] pesi ricalcolati: 30 coppie strat×regime da 51 trade (30g)
Sep 24 14:32:57 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 24 14:46:35 Trading-Agent python[1626778]: [ai-shadow] ok in 10.0s · 785+511 token
Sep 24 15:02:03 Trading-Agent python[1626778]: [DRY_RUN] CLOSE JTOUSDT @ 0.4772 (trailing_stop)
Sep 24 15:02:05 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 24 15:02:05 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
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
Sep 24 20:18:41 Trading-Agent python[1626778]: 

[... 698 caratteri omessi (testa e coda conservate) ...]

Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
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
Sep 25 00:19:46 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 25 00:19:47 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 01:02:14 Trading-Agent python[1626778]: [DRY_RUN] OPEN short BULLAUSDT qty=903.9711 @ 0.10536 lev=1.0x SL=0.1074 TP=0.1013
Sep 25 01:02:20 Trading-Agent python[1626778]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bullausdt@bookTicker/heiusdt@bookTicker/xplusdt@bookTicker
Sep 25 01:02:25 Trading-Agent python[1626778]: [ai-shadow] ok in 10.5s · 970+629 token
Sep 25 01:20:08 Trading-Agent python[1626778]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 01:20:08 Trading-Agent python[1626778]:   return query.where(field_path, op_string, value)
Sep 25 01:20:09 Trading-Agent python[1626778]: [main] pesi ricalcolati: 31 coppie strat×regime da 53 trade (30g)
Sep 25 01:20:09 Trading-Agent python[1626778]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
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
```
