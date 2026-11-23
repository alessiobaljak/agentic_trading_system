# 0768-23nov-log-ribilancio-1000.req

_eseguito: 2026-11-23 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 22 12:20:51 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 12:28:19 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3885 (controllo 1426 · registro 1413 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 12:28:23 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1891 ms
Nov 22 12:31:01 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 12:31:01 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 13:20:59 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 13:28:43 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3885 (controllo 1426 · registro 1413 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 13:28:46 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1809 ms
Nov 22 13:31:54 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 13:31:54 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 14:21:12 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 14:28:57 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3884 (controllo 1426 · registro 1412 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 14:29:01 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1851 ms
Nov 22 14:33:11 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 14:33:11 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 15:21:19 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 15:29:10 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3887 (controllo 1426 · registro 1415 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 15:29:14 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1878 ms
Nov 22 15:34:38 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 15:34:38 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 15:47:09 Trading-Agent python[465569]: [main] market scan...
Nov 22 15:48:42 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 22 15:49:01 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 22 15:49:49 Trading-Agent python[465569]: [scanner] 14 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 22 15:49:49 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 15:49:49 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 15:49:49 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BRUSDT', 'HUMAUSDT', 'IDOLUSDT', 'AKTUSDT', 'BLESSUSDT', 'KERNELUSDT', 'MUBARAKUSDT', 'TAUSDT', 'HYPEUSDT', 'XVGUSDT', 'HOLOUSDT', 'PUMPUSDT', 'PHAUSDT', 'MYXUSDT', 'BTRUSDT', 'BULLAUSDT', 'RAYSOLUSDT', 'PENGUUSDT', 'XPINUSDT', 'AVAAIUSDT', 'CATIUSDT', 'JTOUSDT', 'ZECUSDT', 'TRUMPUSDT', 'CAKEUSDT', 'AGTUSDT', 'UBUSDT', 'SCRUSDT', 'XMRUSDT', 'GRASSUSDT', 'FORMUSDT', 'TAOUSDT', '1000BONKUSDT', 'ENAUSDT', 'VELVETUSDT', 'GPSUSDT', 'ALCHUSDT', 'ASTERUSDT', '1000PEPEUSDT', 'PARTIUSDT', 'QUSDT', 'DEXEUSDT', 'AINUSDT', 'RENDERUSDT', 'USELESSUSDT', 'SKYAIUSDT', 'HUSDT', 'BANKUSDT', 'BIOUSDT', 'AIOUSDT', 'HIVEUSDT', 'JUPUSDT', 'PNUTUSDT', 'TUTUSDT', 'GALAUSDT', '0GUSDT', 'STXUSDT', 'TAKEUSDT', 'SAHARAUSDT', 'ZORAUSDT', 'GUNUSDT', 'SYRUPUSDT', 'ARKMUSDT', 'EIGENUSDT', 'BSVUSDT', 'HOMEUSDT', 'HEMIUSDT', 'PLUMEUSDT', 'HEIUSDT', 'FLOCKUSDT', 'MAVIAUSDT', 'SPXUSDT', 'CROSSUSDT', 'OPENUSDT', 'BMTUSDT', 'IDUSDT', 'PUNDIXUSDT', 'RUNEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 22 16:21:42 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 16:29:11 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3885 (controllo 1426 · registro 1412 · trade 885 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 16:29:14 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1801 ms
Nov 22 16:36:07 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 16:36:07 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 17:22:03 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 17:29:48 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3886 (controllo 1426 · registro 1412 · trade 886 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 17:29:51 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1877 ms
Nov 22 17:37:15 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 17:37:15 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 18:22:42 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 18:30:04 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3887 (controllo 1426 · registro 1412 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 18:30:08 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2349 ms
Nov 22 18:38:26 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 18:38:26 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 19:22:45 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 19:30:22 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3891 (controllo 1426 · registro 1416 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 19:30:25 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1672 ms
Nov 22 19:39:53 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 19:39:53 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 19:47:31 Trading-Agent python[465569]: [main] market scan...
Nov 22 19:49:00 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 22 19:49:19 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 22 19:50:07 Trading-Agent python[465569]: [scanner] 15 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 22 19:50:07 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 19:50:07 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 19:50:08 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'HYPEUSDT', 'AGTUSDT', 'PUMPUSDT', 'BANKUSDT', 'ENAUSDT', 'AINUSDT', 'AVAAIUSDT', 'HEMIUSDT', 'HEIUSDT', 'HOLOUSDT', 'AKTUSDT', 'PHAUSDT', 'KERNELUSDT', 'CROSSUSDT', 'HIVEUSDT', 'ASTERUSDT', 'JUPUSDT', 'RUNEUSDT', 'USELESSUSDT', 'JTOUSDT', 'ZECUSDT', 'XPINUSDT', 'TAOUSDT', 'SKYAIUSDT', 'BLESSUSDT', '1000PEPEUSDT', 'PENGUUSDT', 'BRUSDT', 'VELVETUSDT', 'SAHARAUSDT', 'CATIUSDT', 'XMRUSDT', 'BULLAUSDT', 'RENDERUSDT', 'TRUMPU

[... 2824 caratteri omessi (testa e coda conservate) ...]

rd argument instead.
Nov 22 22:43:21 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 23:23:18 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 22 23:31:17 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3893 (controllo 1426 · registro 1417 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 22 23:31:20 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1453 ms
Nov 22 23:31:20 Trading-Agent python[465569]: [learning] foto del 2026-11-23 scritta: 249 validate, 99 pesi strategia×regime
Nov 22 23:31:20 Trading-Agent python[465569]: [giorni] riga del 2026-11-22: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 22 23:45:01 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 23:45:01 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 23:47:44 Trading-Agent python[465569]: [main] market scan...
Nov 22 23:49:14 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 22 23:49:31 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 22 23:50:20 Trading-Agent python[465569]: [scanner] 17 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 22 23:50:20 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 22 23:50:20 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 22 23:50:20 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BULLAUSDT', 'KERNELUSDT', 'ZECUSDT', 'SAHARAUSDT', 'PENGUUSDT', 'HUMAUSDT', 'PUMPUSDT', 'HYPEUSDT', 'XPINUSDT', 'CROSSUSDT', 'ZORAUSDT', 'HIVEUSDT', 'ENAUSDT', 'BANKUSDT', 'CAKEUSDT', 'TAOUSDT', 'TRUMPUSDT', '1000PEPEUSDT', 'OPENUSDT', 'HOLOUSDT', 'ARKMUSDT', 'ASTERUSDT', 'HUSDT', 'AINUSDT', 'BRUSDT', 'AVAAIUSDT', 'USELESSUSDT', 'MUBARAKUSDT', 'GPSUSDT', 'SKYAIUSDT', '0GUSDT', 'PUNDIXUSDT', 'PNUTUSDT', '1000BONKUSDT', 'SPXUSDT', 'RAYSOLUSDT', 'TAUSDT', 'MYXUSDT', 'BSVUSDT', 'IDUSDT', 'CATIUSDT', 'STXUSDT', 'RENDERUSDT', 'BLESSUSDT', 'DEXEUSDT', 'VELVETUSDT', 'GUNUSDT', 'AGTUSDT', 'IDOLUSDT', 'FLOCKUSDT', 'AKTUSDT', 'GALAUSDT', 'EIGENUSDT', 'PHAUSDT', 'UBUSDT', 'JTOUSDT', 'XMRUSDT', 'TUTUSDT', 'GRASSUSDT', 'PLUMEUSDT', 'BMTUSDT', 'SCRUSDT', 'JUPUSDT', 'SYRUPUSDT', 'ALCHUSDT', 'QUSDT', 'FORMUSDT', 'HEIUSDT', 'HOMEUSDT', 'BTRUSDT', 'BIOUSDT', 'PARTIUSDT', 'HEMIUSDT', 'RUNEUSDT', 'MAVIAUSDT', 'AIOUSDT', 'TAKEUSDT', 'MITOUSDT', 'PTBUSDT', 'XVGUSDT']
Nov 23 00:09:19 Trading-Agent python[465569]: [paper_f5] ribilancio del 2026-11-23: universo 100, long 31, short 28, costo 1.35, equity 10558.39
Nov 23 00:13:32 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-23: universo 100, long 30, short 29, costo 1.08, equity 10498.43
Nov 23 00:17:48 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-23: universo 100, long 32, short 26, costo 1.06, equity 10448.92
Nov 23 00:22:02 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-23: universo 100, long 30, short 29, costo 1.27, equity 10767.87
Nov 23 00:22:37 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-23: 27 ordini limite sul conto, 4 rifiutati
Nov 23 00:23:09 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 00:23:09 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 00:31:30 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3887 (controllo 1426 · registro 1411 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 00:31:32 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1493 ms
Nov 23 00:38:26 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 00:38:26 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 01:05:31 Trading-Agent python[465569]: [paper_f5] ordini limite del 2026-11-23: 64 eseguiti su 64, costo 1.35 (tutto a mercato 4.71)
Nov 23 01:10:02 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-23: 63 eseguiti su 63, costo 1.08 (tutto a mercato 3.80)
Nov 23 01:14:01 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-23: 63 eseguiti su 63, costo 1.06 (tutto a mercato 3.70)
Nov 23 01:18:31 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-23: 63 eseguiti su 63, costo 1.27 (tutto a mercato 4.44)
Nov 23 01:24:04 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 01:31:49 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3886 (controllo 1426 · registro 1410 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 01:31:52 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1491 ms
Nov 23 01:39:53 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 01:39:53 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 02:24:10 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 02:31:52 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3886 (controllo 1426 · registro 1410 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 02:31:55 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1492 ms
Nov 23 02:41:37 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 02:41:37 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 03:24:25 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 03:32:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3889 (controllo 1426 · registro 1413 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 03:32:12 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1361 ms
Nov 23 03:42:40 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 03:42:40 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 03:47:48 Trading-Agent python[465569]: [main] market scan...
Nov 23 03:49:17 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 23 03:49:34 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 23 03:50:22 Trading-Agent python[465569]: [scanner] 15 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 23 03:50:22 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 03:50:22 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 03:50:22 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['AVAAIUSDT', 'JUPUSDT', 'IDOLUSDT', 'HUSDT', 'GPSUSDT', 'GALAUSDT', 'XMRUSDT', '1000BONKUSDT', 'FLOCKUSDT', 'UBUSDT', 'ZECUSDT', '1000PEPEUSDT', 'BLESSUSDT', 'ENAUSDT', 'JTOUSDT', 'PNUTUSDT', 'DEXEUSDT', 'AIOUSDT', 'HEMIUSDT', 'MYXUSDT', 'STXUSDT', 'HYPEUSDT', 'PENGUUSDT', 'KERNELUSDT', 'OPENUSDT', 'CAKEUSDT', 'BRUSDT', 'PLUMEUSDT', 'SKYAIUSDT', 'PUNDIXUSDT', 'BIOUSDT', 'CROSSUSDT', 'AGTUSDT', 'PUMPUSDT', 'TAKEUSDT', 'HEIUSDT', 'AINUSDT', 'VELVETUSDT', 'AKTUSDT', 'QUSDT', 'USELESSUSDT', 'TAOUSDT', 'RENDERUSDT', 'HUMAUSDT', 'TUTUSDT', 'HOLOUSDT', '0GUSDT', 'HOMEUSDT', 'PARTIUSDT', 'ARKMUSDT', 'RUNEUSDT', 'BTRUSDT', 'ASTERUSDT', 'MUBARAKUSDT', 'TRUMPUSDT', 'RAYSOLUSDT', 'SPXUSDT', 'SAHARAUSDT', 'FORMUSDT', 'IDUSDT', 'ZORAUSDT', 'GRASSUSDT', 'PHAUSDT', 'TAUSDT', 'GUNUSDT', 'SYRUPUSDT', 'XVGUSDT', 'BANKUSDT', 'EIGENUSDT', 'HIVEUSDT', 'ALCHUSDT', 'CATIUSDT', 'BMTUSDT', 'MAVIAUSDT', 'SCRUSDT', 'BSVUSDT', 'XPINUSDT', 'MITOUSDT', 'PTBUSDT', 'BULLAUSDT']
```
