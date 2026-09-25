# 0248-log-bot-controllo.req

_eseguito: 2026-09-25 11:43 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 25 08:54:37 Trading-Agent python[1675917]: [main] equity riconciliata: 941.64 (base 1000.00 + realizzato -58.36 + fette aperte +0.00)
Sep 25 08:54:37 Trading-Agent python[1675917]: [main] cooldown ricaricati: 3 coin, 0 strategie in panchina
Sep 25 08:54:39 Trading-Agent python[1675917]: [main] pesi ricalcolati: 38 coppie strat×regime da 60 trade (30g)
Sep 25 08:54:39 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 08:54:39 Trading-Agent python[1675917]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 08:54:41 Trading-Agent python[1675917]: [controllo] pubblicato: sistema verde, paper giallo, 1 anomalie, 1496 ms
Sep 25 08:54:44 Trading-Agent python[1675917]: [main] market scan...
Sep 25 08:56:23 Trading-Agent python[1675917]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 08:56:23 Trading-Agent python[1675917]:   return query.where(field_path, op_string, value)
Sep 25 08:56:23 Trading-Agent python[1675917]: [main] valutate 52 coin validate (52 nel registro): ['XPLUSDT', 'BTRUSDT', 'SEIUSDT', 'JTOUSDT', 'EGLDUSDT', 'RENDERUSDT', 'TSTUSDT', 'JASMYUSDT', 'PENGUUSDT', 'ZKUSDT', 'PLUMEUSDT', 'HUMAUSDT', 'GALAUSDT', 'XRPUSDT', 'JUPUSDT', 'SUIUSDT', 'SYRUPUSDT', 'AXSUSDT', 'DOTUSDT', 'SPXUSDT', 'TRUMPUSDT', 'TUTUSDT', 'ORCAUSDT', 'XMRUSDT', 'SKYAIUSDT', 'USELESSUSDT', 'RSRUSDT', 'ATOMUSDT', 'NEIROUSDT', 'STXUSDT', 'ENAUSDT', 'AVAAIUSDT', 'PHAUSDT', 'GPSUSDT', 'HEMIUSDT', 'MUBARAKUSDT', 'PROMUSDT', 'SAHARAUSDT', 'RAYSOLUSDT', 'HEIUSDT', 'ZORAUSDT', 'EPICUSDT', 'HOMEUSDT', 'QUSDT', 'DEXEUSDT', 'BULLAUSDT', 'PNUTUSDT', 'VETUSDT', 'BICOUSDT', 'ARCUSDT', 'SCRUSDT', 'B2USDT']
Sep 25 09:02:00 Trading-Agent python[1675917]: [DRY_RUN] OPEN short HUMAUSDT qty=3582.2883 @ 0.026286 lev=1.0x SL=0.0268 TP=0.0254
Sep 25 09:02:01 Trading-Agent python[1675917]: [DRY_RUN] OPEN short ORCAUSDT qty=58.3059 @ 1.615 lev=1.0x SL=1.6400 TP=1.5400
Sep 25 09:02:07 Trading-Agent python[1675917]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/humausdt@bookTicker/neirousdt@bookTicker/orcausdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 09:02:14 Trading-Agent python[1675917]: [ai-shadow] ok in 12.6s · 869+610 token
Sep 25 09:07:36 Trading-Agent python[1675917]: [DRY_RUN] SCALE-OUT 3000.2391 SAHARAUSDT @ 0.009728066027280931 (netto +0.6447, residuo 7000.5579)
Sep 25 09:32:05 Trading-Agent python[1675917]: [DRY_RUN] OPEN short JTOUSDT qty=337.1730 @ 0.5225 lev=2.0x SL=0.5350 TP=0.5037
Sep 25 09:32:05 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 09:32:06 Trading-Agent python[1675917]: [DRY_RUN] OPEN short SKYAIUSDT qty=2048.8910 @ 0.04599 lev=1.0x SL=0.0465 TP=0.0445
Sep 25 09:32:11 Trading-Agent python[1675917]: [price_stream] connesso · 8 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/humausdt@bookTicker/jtousdt@bookTicker/neirousdt@bookTicker/orcausdt@bookTicker/saharausdt@bookTicker/skyaiusdt@bookTicker/tutusdt@bookTicker
Sep 25 09:32:21 Trading-Agent python[1675917]: [ai-shadow] ok in 14.2s · 1064+779 token
Sep 25 09:47:16 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: posizione gia' aperta su questa coin
Sep 25 09:47:16 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 09:47:26 Trading-Agent python[1675917]: [ai-shadow] ok in 10.0s · 823+481 token
Sep 25 09:49:39 Trading-Agent python[1675917]: [DRY_RUN] CLOSE JTOUSDT @ 0.5350045308331959 (stop_loss)
Sep 25 09:49:39 Trading-Agent python[1675917]: [referto] JTOUSDT gen_f238d283: mai andato a favore (mfe 0.03R): direzione sbagliata · controtrend rispetto al regime all'ingresso
Sep 25 09:49:41 Trading-Agent python[1675917]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 09:49:41 Trading-Agent python[1675917]:   return query.where(field_path, op_string, value)
Sep 25 09:49:41 Trading-Agent python[1675917]: [main] pesi ricalcolati: 38 coppie strat×regime da 61 trade (30g)
Sep 25 09:49:41 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 09:49:45 Trading-Agent python[1675917]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/humausdt@bookTicker/neirousdt@bookTicker/orcausdt@bookTicker/saharausdt@bookTicker/skyaiusdt@bookTicker/tutusdt@bookTicker
Sep 25 10:01:51 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:01:51 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (49m)
Sep 25 10:02:01 Trading-Agent python[1675917]: [ai-shadow] ok in 10.3s · 821+554 token
Sep 25 10:17:16 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:17:16 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (34m)
Sep 25 10:17:26 Trading-Agent python[1675917]: [ai-shadow] ok in 9.9s · 821+506 token
Sep 25 10:17:58 Trading-Agent python[1675917]: [DRY_RUN] CLOSE HUMAUSDT @ 0.025828 (trailing_stop)
Sep 25 10:18:00 Trading-Agent python[1675917]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 10:18:00 Trading-Agent python[1675917]:   return query.where(field_path, op_string, value)
Sep 25 10:18:01 Trading-Agent python[1675917]: [main] pesi ricalcolati: 39 coppie strat×regime da 62 trade (30g)
Sep 25 10:18:02 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 10:18:04 Trading-Agent python[1675917]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/orcausdt@bookTicker/saharausdt@bookTicker/skyaiusdt@bookTicker/tutusdt@bookTicker
Sep 25 10:32:09 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 10:32:09 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (19m)
Sep 25 10:32:18 Trading-Agent python[1675917]: [ai-shadow] ok in 9.1s · 821+501 token
Sep 25 10:32:50 Trading-Agent python[1675917]: [DRY_RUN] CLOSE ORCAUSDT @ 1.6399921584261172 (stop_loss)
Sep 25 10:32:50 Trading-Agent python[1675917]: [referto] ORCAUSDT gen_fca11c08: mai andato a favore (mfe 0.22R): direzione sbagliata · controtrend rispetto al regime all'ingresso
Sep 25 10:32:52 Trading-Agent python[1675917]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 10:32:52 Trading-Agent python[1675917]:   return query.where(field_path, op_string, value)
Sep 25 10:32:53 Trading-Agent python[1675917]: [main] pesi ricalcolati: 40 coppie strat×regime da 63 trade (30g)
Sep 25 10:32:54 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 10:32:57 Trading-Agent python[1675917]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/skyaiusdt@bookTicker/tutusdt@bookTicker
Sep 25 10:42:28 Trading-Agent python[1675917]: [DRY_RUN] CLOSE SKYAIUSDT @ 0.045705 (trailing_stop)
Sep 25 10:42:35 Trading-Agent python[1675917]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 10:42:39 Trading-Agent python[1675917]: [main] pesi ricalcolati: 41 coppie strat×regime da 64 trade (30g)
Sep 25 10:42:39 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 10:47:02 Trading-Agent python[1675917]: [DRY_RUN] OPEN short HUMAUSDT qty=3504.4135 @ 0.026771 lev=1.0x SL=0.0275 TP=0.0247
Sep 25 10:47:03 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: cooldown dopo stop (4m)
Sep 25 10:47:03 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (47m)
Sep 25 10:47:12 Trading-Agent python[1675917]: [ai-shadow] ok in 9.5s · 875+527 token
Sep 25 10:47:12 Trading-Agent python[1675917]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/humausdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 10:57:59 Trading-Agent python[1675917]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 11:01:52 Trading-Agent python[1675917]: [DRY_RUN] OPEN short SUIUSDT qty=87.7529 @ 1.0691 lev=1.0x SL=1.0901 TP=1.0376
Sep 25 11:01:53 Trading-Agent python[1675917]: [DRY_RUN] OPEN short JTOUSDT qty=245.1295 @ 0.5481 lev=2.0x SL=0.5640 TP=0.5242
Sep 25 11:01:53 Trading-Agent python[1675917]: [rifiuto] HUMAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 11:01:58 Trading-Agent python[1675917]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=enausdt@bookTicker/humausdt@bookTicker/jtousdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/suiusdt@bookTicker/tutusdt@bookTicker
Sep 25 11:02:06 Trading-Agent python[1675917]: [ai-shadow] ok in 12.7s · 872+650 token
Sep 25 11:02:36 Trading-Agent python[1675917]: [DRY_RUN] CLOSE ENAUSDT @ 0.23044098601642599 (stop_loss)
Sep 25 11:02:36 Trading-Agent python[1675917]: [referto] ENAUSDT gen_bb762669: a favore fino a 0.66R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Sep 25 11:02:40 Trading-Agent python[1675917]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 11:02:40 Trading-Agent python[1675917]:   return query.where(field_path, op_string, value)
Sep 25 11:02:40 Trading-Agent python[1675917]: [main] pesi ricalcolati: 42 coppie strat×regime da 65 trade (30g)
Sep 25 11:02:41 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 11:02:47 Trading-Agent python[1675917]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=humausdt@bookTicker/jtousdt@bookTicker/neirousdt@bookTicker/saharausdt@bookTicker/suiusdt@bookTicker/tutusdt@bookTicker
Sep 25 11:05:53 Trading-Agent python[1675917]: [DRY_RUN] CLOSE NEIROUSDT @ 9.183844726705407e-05 (stop_loss)
Sep 25 11:05:53 Trading-Agent python[1675917]: [referto] NEIROUSDT gen_f3124a14: a favore fino a 0.41R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
Sep 25 11:05:57 Trading-Agent python[1675917]: [main] pesi ricalcolati: 43 coppie strat×regime da 66 trade (30g)
Sep 25 11:05:57 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 11:05:59 Trading-Agent python[1675917]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=humausdt@bookTicker/jtousdt@bookTicker/saharausdt@bookTicker/suiusdt@bookTicker/tutusdt@bookTicker
Sep 25 11:07:00 Trading-Agent python[1675917]: [DRY_RUN] CLOSE HUMAUSDT @ 0.027470953231962743 (stop_loss)
Sep 25 11:07:00 Trading-Agent python[1675917]: [referto] HUMAUSDT gen_fca11c08: mai andato a favore (mfe 0.00R): direzione sbagliata
Sep 25 11:07:09 Trading-Agent python[1675917]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=jtousdt@bookTicker/saharausdt@bookTicker/suiusdt@bookTicker/tutusdt@bookTicker
Sep 25 11:07:11 Trading-Agent python[1675917]: [main] pesi ricalcolati: 44 coppie strat×regime da 67 trade (30g)
Sep 25 11:07:11 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 11:12:58 Trading-Agent python[1675917]: [DRY_RUN] CLOSE SUIUSDT @ 1.0901049969686643 (stop_loss)
Sep 25 11:12:58 Trading-Agent python[1675917]: [referto] SUIUSDT gen_490a90e5: mai andato a favore (mfe 0.07R): direzione sbagliata · controtrend rispetto al regime all'ingresso
Sep 25 11:13:01 Trading-Agent python[1675917]: [main] pesi ricalcolati: 45 coppie strat×regime da 68 trade (30g)
Sep 25 11:13:01 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 11:13:08 Trading-Agent python[1675917]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=jtousdt@bookTicker/saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] USELESSUSDT gen_2031005e: peso 0.26: confidenza 16 < soglia 30
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] JTOUSDT gen_f238d283 short: posizione gia' aperta su questa coin
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (51m)
Sep 25 11:16:48 Trading-Agent python[1675917]: [rifiuto] ORCAUSDT gen_fca11c08 short: cooldown dopo stop (17m)
Sep 25 11:17:00 Trading-Agent python[1675917]: [ai-shadow] ok in 11.8s · 918+633 token
Sep 25 11:32:13 Trading-Agent python[1675917]: [rifiuto] USELESSUSDT gen_2031005e: peso 0.26: confidenza 16 < soglia 30
Sep 25 11:32:13 Trading-Agent python[1675917]: [rifiuto] HUMAUSDT gen_fca11c08 short: cooldown dopo stop (36m)
Sep 25 11:32:23 Trading-Agent python[1675917]: [ai-shadow] ok in 9.4s · 830+524 token
Sep 25 11:38:06 Trading-Agent python[1675917]: [DRY_RUN] CLOSE JTOUSDT @ 0.5412 (trailing_stop)
Sep 25 11:38:08 Trading-Agent python[1675917]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 11:38:08 Trading-Agent python[1675917]:   return query.where(field_path, op_string, value)
Sep 25 11:38:09 Trading-Agent python[1675917]: [main] pesi ricalcolati: 45 coppie strat×regime da 69 trade (30g)
Sep 25 11:38:09 Trading-Agent python[1675917]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 11:38:13 Trading-Agent python[1675917]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 11:42:41 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 25 11:42:41 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 25 11:42:41 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 25 11:42:41 Trading-Agent systemd[1]: trading-bot.service: Consumed 10min 30.834s CPU time.
Sep 25 11:42:41 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 25 11:42:43 Trading-Agent python[1681701]: [firebase] connesso (Firestore + RTDB)
Sep 25 11:42:44 Trading-Agent python[1681701]: [execution] ricaricate 2 posizioni aperte da Firebase (no orfani al riavvio): ['SAHARAUSDT', 'TUTUSDT']
Sep 25 11:42:44 Trading-Agent python[1681701]: [main] avvio bot @ 2026-09-25T11:42:44.022537+00:00 DRY_RUN=True
Sep 25 11:42:44 Trading-Agent python[1681701]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 11:42:44 Trading-Agent python[1681701]:   return query.where(field_path, op_string, value)
Sep 25 11:42:44 Trading-Agent python[1681701]: [main] equity riconciliata: 930.77 (base 1000.00 + realizzato -69.88 + fette aperte +0.64)
Sep 25 11:42:44 Trading-Agent python[1681701]: [main] cooldown ricaricati: 4 coin, 0 strategie in panchina
Sep 25 11:42:45 Trading-Agent python[1681701]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=saharausdt@bookTicker/tutusdt@bookTicker
Sep 25 11:42:46 Trading-Agent python[1681701]: [main] pesi ricalcolati: 45 coppie strat×regime da 69 trade (30g)
Sep 25 11:42:46 Trading-Agent python[1681701]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 11:42:48 Trading-Agent python[1681701]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1558 ms
Sep 25 11:42:51 Trading-Agent python[1681701]: [main] market scan...
```
