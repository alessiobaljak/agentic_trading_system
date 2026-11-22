# 0766-22nov-log-ribilancio-1000.req

_eseguito: 2026-11-22 04:20 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 21 12:21:27 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1566 ms
Nov 21 12:32:04 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 12:32:04 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 13:03:04 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 13:21:42 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3879 (controllo 1426 · registro 1403 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 13:21:45 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1603 ms
Nov 21 13:32:30 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 13:32:30 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 14:03:08 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 14:22:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3879 (controllo 1426 · registro 1403 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 14:22:12 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1625 ms
Nov 21 14:33:42 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 14:33:42 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 15:03:33 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 15:22:35 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3882 (controllo 1426 · registro 1406 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 15:22:38 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1880 ms
Nov 21 15:35:19 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 15:35:19 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 15:46:02 Trading-Agent python[465569]: [main] market scan...
Nov 21 15:47:30 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 21 15:47:48 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 21 15:48:36 Trading-Agent python[465569]: [scanner] 3 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 21 15:48:36 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 15:48:36 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 15:48:37 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['EIGENUSDT', 'BULLAUSDT', 'UBUSDT', 'PNUTUSDT', 'AVAAIUSDT', 'ZECUSDT', 'PUMPUSDT', 'HIVEUSDT', 'TRUMPUSDT', 'MYXUSDT', 'USELESSUSDT', 'RAYSOLUSDT', 'TAOUSDT', 'ENAUSDT', 'GRASSUSDT', 'RENDERUSDT', 'FORMUSDT', 'SPXUSDT', 'HOLOUSDT', 'PENGUUSDT', 'STXUSDT', 'PHAUSDT', 'AKTUSDT', 'MAVIAUSDT', 'DEXEUSDT', 'TUTUSDT', 'HYPEUSDT', 'JTOUSDT', 'IDUSDT', 'ALCHUSDT', 'XMRUSDT', 'BRUSDT', 'HEIUSDT', '1000PEPEUSDT', 'JUPUSDT', 'ASTERUSDT', 'GUNUSDT', 'CAKEUSDT', 'VELVETUSDT', 'IDOLUSDT', 'GPSUSDT', 'BLESSUSDT', 'BIOUSDT', 'GALAUSDT', 'SKYAIUSDT', 'PUNDIXUSDT', '0GUSDT', 'OPENUSDT', 'HEMIUSDT', 'PARTIUSDT', 'HUMAUSDT', '1000BONKUSDT', 'AGTUSDT', 'BTRUSDT', 'SAHARAUSDT', 'MUBARAKUSDT', 'FLOCKUSDT', 'AIOUSDT', 'XVGUSDT', 'ARKMUSDT', 'SYRUPUSDT', 'HUSDT', 'SCRUSDT', 'BSVUSDT', 'CROSSUSDT', 'RUNEUSDT', 'PLUMEUSDT', 'TAUSDT', 'AINUSDT', 'KERNELUSDT', 'HOMEUSDT', 'BMTUSDT', 'QUSDT', 'ZORAUSDT', 'BANKUSDT', 'CATIUSDT', 'TAKEUSDT', 'XPINUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 21 16:03:44 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 16:23:01 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3880 (controllo 1426 · registro 1404 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 16:23:04 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1716 ms
Nov 21 16:36:01 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 16:36:01 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 17:03:57 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 17:23:14 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3880 (controllo 1426 · registro 1404 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 17:23:17 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1889 ms
Nov 21 17:36:52 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 17:36:52 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 18:04:09 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 18:23:40 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3881 (controllo 1426 · registro 1405 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 18:23:43 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1734 ms
Nov 21 18:37:51 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 18:37:51 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 19:04:38 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 19:23:55 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3884 (controllo 1426 · registro 1408 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 19:23:59 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2048 ms
Nov 21 19:39:15 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 19:39:15 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 19:46:13 Trading-Agent python[465569]: [main] market scan...
Nov 21 19:47:44 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 21 19:48:02 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 21 19:48:50 Trading-Agent python[465569]: [scanner] 4 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 21 19:48:50 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 19:48:50 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 19:48:50 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'BULLAUSDT', 'PHAUSDT', 'HYPEUSDT', 'SKYAIUSDT', 'RAYSOLUSDT', 'AINUSDT', 'TRUMPUSDT', 'HUSDT', 'XMRUSDT', 'ZECUSDT', 'PARTIUSDT', 'RENDERUSDT', 'USELESSUSDT', 'CAKEUSDT', 'JTOUSDT', 'BANKUSDT', 'BMTUSDT', 'ALCHUSDT', 'BLESSUSDT', 'GPSUSDT', 'HOMEUSDT', 'STXUSDT', 'GUNUSDT', 'SCRUSDT', 'PENGUUSDT', 'PUMPUSDT', '1000PEPEUSDT', 'HUMAUSDT', 'TAUSDT', 'AVAAIUSDT', 'BRUSDT', 'UBUSDT', 'ENAUSDT', 'TAOUSDT', 'HOLOUSDT', 'GRASSUSDT', 'QUSDT', 'ASTERUSDT', 'CATIUSDT', 'HEIUSDT', 'ARKMUSDT', 'OPENUSDT', 'MYXUSDT', 'SPXUSDT', '0GUSDT', 'XVGUSDT', 'JUPUSDT', 'ZORAUSDT', 'BSVUSDT', 'BIOUSDT', 'GALAUSDT', 'PNUTUSDT', 'VELVETUSDT', 'AKTUSDT', 'XPINUSDT', 'FLOCKUSDT', 'AIOUSDT', 'EIGENUSDT', 'TAKEUSDT', 'MAVIAUSDT', 'SYRUPUSDT', 'PUNDIXUSDT', 'CROSSUSD

[... 2806 caratteri omessi (testa e coda conservate) ...]

 3884 (controllo 1426 · registro 1410 · trade 886 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 23:24:59 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1768 ms
Nov 21 23:24:59 Trading-Agent python[465569]: [learning] foto del 2026-11-22 scritta: 249 validate, 99 pesi strategia×regime
Nov 21 23:24:59 Trading-Agent python[465569]: [giorni] riga del 2026-11-21: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 21 23:28:55 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 23:28:55 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 23:46:18 Trading-Agent python[465569]: [main] market scan...
Nov 21 23:47:49 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 21 23:48:06 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 21 23:48:53 Trading-Agent python[465569]: [scanner] 6 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 21 23:48:53 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BSVUSDT', 'GPSUSDT', 'FORMUSDT', 'SKYAIUSDT', 'XVGUSDT', 'PNUTUSDT', 'JUPUSDT', 'ALCHUSDT', 'HOLOUSDT', 'AIOUSDT', 'HUSDT', 'TRUMPUSDT', 'PUMPUSDT', 'SPXUSDT', 'BIOUSDT', 'PHAUSDT', 'BRUSDT', 'PUNDIXUSDT', 'ASTERUSDT', 'ZECUSDT', 'IDUSDT', 'IDOLUSDT', 'BULLAUSDT', 'XMRUSDT', 'CATIUSDT', 'STXUSDT', 'PARTIUSDT', 'ENAUSDT', 'AINUSDT', 'AKTUSDT', 'BLESSUSDT', 'USELESSUSDT', '1000PEPEUSDT', 'VELVETUSDT', 'KERNELUSDT', 'BANKUSDT', 'HEMIUSDT', 'TAOUSDT', 'HYPEUSDT', 'SAHARAUSDT', 'HUMAUSDT', 'GRASSUSDT', '0GUSDT', 'BMTUSDT', '1000BONKUSDT', 'RAYSOLUSDT', 'AVAAIUSDT', 'HEIUSDT', 'HOMEUSDT', 'MAVIAUSDT', 'UBUSDT', 'PENGUUSDT', 'QUSDT', 'GALAUSDT', 'XPINUSDT', 'JTOUSDT', 'GUNUSDT', 'FLOCKUSDT', 'ARKMUSDT', 'AGTUSDT', 'MUBARAKUSDT', 'TAKEUSDT', 'RENDERUSDT', 'TAUSDT', 'TUTUSDT', 'HIVEUSDT', 'SYRUPUSDT', 'ZORAUSDT', 'EIGENUSDT', 'DEXEUSDT', 'PLUMEUSDT', 'BTRUSDT', 'MYXUSDT', 'CROSSUSDT', 'OPENUSDT', 'SCRUSDT', 'CAKEUSDT', 'RUNEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 21 23:59:42 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 23:59:42 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 00:09:16 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-22: universo 100, long 26, short 31, costo 0.38, equity 10715.91
Nov 22 00:13:29 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-22: universo 100, long 30, short 27, costo 0.45, equity 10621.64
Nov 22 00:17:44 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-22: universo 100, long 26, short 31, costo 0.39, equity 11013.51
Nov 22 00:17:54 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-22: 4 ordini limite sul conto, 3 rifiutati
Nov 22 00:18:31 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 00:18:31 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 00:25:20 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3882 (controllo 1426 · registro 1408 · trade 886 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 00:25:23 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1644 ms
Nov 22 00:33:34 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 00:33:34 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 00:39:52 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 22 00:40:31 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 22 00:41:10 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 22 01:05:41 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-22: 57 eseguiti su 57, costo 0.38 (tutto a mercato 1.33)
Nov 22 01:10:01 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-22: 58 eseguiti su 58, costo 0.45 (tutto a mercato 1.59)
Nov 22 01:13:51 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-22: 57 eseguiti su 57, costo 0.39 (tutto a mercato 1.38)
Nov 22 01:18:11 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 01:25:32 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3883 (controllo 1426 · registro 1408 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 01:25:34 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1419 ms
Nov 22 01:34:21 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 01:34:21 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 02:18:20 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 02:25:56 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3886 (controllo 1426 · registro 1410 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 02:25:59 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1622 ms
Nov 22 02:35:04 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 02:35:04 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 03:18:36 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 03:26:27 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3889 (controllo 1426 · registro 1413 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 03:26:29 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1457 ms
Nov 22 03:35:55 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 03:35:55 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 03:46:20 Trading-Agent python[465569]: [main] market scan...
Nov 22 03:47:46 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 22 03:48:04 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 22 03:48:52 Trading-Agent python[465569]: [scanner] 9 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 22 03:48:52 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 03:48:52 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 03:48:52 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BULLAUSDT', 'BANKUSDT', 'QUSDT', 'BTRUSDT', 'PLUMEUSDT', 'HYPEUSDT', 'AIOUSDT', 'IDOLUSDT', 'ALCHUSDT', 'BRUSDT', 'HUSDT', 'DEXEUSDT', 'SPXUSDT', 'ZECUSDT', '1000PEPEUSDT', 'IDUSDT', 'CROSSUSDT', 'TAOUSDT', 'BLESSUSDT', 'HEIUSDT', 'ZORAUSDT', 'USELESSUSDT', '0GUSDT', 'TUTUSDT', 'GUNUSDT', 'UBUSDT', 'XMRUSDT', 'PUMPUSDT', 'SAHARAUSDT', 'MYXUSDT', 'PENGUUSDT', 'ARKMUSDT', 'TAUSDT', 'JTOUSDT', 'RUNEUSDT', 'VELVETUSDT', 'ENAUSDT', 'OPENUSDT', 'RAYSOLUSDT', 'HIVEUSDT', 'MAVIAUSDT', 'SKYAIUSDT', 'KERNELUSDT', 'PHAUSDT', 'GALAUSDT', 'HOMEUSDT', 'EIGENUSDT', 'TRUMPUSDT', 'AVAAIUSDT', 'HOLOUSDT', 'AINUSDT', 'PARTIUSDT', 'CAKEUSDT', 'XVGUSDT', 'JUPUSDT', 'GPSUSDT', 'TAKEUSDT', 'HEMIUSDT', 'AKTUSDT', 'CATIUSDT', 'BIOUSDT', 'PNUTUSDT', 'MUBARAKUSDT', 'FORMUSDT', 'ASTERUSDT', 'FLOCKUSDT', '1000BONKUSDT', 'STXUSDT', 'RENDERUSDT', 'SCRUSDT', 'GRASSUSDT', 'XPINUSDT', 'SYRUPUSDT', 'HUMAUSDT', 'BSVUSDT', 'PUNDIXUSDT', 'AGTUSDT', 'BMTUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 22 04:18:58 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
```
