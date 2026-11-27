# 0777-27nov-log-ribilancio-1000.req

_eseguito: 2026-11-27 04:18 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 26 11:55:40 Trading-Agent python[465569]: [scanner] 10 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 26 11:55:40 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['SKYAIUSDT', 'XMRUSDT', 'IDOLUSDT', 'AINUSDT', 'AVAAIUSDT', 'ZECUSDT', 'GALAUSDT', 'QUSDT', 'AIOUSDT', 'JUPUSDT', 'UBUSDT', 'PENGUUSDT', 'BULLAUSDT', 'AKTUSDT', 'TUTUSDT', 'FORMUSDT', 'TAUSDT', 'HYPEUSDT', 'BRUSDT', '0GUSDT', 'TRUMPUSDT', 'CROSSUSDT', 'DEXEUSDT', 'OPENUSDT', 'AGTUSDT', 'HUMAUSDT', 'ASTERUSDT', 'RENDERUSDT', '1000PEPEUSDT', 'FLOCKUSDT', 'BIOUSDT', 'EIGENUSDT', 'HEMIUSDT', 'VELVETUSDT', 'BLESSUSDT', '1000BONKUSDT', 'MUBARAKUSDT', 'CAKEUSDT', 'PHAUSDT', 'IDUSDT', 'XVGUSDT', 'SYRUPUSDT', 'GPSUSDT', 'HOLOUSDT', 'PUMPUSDT', 'ENAUSDT', 'TAKEUSDT', 'PARTIUSDT', 'MYXUSDT', 'BMTUSDT', 'RAYSOLUSDT', 'PLUMEUSDT', 'MAVIAUSDT', 'XPINUSDT', 'PUNDIXUSDT', 'ALCHUSDT', 'USELESSUSDT', 'TAOUSDT', 'GRASSUSDT', 'HUSDT', 'SPXUSDT', 'PNUTUSDT', 'STXUSDT', 'KERNELUSDT', 'ZORAUSDT', 'SCRUSDT', 'GUNUSDT', 'HIVEUSDT', 'SAHARAUSDT', 'HOMEUSDT', 'CATIUSDT', 'JTOUSDT', 'ARKMUSDT', 'HEIUSDT', 'BSVUSDT', 'BANKUSDT', 'BTRUSDT', 'RUNEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 26 12:00:49 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 12:00:49 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 12:48:25 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 12:52:41 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3905 (registro 1429 · controllo 1426 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 12:52:45 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2205 ms
Nov 26 13:02:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 13:02:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 13:48:28 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 13:52:44 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3906 (registro 1429 · controllo 1426 · trade 888 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 13:52:48 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1815 ms
Nov 26 14:03:33 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 14:03:33 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 14:48:54 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 14:53:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3906 (registro 1429 · controllo 1426 · trade 888 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 14:53:13 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1996 ms
Nov 26 15:04:38 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 15:04:38 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 15:49:23 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 15:53:16 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3907 (registro 1431 · controllo 1426 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 15:53:19 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1622 ms
Nov 26 15:53:22 Trading-Agent python[465569]: [main] market scan...
Nov 26 15:54:53 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 26 15:55:11 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 26 15:56:00 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 26 15:56:00 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['XMRUSDT', 'AGTUSDT', 'ZECUSDT', 'HUMAUSDT', 'ENAUSDT', 'RAYSOLUSDT', 'AKTUSDT', '0GUSDT', 'HOLOUSDT', 'CROSSUSDT', 'BRUSDT', 'BTRUSDT', '1000PEPEUSDT', 'SYRUPUSDT', 'MUBARAKUSDT', 'QUSDT', 'GPSUSDT', 'PUMPUSDT', 'HYPEUSDT', 'ASTERUSDT', 'RENDERUSDT', 'TAKEUSDT', 'RUNEUSDT', 'TAOUSDT', 'BLESSUSDT', 'HOMEUSDT', 'TRUMPUSDT', 'KERNELUSDT', 'JUPUSDT', 'BSVUSDT', 'IDOLUSDT', 'HEIUSDT', 'BIOUSDT', 'CAKEUSDT', 'PUNDIXUSDT', 'UBUSDT', 'PHAUSDT', 'VELVETUSDT', 'MYXUSDT', 'PENGUUSDT', 'HEMIUSDT', 'SAHARAUSDT', 'DEXEUSDT', 'AVAAIUSDT', 'OPENUSDT', 'AIOUSDT', 'PLUMEUSDT', 'ARKMUSDT', 'PARTIUSDT', '1000BONKUSDT', 'ALCHUSDT', 'XVGUSDT', 'SKYAIUSDT', 'GUNUSDT', 'XPINUSDT', 'MAVIAUSDT', 'USELESSUSDT', 'TAUSDT', 'SCRUSDT', 'TUTUSDT', 'AINUSDT', 'SPXUSDT', 'HUSDT', 'FLOCKUSDT', 'STXUSDT', 'EIGENUSDT', 'PNUTUSDT', 'ZORAUSDT', 'GALAUSDT', 'JTOUSDT', 'CATIUSDT', 'HIVEUSDT', 'BANKUSDT', 'GRASSUSDT', 'IDUSDT', 'FORMUSDT', 'BMTUSDT', 'MITOUSDT', 'PTBUSDT', 'BULLAUSDT']
Nov 26 16:06:28 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 16:06:28 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 16:49:37 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 16:53:44 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3904 (registro 1429 · controllo 1426 · trade 886 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 16:53:47 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1782 ms
Nov 26 17:07:40 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 17:07:40 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 17:50:05 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 17:54:13 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3905 (registro 1431 · controllo 1426 · trade 885 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 17:54:16 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2074 ms
Nov 26 18:08:25 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 18:08:25 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 18:50:32 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 18:54:48 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3906 (registro 1433 · controllo 1426 · trade 884 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 18:54:52 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1777 ms
Nov 26 19:09:22 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 19:09:22 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 19:50:54 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 19:53:28 Trading-Agent python[465569]: [main] market scan...
Nov 26 19:55:00 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 26 19:55:17 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 26 19:56:04 Trading-Agent python[465569]: [scanner] 14 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 26 19:56:04 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 19:56:04 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 19:56:05 Tra

[... 3752 caratteri omessi (testa e coda conservate) ...]

o, paper giallo, 3 anomalie, 1447 ms
Nov 26 23:00:25 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 23:00:25 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 23:51:56 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 23:53:29 Trading-Agent python[465569]: [main] market scan...
Nov 26 23:54:58 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 26 23:55:16 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 26 23:56:02 Trading-Agent python[465569]: [scanner] 14 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 26 23:56:02 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 23:56:02 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 23:56:03 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['ZECUSDT', 'PLUMEUSDT', 'MUBARAKUSDT', '1000BONKUSDT', 'TAUSDT', 'GUNUSDT', '1000PEPEUSDT', 'BRUSDT', 'CAKEUSDT', 'SPXUSDT', 'RUNEUSDT', 'DEXEUSDT', 'PHAUSDT', 'TRUMPUSDT', 'VELVETUSDT', 'TAOUSDT', 'PENGUUSDT', 'ZORAUSDT', 'RAYSOLUSDT', 'HUMAUSDT', 'ENAUSDT', 'HEMIUSDT', 'SYRUPUSDT', 'PNUTUSDT', 'AIOUSDT', 'BLESSUSDT', 'XMRUSDT', 'HOLOUSDT', 'PUMPUSDT', 'BTRUSDT', 'HOMEUSDT', 'JTOUSDT', 'QUSDT', 'IDOLUSDT', 'JUPUSDT', 'GRASSUSDT', 'MYXUSDT', 'USELESSUSDT', 'HYPEUSDT', 'ARKMUSDT', 'SCRUSDT', 'FLOCKUSDT', 'BIOUSDT', 'CATIUSDT', 'BANKUSDT', 'XVGUSDT', 'SAHARAUSDT', 'ASTERUSDT', 'SKYAIUSDT', 'PUNDIXUSDT', 'HUSDT', 'AGTUSDT', 'TUTUSDT', 'GALAUSDT', 'KERNELUSDT', 'TAKEUSDT', 'MAVIAUSDT', 'AKTUSDT', 'HEIUSDT', 'AINUSDT', 'AVAAIUSDT', 'BULLAUSDT', 'STXUSDT', 'IDUSDT', 'FORMUSDT', 'EIGENUSDT', 'PARTIUSDT', 'HIVEUSDT', 'GPSUSDT', 'CROSSUSDT', 'XPINUSDT', '0GUSDT', 'OPENUSDT', 'ALCHUSDT', 'BSVUSDT', 'UBUSDT', 'BMTUSDT', 'RENDERUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 26 23:57:36 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3909 (registro 1436 · controllo 1426 · trade 884 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 23:57:39 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1867 ms
Nov 26 23:57:39 Trading-Agent python[465569]: [learning] foto del 2026-11-27 scritta: 249 validate, 99 pesi strategia×regime
Nov 26 23:57:40 Trading-Agent python[465569]: [giorni] riga del 2026-11-26: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 27 00:01:18 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 00:01:18 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 00:09:46 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-27: universo 100, long 29, short 29, costo 0.28, equity 10732.32
Nov 27 00:13:57 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-27: universo 100, long 31, short 22, costo 1.12, equity 10714.39
Nov 27 00:18:16 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-27: universo 100, long 29, short 29, costo 0.30, equity 11023.95
Nov 27 00:18:32 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-27: 10 ordini limite sul conto, 4 rifiutati
Nov 27 00:19:03 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 00:19:03 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 00:57:48 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3910 (registro 1435 · controllo 1426 · trade 885 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 00:57:51 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1475 ms
Nov 27 01:04:20 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 01:04:20 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 01:06:14 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-27: 58 eseguiti su 58, costo 0.28 (tutto a mercato 1.00)
Nov 27 01:10:19 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-27: 57 eseguiti su 57, costo 1.12 (tutto a mercato 3.93)
Nov 27 01:14:49 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-27: 58 eseguiti su 58, costo 0.30 (tutto a mercato 1.04)
Nov 27 01:52:08 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 01:57:55 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3912 (registro 1436 · controllo 1426 · trade 886 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 01:57:58 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1771 ms
Nov 27 02:05:38 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 02:05:38 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 02:52:13 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 02:58:01 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3913 (registro 1436 · controllo 1426 · trade 887 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 02:58:04 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1823 ms
Nov 27 03:07:21 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 03:07:21 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 03:52:40 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 03:53:41 Trading-Agent python[465569]: [main] market scan...
Nov 27 03:55:10 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 27 03:55:27 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 27 03:56:13 Trading-Agent python[465569]: [scanner] 16 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 27 03:56:14 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['HYPEUSDT', 'USELESSUSDT', 'XPINUSDT', 'ZECUSDT', 'SKYAIUSDT', 'ENAUSDT', 'AIOUSDT', 'JUPUSDT', '1000PEPEUSDT', 'HUMAUSDT', 'PUMPUSDT', 'MUBARAKUSDT', 'SCRUSDT', 'FORMUSDT', 'HUSDT', 'XMRUSDT', 'CROSSUSDT', 'EIGENUSDT', 'AVAAIUSDT', 'MYXUSDT', 'RENDERUSDT', 'GPSUSDT', 'VELVETUSDT', 'BLESSUSDT', 'ALCHUSDT', 'TUTUSDT', 'HOMEUSDT', 'BULLAUSDT', 'CATIUSDT', 'ASTERUSDT', 'SPXUSDT', 'HEMIUSDT', 'GRASSUSDT', 'STXUSDT', 'TAOUSDT', 'SYRUPUSDT', 'FLOCKUSDT', 'RAYSOLUSDT', 'RUNEUSDT', 'GUNUSDT', 'TAKEUSDT', 'XVGUSDT', 'IDOLUSDT', 'PENGUUSDT', '1000BONKUSDT', 'UBUSDT', 'HOLOUSDT', 'IDUSDT', 'CAKEUSDT', 'HEIUSDT', 'BIOUSDT', 'PLUMEUSDT', 'ARKMUSDT', 'JTOUSDT', 'GALAUSDT', 'BANKUSDT', '0GUSDT', 'PARTIUSDT', 'HIVEUSDT', 'OPENUSDT', 'PNUTUSDT', 'DEXEUSDT', 'BRUSDT', 'MAVIAUSDT', 'AINUSDT', 'TRUMPUSDT', 'AKTUSDT', 'BSVUSDT', 'PHAUSDT', 'BMTUSDT', 'SAHARAUSDT', 'BTRUSDT', 'ZORAUSDT', 'AGTUSDT', 'QUSDT', 'TAUSDT', 'PUNDIXUSDT', 'KERNELUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 27 03:58:26 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3915 (registro 1437 · controllo 1426 · trade 888 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 03:58:26 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 03:58:26 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 03:58:29 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1630 ms
Nov 27 04:08:26 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 04:08:26 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
