# 0244-log-bot-dopo-controllo.req

_eseguito: 2026-09-25 08:35 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
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
Sep 25 06:21:12 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 25 06:21:12 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 25 06:21:12 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 25 06:21:12 Trading-Agent systemd[1]: trading-bot.service: Consumed 1min 28.542s CPU time.
Sep 25 06:21:12 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 25 06:21:14 Trading-Agent python[1665229]: [firebase] connesso (Firestore + RTDB)
Sep 25 06:21:14 Trading-Agent python[1665229]: [execution] ricaricate 3 posizioni aperte da Firebase (no orfani al riavvio): ['HEIUSDT', 'PROMUSDT', 'TUTUSDT']
Sep 25 06:21:14 Trading-Agent python[1665229]: [main] avvio bot @ 2026-09-25T06:21:14.811119+00:00 DRY_RUN=True
Sep 25 06:21:14 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 06:21:14 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 06:21:15 Trading-Agent python[1665229]: [main] equity riconciliata: 949.88 (base 1000.00 + realizzato -50.12 + fette aperte +0.00)
Sep 25 06:21:15 Trading-Agent python[1665229]: [main] cooldown ricaricati: 1 coin, 0 strategie in panchina
Sep 25 06:21:16 Trading-Agent python[1665229]: [main] pesi ricalcolati: 33 coppie strat×regime da 55 trade (30g)
Sep 25 06:21:16 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 06:21:17 Trading-Agent python[1665229]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/tutusdt@bookTicker
Sep 25 06:21:19 Trading-Agent python[1665229]: [main] market scan...
Sep 25 06:22:55 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 06:22:55 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 06:22:55 Trading-Agent python[1665229]: [main] valutate 52 coin validate (52 nel registro): ['PHAUSDT', 'XPLUSDT', 'EGLDUSDT', 'BTRUSDT', 'TRUMPUSDT', 'XRPUSDT', 'TUTUSDT', 'DOTUSDT', 'ENAUSDT', 'USELESSUSDT', 'RAYSOLUSDT', 'PENGUUSDT', 'MUBARAKUSDT', 'ZORAUSDT', 'SUIUSDT', 'JTOUSDT', 'JUPUSDT', 'SAHARAUSDT', 'SCRUSDT', 'AXSUSDT', 'B2USDT', 'SYRUPUSDT', 'HEMIUSDT', 'TSTUSDT', 'XMRUSDT', 'BULLAUSDT', 'NEIROUSDT', 'RENDERUSDT', 'SEIUSDT', 'ATOMUSDT', 'ARCUSDT', 'VETUSDT', 'SPXUSDT', 'PLUMEUSDT', 'HEIUSDT', 'BICOUSDT', 'PROMUSDT', 'GALAUSDT', 'STXUSDT', 'AVAAIUSDT', 'ZKUSDT', 'HUMAUSDT', 'PNUTUSDT', 'JASMYUSDT', 'SKYAIUSDT', 'HOMEUSDT', 'RSRUSDT', 'GPSUSDT', 'ORCAUSDT', 'EPICUSDT', 'DEXEUSDT', 'QUSDT']
Sep 25 06:24:36 Trading-Agent python[1665229]: [DRY_RUN] OPEN short RENDERUSDT qty=51.0137 @ 1.862 lev=1.0x SL=1.8936 TP=1.7672
Sep 25 06:24:43 Trading-Agent python[1665229]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/renderusdt@bookTicker/tutusdt@bookTicker
Sep 25 06:24:48 Trading-Agent python[1665229]: [ai-shadow] ok in 10.9s · 787+477 token
Sep 25 07:16:50 Trading-Agent python[1665229]: [DRY_RUN] OPEN long SAHARAUSDT qty=10000.7969 @ 0.009498 lev=1.0x SL=0.0094 TP=0.0098
Sep 25 07:16:56 Trading-Agent python[1665229]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/promusdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 07:16:58 Trading-Agent python[1665229]: [ai-shadow] ok in 7.9s · 784+379 token
Sep 25 07:21:44 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 07:21:44 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 07:21:45 Trading-Agent python[1665229]: [main] pesi ricalcolati: 33 coppie strat×regime da 55 trade (30g)
Sep 25 07:21:45 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 07:32:05 Trading-Agent python[1665229]: [DRY_RUN] OPEN short XPLUSDT qty=575.6922 @ 0.11643 lev=1.0x SL=0.1223 TP=0.0987
Sep 25 07:32:06 Trading-Agent python[1665229]: [DRY_RUN] OPEN short NEIROUSDT qty=1051911.0670 @ 9.03e-05 lev=1.0x SL=0.0001 TP=0.0001
Sep 25 07:32:12 Trading-Agent python[1665229]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=heiusdt@bookTicker/neirousdt@bookTicker/promusdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 07:32:18 Trading-Agent python[1665229]: [ai-shadow] ok in 11.6s · 871+616 token
Sep 25 07:36:37 Trading-Agent python[1665229]: [DRY_RUN] CLOSE HEIUSDT @ 0.14087799926342626 (stop_loss)
Sep 25 07:36:37 Trading-Agent python[1665229]: [referto] HEIUSDT gen_e6ddc613: a favore fino a 0.88R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Sep 25 07:36:41 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 07:36:41 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 07:36:41 Trading-Agent python[1665229]: [main] pesi ricalcolati: 34 coppie strat×regime da 56 trade (30g)
Sep 25 07:36:42 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 07:36:48 Trading-Agent python[1665229]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=neirousdt@bookTicker/promusdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 07:47:02 Trading-Agent python[1665229]: [DRY_RUN] OPEN short STXUSDT qty=303.6476 @ 0.312 lev=1.0x SL=0.3168 TP=0.2977
Sep 25 07:47:08 Trading-Agent python[1665229]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=neirousdt@bookTicker/promusdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/stxusdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 07:47:14 Trading-Agent python[1665229]: [ai-shadow] ok in 11.8s · 782+576 token
Sep 25 08:04:12 Trading-Agent python[1665229]: [DRY_RUN] CLOSE PROMUSDT @ 5.54025 (trailing_stop)
Sep 25 08:04:16 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 08:04:16 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 08:04:16 Trading-Agent python[1665229]: [main] pesi ricalcolati: 35 coppie strat×regime da 57 trade (30g)
Sep 25 08:04:16 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 08:04:20 Trading-Agent python[1665229]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=neirousdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/stxusdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 08:17:48 Trading-Agent python[1665229]: [DRY_RUN] CLOSE STXUSDT @ 0.31676721375772265 (stop_loss)
Sep 25 08:17:48 Trading-Agent python[1665229]: [referto] STXUSDT gen_acfd527a: mai andato a favore (mfe 0.00R): direzione sbagliata
Sep 25 08:17:49 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 08:17:49 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 08:17:50 Trading-Agent python[1665229]: [main] pesi ricalcolati: 36 coppie strat×regime da 58 trade (30g)
Sep 25 08:17:50 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 08:17:57 Trading-Agent python[1665229]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=neirousdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker/xplusdt@bookTicker
Sep 25 08:29:02 Trading-Agent python[1665229]: [DRY_RUN] CLOSE XPLUSDT @ 0.12233614758194834 (stop_loss)
Sep 25 08:29:02 Trading-Agent python[1665229]: [referto] XPLUSDT gen_b437a671: a favore fino a 0.47R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
Sep 25 08:29:04 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 08:29:04 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 08:29:04 Trading-Agent python[1665229]: [main] pesi ricalcolati: 37 coppie strat×regime da 59 trade (30g)
Sep 25 08:29:05 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 08:29:09 Trading-Agent python[1665229]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=neirousdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 08:31:51 Trading-Agent python[1665229]: [DRY_RUN] OPEN short ENAUSDT qty=420.3962 @ 0.2244 lev=1.0x SL=0.2304 TP=0.2153
Sep 25 08:31:58 Trading-Agent python[1665229]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/renderusdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 08:32:02 Trading-Agent python[1665229]: [ai-shadow] ok in 10.1s · 779+494 token
Sep 25 08:32:33 Trading-Agent python[1665229]: [DRY_RUN] CLOSE RENDERUSDT @ 1.8935850012972295 (stop_loss)
Sep 25 08:32:33 Trading-Agent python[1665229]: [referto] RENDERUSDT gen_acfd527a: a favore fino a 0.65R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Sep 25 08:32:39 Trading-Agent python[1665229]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 08:32:43 Trading-Agent python[1665229]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 08:32:43 Trading-Agent python[1665229]:   return query.where(field_path, op_string, value)
Sep 25 08:32:44 Trading-Agent python[1665229]: [main] pesi ricalcolati: 38 coppie strat×regime da 60 trade (30g)
Sep 25 08:32:44 Trading-Agent python[1665229]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 08:33:53 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 25 08:33:53 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 25 08:33:53 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 25 08:33:53 Trading-Agent systemd[1]: trading-bot.service: Consumed 8min 30.017s CPU time.
Sep 25 08:33:53 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 25 08:33:54 Trading-Agent python[1675343]: [firebase] connesso (Firestore + RTDB)
Sep 25 08:33:55 Trading-Agent python[1675343]: [execution] ricaricate 4 posizioni aperte da Firebase (no orfani al riavvio): ['ENAUSDT', 'NEIROUSDT', 'SAHARAUSDT', 'TUTUSDT']
Sep 25 08:33:55 Trading-Agent python[1675343]: [main] avvio bot @ 2026-09-25T08:33:55.284730+00:00 DRY_RUN=True
Sep 25 08:33:55 Trading-Agent python[1675343]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 08:33:55 Trading-Agent python[1675343]:   return query.where(field_path, op_string, value)
Sep 25 08:33:55 Trading-Agent python[1675343]: [main] equity riconciliata: 941.64 (base 1000.00 + realizzato -58.36 + fette aperte +0.00)
Sep 25 08:33:55 Trading-Agent python[1675343]: [main] cooldown ricaricati: 4 coin, 0 strategie in panchina
Sep 25 08:33:56 Trading-Agent python[1675343]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 08:33:57 Trading-Agent python[1675343]: [main] pesi ricalcolati: 38 coppie strat×regime da 60 trade (30g)
Sep 25 08:33:57 Trading-Agent python[1675343]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 08:33:59 Trading-Agent python[1675343]: [controllo] pubblicato: sistema verde, paper giallo, 1 anomalie, 1441 ms
Sep 25 08:34:02 Trading-Agent python[1675343]: [main] market scan...
```
