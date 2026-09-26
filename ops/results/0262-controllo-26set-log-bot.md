# 0262-controllo-26set-log-bot.req

_eseguito: 2026-09-26 06:05 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 25 20:05:46 Trading-Agent python[1688981]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 20:29:56 Trading-Agent python[1688981]: [main] market scan...
Sep 25 20:31:34 Trading-Agent python[1688981]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 20:31:34 Trading-Agent python[1688981]:   return query.where(field_path, op_string, value)
Sep 25 20:31:35 Trading-Agent python[1688981]: [main] valutate 52 coin validate (52 nel registro): ['SEIUSDT', 'JTOUSDT', 'SUIUSDT', 'NEIROUSDT', 'ENAUSDT', 'PENGUUSDT', 'GALAUSDT', 'GPSUSDT', 'JUPUSDT', 'PHAUSDT', 'PROMUSDT', 'DOTUSDT', 'ZORAUSDT', 'BTRUSDT', 'MUBARAKUSDT', 'PNUTUSDT', 'STXUSDT', 'SPXUSDT', 'RENDERUSDT', 'EGLDUSDT', 'TRUMPUSDT', 'ORCAUSDT', 'VETUSDT', 'AXSUSDT', 'EPICUSDT', 'DEXEUSDT', 'TUTUSDT', 'RSRUSDT', 'PLUMEUSDT', 'XPLUSDT', 'ATOMUSDT', 'USELESSUSDT', 'XMRUSDT', 'RAYSOLUSDT', 'XRPUSDT', 'QUSDT', 'BICOUSDT', 'JASMYUSDT', 'ZKUSDT', 'HUMAUSDT', 'TSTUSDT', 'ARCUSDT', 'HEMIUSDT', 'SAHARAUSDT', 'BULLAUSDT', 'HEIUSDT', 'HOMEUSDT', 'SCRUSDT', 'SYRUPUSDT', 'SKYAIUSDT', 'AVAAIUSDT', 'B2USDT']
Sep 25 20:32:06 Trading-Agent python[1688981]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 20:32:07 Trading-Agent python[1688981]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 20:32:08 Trading-Agent python[1688981]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1644 ms
Sep 25 20:36:27 Trading-Agent python[1688981]: [main] verdetto trailing assegnato a 2 trade paper
Sep 25 20:46:49 Trading-Agent python[1688981]: [selettore] ORCAUSDT gen_fca11c08 short p=0.64 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 20:46:49 Trading-Agent python[1688981]: [DRY_RUN] OPEN short ORCAUSDT qty=112.0281 @ 1.672 lev=2.0x SL=1.7007 TP=1.5859
Sep 25 20:46:58 Trading-Agent python[1688981]: [ai-shadow] ok in 8.5s · 792+429 token
Sep 25 20:46:59 Trading-Agent python[1688981]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=orcausdt@bookTicker/qusdt@bookTicker
Sep 25 20:57:02 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Sep 25 20:57:02 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Sep 25 20:57:02 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Sep 25 20:57:02 Trading-Agent systemd[1]: trading-bot.service: Consumed 6min 30.024s CPU time.
Sep 25 20:57:02 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Sep 25 20:57:04 Trading-Agent python[1696285]: [firebase] connesso (Firestore + RTDB)
Sep 25 20:57:05 Trading-Agent python[1696285]: [execution] ricaricate 2 posizioni aperte da Firebase (no orfani al riavvio): ['ORCAUSDT', 'QUSDT']
Sep 25 20:57:05 Trading-Agent python[1696285]: [main] avvio bot @ 2026-09-25T20:57:05.320248+00:00 DRY_RUN=True
Sep 25 20:57:05 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 20:57:05 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 25 20:57:05 Trading-Agent python[1696285]: [main] equity riconciliata: 936.55 (base 1000.00 + realizzato -63.45 + fette aperte +0.00)
Sep 25 20:57:05 Trading-Agent python[1696285]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina
Sep 25 20:57:05 Trading-Agent python[1696285]: [selettore] modello caricato: 41404 righe, soglia 0.45, verdetto NON BATTE, stato ombra, generato 2026-09-25T12:08:12.711365+00:00 -> solo ombra, non decide
Sep 25 20:57:06 Trading-Agent python[1696285]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=orcausdt@bookTicker/qusdt@bookTicker
Sep 25 20:57:08 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 20:57:09 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 20:57:10 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1504 ms
Sep 25 20:57:13 Trading-Agent python[1696285]: [main] market scan...
Sep 25 20:58:56 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 20:58:56 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 25 20:58:57 Trading-Agent python[1696285]: [main] valutate 52 coin validate (52 nel registro): ['SEIUSDT', 'SUIUSDT', 'DOTUSDT', 'ORCAUSDT', 'VETUSDT', 'RSRUSDT', 'JTOUSDT', 'SPXUSDT', 'ENAUSDT', 'JUPUSDT', 'ATOMUSDT', 'TRUMPUSDT', 'PHAUSDT', 'PENGUUSDT', 'GALAUSDT', 'MUBARAKUSDT', 'PROMUSDT', 'NEIROUSDT', 'JASMYUSDT', 'BULLAUSDT', 'RENDERUSDT', 'AXSUSDT', 'HOMEUSDT', 'RAYSOLUSDT', 'ARCUSDT', 'EPICUSDT', 'STXUSDT', 'GPSUSDT', 'PNUTUSDT', 'PLUMEUSDT', 'XPLUSDT', 'TUTUSDT', 'ZKUSDT', 'XMRUSDT', 'BTRUSDT', 'DEXEUSDT', 'XRPUSDT', 'USELESSUSDT', 'HUMAUSDT', 'QUSDT', 'AVAAIUSDT', 'SYRUPUSDT', 'HEMIUSDT', 'ZORAUSDT', 'TSTUSDT', 'SAHARAUSDT', 'SCRUSDT', 'EGLDUSDT', 'SKYAIUSDT', 'HEIUSDT', 'BICOUSDT', 'B2USDT']
Sep 25 21:00:39 Trading-Agent python[1696285]: [rifiuto] ORCAUSDT gen_fca11c08 short: posizione gia' aperta su questa coin
Sep 25 21:00:48 Trading-Agent python[1696285]: [ai-shadow] ok in 8.2s · 792+382 token
Sep 25 21:57:09 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 21:57:09 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 25 21:57:09 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 82 trade (30g)
Sep 25 21:57:10 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 21:57:12 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1521 ms
Sep 25 22:20:17 Trading-Agent python[1696285]: [DRY_RUN] CLOSE ORCAUSDT @ 1.6517499999999998 (trailing_stop)
Sep 25 22:20:20 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 22:20:20 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 25 22:20:21 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 83 trade (30g)
Sep 25 22:20:21 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 22:20:24 Trading-Agent python[1696285]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=qusdt@bookTicker
Sep 25 22:32:15 Trading-Agent python[1696285]: [selettore] SYRUPUSDT gen_b7d57ce7 short p=0.57 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 25 22:32:15 Trading-Agent python[1696285]: [DRY_RUN] OPEN short SYRUPUSDT qty=426.4862 @ 0.22006 lev=1.0x SL=0.2234 TP=0.2134
Sep 25 22:32:22 Trading-Agent python[1696285]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=qusdt@bookTicker/syrupusdt@bookTicker
Sep 25 22:32:25 Trading-Agent python[1696285]: [ai-shadow] ok in 8.9s · 799+447 token
Sep 25 22:50:43 Trading-Agent python[1696285]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 22:57:24 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 25 22:57:24 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 25 22:57:24 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 83 trade (30g)
Sep 25 22:57:25 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 22:57:27 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1531 ms
Sep 25 23:16:56 Trading-Agent python[1696285]: [rifiuto] QUSDT gen_18c839a0 long: posizione gia' aperta su questa coin
Sep 25 23:17:04 Trading-Agent python[1696285]: [ai-shadow] ok in 7.7s · 833+425 token
Sep 25 23:21:14 Trading-Agent python[1696285]: [main] verdetto trailing assegnato a 1 trade paper
Sep 25 23:32:14 Trading-Agent python[1696285]: [rifiuto] QUSDT gen_bf2be656 long: posizione gia' aperta su questa coin
Sep 25 23:32:23 Trading-Agent python[1696285]: [ai-shadow] ok in 9.0s · 791+370 token
Sep 25 23:57:49 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the '

