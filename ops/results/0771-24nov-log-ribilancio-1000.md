# 0771-24nov-log-ribilancio-1000.req

_eseguito: 2026-11-24 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 23 11:50:08 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 23 11:50:26 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 23 11:51:14 Trading-Agent python[465569]: [scanner] 15 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 23 11:51:14 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 11:51:14 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 11:51:14 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['AINUSDT', 'TAUSDT', 'VELVETUSDT', 'MUBARAKUSDT', 'PENGUUSDT', 'GPSUSDT', 'QUSDT', 'BLESSUSDT', 'AGTUSDT', 'HYPEUSDT', 'TUTUSDT', 'GALAUSDT', 'KERNELUSDT', 'CROSSUSDT', 'RAYSOLUSDT', 'RENDERUSDT', 'RUNEUSDT', 'AVAAIUSDT', 'UBUSDT', 'BMTUSDT', 'XPINUSDT', 'ENAUSDT', '1000PEPEUSDT', 'SYRUPUSDT', 'AKTUSDT', 'HOMEUSDT', 'CATIUSDT', 'ZORAUSDT', 'XVGUSDT', 'AIOUSDT', 'ZECUSDT', 'TAOUSDT', 'JUPUSDT', 'HEMIUSDT', 'BULLAUSDT', 'CAKEUSDT', 'SKYAIUSDT', 'FLOCKUSDT', 'STXUSDT', 'USELESSUSDT', 'HUMAUSDT', 'FORMUSDT', 'IDUSDT', '1000BONKUSDT', 'IDOLUSDT', '0GUSDT', 'XMRUSDT', 'PUMPUSDT', 'TAKEUSDT', 'MYXUSDT', 'BRUSDT', 'BIOUSDT', 'HOLOUSDT', 'JTOUSDT', 'SPXUSDT', 'HIVEUSDT', 'BANKUSDT', 'MAVIAUSDT', 'HUSDT', 'GRASSUSDT', 'SAHARAUSDT', 'EIGENUSDT', 'HEIUSDT', 'ASTERUSDT', 'PUNDIXUSDT', 'PNUTUSDT', 'TRUMPUSDT', 'OPENUSDT', 'GUNUSDT', 'BSVUSDT', 'PHAUSDT', 'DEXEUSDT', 'ALCHUSDT', 'ARKMUSDT', 'PARTIUSDT', 'BTRUSDT', 'SCRUSDT', 'PLUMEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 23 12:27:45 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 12:34:36 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3885 (controllo 1426 · registro 1410 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 12:34:39 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1776 ms
Nov 23 12:39:20 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 12:39:20 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 13:28:09 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 13:34:59 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3886 (controllo 1426 · registro 1411 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 13:35:03 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1870 ms
Nov 23 13:41:02 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 13:41:02 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 14:28:24 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 14:35:20 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3887 (controllo 1426 · registro 1411 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 14:35:23 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2096 ms
Nov 23 14:42:16 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 14:42:16 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 15:28:29 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 15:35:44 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3890 (controllo 1426 · registro 1414 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 15:35:47 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1849 ms
Nov 23 15:43:34 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 15:43:34 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 15:48:52 Trading-Agent python[465569]: [main] market scan...
Nov 23 15:50:21 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 23 15:50:38 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 23 15:51:26 Trading-Agent python[465569]: [scanner] 9 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 23 15:51:26 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 15:51:26 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 15:51:26 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['1000PEPEUSDT', 'MYXUSDT', 'DEXEUSDT', 'AINUSDT', 'TAUSDT', 'USELESSUSDT', 'PHAUSDT', 'ZECUSDT', 'ENAUSDT', 'ALCHUSDT', 'HYPEUSDT', 'AVAAIUSDT', '0GUSDT', 'SCRUSDT', 'HUSDT', 'JUPUSDT', 'PENGUUSDT', 'GRASSUSDT', 'RAYSOLUSDT', 'HOMEUSDT', 'QUSDT', 'TRUMPUSDT', 'OPENUSDT', 'MUBARAKUSDT', 'HEIUSDT', 'TUTUSDT', 'CROSSUSDT', 'PUMPUSDT', '1000BONKUSDT', 'GALAUSDT', 'BANKUSDT', 'GUNUSDT', 'BRUSDT', 'HEMIUSDT', 'FORMUSDT', 'HOLOUSDT', 'FLOCKUSDT', 'JTOUSDT', 'PARTIUSDT', 'IDUSDT', 'UBUSDT', 'TAOUSDT', 'HUMAUSDT', 'STXUSDT', 'EIGENUSDT', 'CAKEUSDT', 'KERNELUSDT', 'PLUMEUSDT', 'BSVUSDT', 'PNUTUSDT', 'SAHARAUSDT', 'HIVEUSDT', 'BULLAUSDT', 'PUNDIXUSDT', 'IDOLUSDT', 'BIOUSDT', 'RENDERUSDT', 'AKTUSDT', 'ARKMUSDT', 'RUNEUSDT', 'VELVETUSDT', 'XMRUSDT', 'ASTERUSDT', 'ZORAUSDT', 'SPXUSDT', 'XVGUSDT', 'SYRUPUSDT', 'BTRUSDT', 'AIOUSDT', 'AGTUSDT', 'MAVIAUSDT', 'SKYAIUSDT', 'CATIUSDT', 'GPSUSDT', 'TAKEUSDT', 'BLESSUSDT', 'XPINUSDT', 'BMTUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 23 16:28:55 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 16:35:54 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3889 (controllo 1426 · registro 1412 · trade 889 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 16:35:57 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1652 ms
Nov 23 16:45:24 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 16:45:24 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 17:29:22 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 17:36:04 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3890 (controllo 1426 · registro 1413 · trade 889 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 17:36:08 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1951 ms
Nov 23 17:46:29 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 17:46:29 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 18:29:51 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 18:36:33 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3888 (controllo 1426 · registro 1412 · trade 888 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 18:36:37 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1892 ms
Nov 23 18:47:24 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 18:47:24 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 19:29:55 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 19:36:37 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3890 (controllo 1426 · registro 1415 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 19:36:40 Trading-Agent p

[... 3772 caratteri omessi (testa e coda conservate) ...]

on[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 21:49:40 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 22:31:07 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 22:37:17 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3891 (controllo 1426 · registro 1416 · trade 887 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 22:37:20 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1615 ms
Nov 23 22:50:39 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 22:50:39 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 23:31:16 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 23 23:37:35 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3894 (controllo 1426 · registro 1418 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 23 23:37:38 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1772 ms
Nov 23 23:37:38 Trading-Agent python[465569]: [learning] foto del 2026-11-24 scritta: 249 validate, 99 pesi strategia×regime
Nov 23 23:37:38 Trading-Agent python[465569]: [giorni] riga del 2026-11-23: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 23 23:49:40 Trading-Agent python[465569]: [main] market scan...
Nov 23 23:51:08 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 23 23:51:25 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 23 23:52:10 Trading-Agent python[465569]: [scanner] 9 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 23 23:52:10 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 23 23:52:10 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 23 23:52:10 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['ZECUSDT', 'QUSDT', 'XMRUSDT', 'USELESSUSDT', 'JUPUSDT', 'HUSDT', 'VELVETUSDT', 'IDOLUSDT', 'GPSUSDT', 'PUNDIXUSDT', 'SYRUPUSDT', 'JTOUSDT', 'BLESSUSDT', 'HYPEUSDT', '0GUSDT', '1000BONKUSDT', 'UBUSDT', 'ENAUSDT', 'KERNELUSDT', 'ARKMUSDT', 'RAYSOLUSDT', 'PUMPUSDT', 'SCRUSDT', 'HEIUSDT', 'HEMIUSDT', 'PLUMEUSDT', 'TRUMPUSDT', 'CROSSUSDT', 'AVAAIUSDT', 'RENDERUSDT', 'DEXEUSDT', 'BANKUSDT', 'SPXUSDT', 'ASTERUSDT', '1000PEPEUSDT', 'TAOUSDT', 'PENGUUSDT', 'HUMAUSDT', 'MYXUSDT', 'MUBARAKUSDT', 'GALAUSDT', 'XVGUSDT', 'FLOCKUSDT', 'TUTUSDT', 'HOMEUSDT', 'SAHARAUSDT', 'HOLOUSDT', 'FORMUSDT', 'EIGENUSDT', 'AKTUSDT', 'BRUSDT', 'HIVEUSDT', 'GRASSUSDT', 'ALCHUSDT', 'ZORAUSDT', 'GUNUSDT', 'STXUSDT', 'TAUSDT', 'PNUTUSDT', 'IDUSDT', 'BTRUSDT', 'RUNEUSDT', 'BIOUSDT', 'TAKEUSDT', 'CAKEUSDT', 'BSVUSDT', 'OPENUSDT', 'AINUSDT', 'AIOUSDT', 'PARTIUSDT', 'PHAUSDT', 'XPINUSDT', 'SKYAIUSDT', 'CATIUSDT', 'BMTUSDT', 'MAVIAUSDT', 'AGTUSDT', 'MITOUSDT', 'PTBUSDT', 'BULLAUSDT']
Nov 24 00:09:30 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-24: universo 100, long 30, short 29, costo 0.21, equity 10670.48
Nov 24 00:13:38 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-24: universo 100, long 30, short 25, costo 0.65, equity 10659.95
Nov 24 00:17:52 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-24: universo 100, long 30, short 29, costo 0.20, equity 10948.64
Nov 24 00:18:08 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-24: 9 ordini limite sul conto, 4 rifiutati
Nov 24 00:18:39 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 00:18:39 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 00:37:58 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3894 (controllo 1426 · registro 1421 · trade 885 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 00:38:01 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1789 ms
Nov 24 00:49:16 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 00:49:16 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 01:05:53 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-24: 59 eseguiti su 59, costo 0.21 (tutto a mercato 0.73)
Nov 24 01:09:58 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-24: 58 eseguiti su 58, costo 0.65 (tutto a mercato 2.27)
Nov 24 01:14:18 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-24: 59 eseguiti su 59, costo 0.20 (tutto a mercato 0.70)
Nov 24 01:31:51 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 01:38:25 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3894 (controllo 1426 · registro 1422 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 01:38:28 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1706 ms
Nov 24 01:50:07 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 01:50:07 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 02:32:00 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 02:38:27 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3892 (controllo 1426 · registro 1421 · trade 883 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 02:38:30 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1706 ms
Nov 24 02:51:10 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 02:51:10 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 03:32:10 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 03:38:28 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3894 (controllo 1426 · registro 1424 · trade 882 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 03:38:31 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1754 ms
Nov 24 03:50:01 Trading-Agent python[465569]: [main] market scan...
Nov 24 03:51:28 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 24 03:51:45 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 24 03:52:33 Trading-Agent python[465569]: [scanner] 9 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 24 03:52:33 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 03:52:33 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 03:52:33 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['SAHARAUSDT', 'QUSDT', 'HUSDT', 'ZECUSDT', 'JUPUSDT', 'AGTUSDT', 'ARKMUSDT', 'FORMUSDT', 'PUMPUSDT', 'HYPEUSDT', 'RENDERUSDT', 'BSVUSDT', 'USELESSUSDT', 'FLOCKUSDT', 'GUNUSDT', 'IDOLUSDT', 'TAOUSDT', 'RAYSOLUSDT', 'ASTERUSDT', 'BRUSDT', 'PARTIUSDT', 'ALCHUSDT', 'ENAUSDT', 'MUBARAKUSDT', 'TRUMPUSDT', 'VELVETUSDT', 'STXUSDT', 'SYRUPUSDT', 'PENGUUSDT', 'MYXUSDT', 'OPENUSDT', 'UBUSDT', 'TAUSDT', 'ZORAUSDT', 'GPSUSDT', 'GRASSUSDT', 'AIOUSDT', 'XMRUSDT', 'PNUTUSDT', 'AKTUSDT', 'MAVIAUSDT', 'GALAUSDT', 'XPINUSDT', 'AVAAIUSDT', 'XVGUSDT', 'CROSSUSDT', '0GUSDT', 'CAKEUSDT', 'DEXEUSDT', 'EIGENUSDT', 'IDUSDT', 'KERNELUSDT', 'HEMIUSDT', '1000PEPEUSDT', 'AINUSDT', 'BLESSUSDT', 'PHAUSDT', 'HEIUSDT', 'HOLOUSDT', 'BIOUSDT', 'PUNDIXUSDT', 'HUMAUSDT', 'PLUMEUSDT', 'TUTUSDT', 'SCRUSDT', 'JTOUSDT', 'SPXUSDT', 'HOMEUSDT', 'HIVEUSDT', 'RUNEUSDT', 'CATIUSDT', '1000BONKUSDT', 'BANKUSDT', 'SKYAIUSDT', 'BTRUSDT', 'TAKEUSDT', 'BULLAUSDT', 'MITOUSDT', 'PTBUSDT', 'BMTUSDT']
```