[... 273 caratteri omessi (testa e coda conservate) ...]

t python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 25 23:57:52 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1637 ms
Sep 26 00:13:46 Trading-Agent python[1696285]: [price_agent] GET /fapi/v1/premiumIndex fallito: 429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/premiumIndex?symbol=QUSDT
Sep 26 00:13:56 Trading-Agent python[1696285]: [price_agent] GET /fapi/v1/premiumIndex fallito: 429 Client Error: Too Many Requests for url: https://fapi.binance.com/fapi/v1/premiumIndex?symbol=SYRUPUSDT
Sep 26 00:57:10 Trading-Agent python[1696285]: [main] market scan...
Sep 26 00:58:49 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 00:58:49 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 00:58:50 Trading-Agent python[1696285]: [main] valutate 52 coin validate (52 nel registro): ['MUBARAKUSDT', 'ENAUSDT', 'AXSUSDT', 'XPLUSDT', 'HOMEUSDT', 'JTOUSDT', 'TUTUSDT', 'PROMUSDT', 'PENGUUSDT', 'SEIUSDT', 'BICOUSDT', 'SUIUSDT', 'ATOMUSDT', 'TRUMPUSDT', 'PNUTUSDT', 'ZKUSDT', 'XRPUSDT', 'NEIROUSDT', 'RSRUSDT', 'PLUMEUSDT', 'USELESSUSDT', 'GALAUSDT', 'DOTUSDT', 'SYRUPUSDT', 'TSTUSDT', 'JUPUSDT', 'QUSDT', 'ORCAUSDT', 'HEIUSDT', 'RAYSOLUSDT', 'XMRUSDT', 'HUMAUSDT', 'GPSUSDT', 'SPXUSDT', 'SAHARAUSDT', 'EPICUSDT', 'ARCUSDT', 'RENDERUSDT', 'DEXEUSDT', 'JASMYUSDT', 'STXUSDT', 'BTRUSDT', 'ZORAUSDT', 'HEMIUSDT', 'VETUSDT', 'EGLDUSDT', 'PHAUSDT', 'AVAAIUSDT', 'B2USDT', 'SCRUSDT', 'SKYAIUSDT', 'BULLAUSDT']
Sep 26 00:59:21 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 83 trade (30g)
Sep 26 00:59:22 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 00:59:23 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1414 ms
Sep 26 01:07:48 Trading-Agent python[1696285]: [main] verdetto trailing assegnato a 1 trade paper
Sep 26 01:59:41 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 01:59:41 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 01:59:42 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 83 trade (30g)
Sep 26 01:59:42 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 01:59:44 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1504 ms
Sep 26 03:00:01 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 03:00:01 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 03:00:01 Trading-Agent python[1696285]: [main] pesi ricalcolati: 51 coppie strat×regime da 83 trade (30g)
Sep 26 03:00:02 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 03:00:04 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 5 anomalie, 1533 ms
Sep 26 03:08:28 Trading-Agent python[1696285]: [main] verdetto trailing assegnato a 1 trade paper
Sep 26 03:13:37 Trading-Agent python[1696285]: [DRY_RUN] CLOSE QUSDT @ 0.02396434780733142 (stop_loss)
Sep 26 03:13:37 Trading-Agent python[1696285]: [referto] QUSDT gen_bf2be656: a favore fino a 0.43R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
Sep 26 03:13:39 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 03:13:39 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 03:13:40 Trading-Agent python[1696285]: [main] pesi ricalcolati: 52 coppie strat×regime da 84 trade (30g)
Sep 26 03:13:40 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 03:13:43 Trading-Agent python[1696285]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=syrupusdt@bookTicker
Sep 26 03:47:02 Trading-Agent python[1696285]: [selettore] NEIROUSDT gen_e132204b long p=0.66 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 26 03:47:02 Trading-Agent python[1696285]: [DRY_RUN] OPEN long NEIROUSDT qty=998691.3013 @ 9.375e-05 lev=1.0x SL=0.0001 TP=0.0001
Sep 26 03:47:09 Trading-Agent python[1696285]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=neirousdt@bookTicker/syrupusdt@bookTicker
Sep 26 03:47:10 Trading-Agent python[1696285]: [ai-shadow] ok in 7.7s · 787+400 token
Sep 26 04:00:03 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 04:00:03 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 04:00:03 Trading-Agent python[1696285]: [main] pesi ricalcolati: 52 coppie strat×regime da 84 trade (30g)
Sep 26 04:00:04 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 04:00:06 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 5 anomalie, 1578 ms
Sep 26 04:57:22 Trading-Agent python[1696285]: [main] market scan...
Sep 26 04:59:23 Trading-Agent python[1696285]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 26 04:59:23 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 04:59:23 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 04:59:24 Trading-Agent python[1696285]: [main] valutate 62 coin validate (62 nel registro): ['PROMUSDT', 'QUSDT', 'ENAUSDT', 'SUPERUSDT', 'VETUSDT', 'JTOUSDT', 'JUPUSDT', 'USELESSUSDT', 'XPLUSDT', 'BTRUSDT', 'SAHARAUSDT', 'THEUSDT', 'PENGUUSDT', 'JASMYUSDT', 'SKYAIUSDT', 'DOTUSDT', 'TUTUSDT', 'XRPUSDT', 'RAYSOLUSDT', 'TRUMPUSDT', 'RSRUSDT', 'GALAUSDT', 'MUBARAKUSDT', 'TSTUSDT', 'PNUTUSDT', 'SUIUSDT', 'XMRUSDT', 'EPICUSDT', 'RENDERUSDT', 'ATOMUSDT', 'FLOCKUSDT', 'HUMAUSDT', 'PLUMEUSDT', 'WALUSDT', 'SEIUSDT', 'ZORAUSDT', 'AXSUSDT', 'BULLAUSDT', 'SPXUSDT', 'DEXEUSDT', 'ARCUSDT', 'PHAUSDT', 'SCRUSDT', 'ORCAUSDT', 'NEIROUSDT', 'STXUSDT', 'ZKUSDT', 'SOPHUSDT', 'OPENUSDT', 'HEMIUSDT', 'GPSUSDT', 'SYRUPUSDT', 'HEIUSDT', 'EGLDUSDT', 'CROSSUSDT', 'B2USDT', 'TAUSDT', 'BICOUSDT', 'MITOUSDT', 'AVAAIUSDT', 'HOMEUSDT', 'ONGUSDT']
Sep 26 05:00:27 Trading-Agent python[1696285]: [main] pesi ricalcolati: 52 coppie strat×regime da 84 trade (30g)
Sep 26 05:00:28 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 05:00:30 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 5 anomalie, 1697 ms
Sep 26 06:02:14 Trading-Agent python[1696285]: [main] trade bloccato dal gate: stop troppo largo: 9.2% del prezzo > 6% (ATR gonfiato: primo incasso a +14%, lock a +7%)
Sep 26 06:02:14 Trading-Agent python[1696285]: [rifiuto] MUBARAKUSDT gen_ff3e4154 long: risk gate: stop troppo largo: 9.2% del prezzo > 6% (ATR gonfiato: primo incasso a +14%, lock a +7%)
Sep 26 06:02:26 Trading-Agent python[1696285]: [ai-shadow] ok in 12.0s · 885+608 token
Sep 26 06:02:58 Trading-Agent python[1696285]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 26 06:02:58 Trading-Agent python[1696285]:   return query.where(field_path, op_string, value)
Sep 26 06:02:58 Trading-Agent python[1696285]: [main] pesi ricalcolati: 52 coppie strat×regime da 84 trade (30g)
Sep 26 06:02:59 Trading-Agent python[1696285]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_ba3a671f: solo_short — long 5/5 persi (campione 5) | gen_fa304106: solo_long — short 4/4 persi (campione 4)
Sep 26 06:03:00 Trading-Agent python[1696285]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1485 ms
```
