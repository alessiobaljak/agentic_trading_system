# 0775-26nov-log-ribilancio-1000.req

_eseguito: 2026-11-26 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 25 11:54:44 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 11:54:44 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 11:54:45 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['SYRUPUSDT', 'VELVETUSDT', 'AIOUSDT', 'TAOUSDT', '0GUSDT', 'HOLOUSDT', 'DEXEUSDT', 'HEMIUSDT', 'SPXUSDT', 'GALAUSDT', 'STXUSDT', 'EIGENUSDT', 'PENGUUSDT', 'ARKMUSDT', 'ZORAUSDT', 'JTOUSDT', 'ALCHUSDT', 'ENAUSDT', 'TRUMPUSDT', 'GUNUSDT', 'SKYAIUSDT', 'OPENUSDT', 'RUNEUSDT', 'PARTIUSDT', '1000PEPEUSDT', 'USELESSUSDT', 'MAVIAUSDT', 'FLOCKUSDT', 'RENDERUSDT', '1000BONKUSDT', 'BLESSUSDT', 'PHAUSDT', 'PLUMEUSDT', 'KERNELUSDT', 'BIOUSDT', 'CROSSUSDT', 'PUMPUSDT', 'TAKEUSDT', 'MYXUSDT', 'FORMUSDT', 'BANKUSDT', 'CATIUSDT', 'HEIUSDT', 'AVAAIUSDT', 'IDOLUSDT', 'GPSUSDT', 'ZECUSDT', 'HYPEUSDT', 'SCRUSDT', 'HUMAUSDT', 'PUNDIXUSDT', 'CAKEUSDT', 'BMTUSDT', 'SAHARAUSDT', 'MUBARAKUSDT', 'BSVUSDT', 'AKTUSDT', 'AGTUSDT', 'IDUSDT', 'TUTUSDT', 'PNUTUSDT', 'ASTERUSDT', 'HUSDT', 'BTRUSDT', 'QUSDT', 'GRASSUSDT', 'XPINUSDT', 'JUPUSDT', 'RAYSOLUSDT', 'TAUSDT', 'HOMEUSDT', 'UBUSDT', 'XMRUSDT', 'AINUSDT', 'XVGUSDT', 'BRUSDT', 'BULLAUSDT', 'HIVEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 25 12:42:02 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 12:47:51 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3902 (controllo 1426 · registro 1426 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 12:47:54 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1763 ms
Nov 25 12:50:01 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 12:50:01 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 13:42:13 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 13:48:02 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3901 (controllo 1426 · registro 1426 · trade 886 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 13:48:05 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1942 ms
Nov 25 13:51:14 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 13:51:14 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 14:42:43 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 14:48:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3900 (controllo 1426 · registro 1426 · trade 885 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 14:48:12 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1644 ms
Nov 25 14:52:31 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 14:52:31 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 15:25:13 Trading-Agent python[465569]: [demo_binance] ora di Binance riletta: scarto -129 ms
Nov 25 15:42:58 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 15:48:38 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3904 (registro 1430 · controllo 1426 · trade 885 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 15:48:41 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1885 ms
Nov 25 15:52:28 Trading-Agent python[465569]: [main] market scan...
Nov 25 15:53:58 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 25 15:54:16 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 25 15:55:04 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 25 15:55:04 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 15:55:04 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 15:55:06 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['ZECUSDT', 'USELESSUSDT', '1000PEPEUSDT', 'RENDERUSDT', 'STXUSDT', 'HEIUSDT', 'AVAAIUSDT', 'HYPEUSDT', 'GUNUSDT', 'AGTUSDT', 'TRUMPUSDT', 'CATIUSDT', 'ENAUSDT', '1000BONKUSDT', 'JTOUSDT', 'SPXUSDT', '0GUSDT', 'AINUSDT', 'DEXEUSDT', 'MAVIAUSDT', 'HUMAUSDT', 'PUMPUSDT', 'PARTIUSDT', 'PHAUSDT', 'BRUSDT', 'SCRUSDT', 'TAOUSDT', 'JUPUSDT', 'CAKEUSDT', 'PENGUUSDT', 'XMRUSDT', 'PLUMEUSDT', 'MYXUSDT', 'OPENUSDT', 'ALCHUSDT', 'SYRUPUSDT', 'GRASSUSDT', 'HOMEUSDT', 'QUSDT', 'MUBARAKUSDT', 'HEMIUSDT', 'BIOUSDT', 'ARKMUSDT', 'GALAUSDT', 'HOLOUSDT', 'HUSDT', 'AKTUSDT', 'GPSUSDT', 'EIGENUSDT', 'UBUSDT', 'RAYSOLUSDT', 'PNUTUSDT', 'SKYAIUSDT', 'ASTERUSDT', 'BSVUSDT', 'IDUSDT', 'BANKUSDT', 'FLOCKUSDT', 'TUTUSDT', 'BTRUSDT', 'HIVEUSDT', 'ZORAUSDT', 'PUNDIXUSDT', 'BULLAUSDT', 'RUNEUSDT', 'TAKEUSDT', 'FORMUSDT', 'XVGUSDT', 'IDOLUSDT', 'CROSSUSDT', 'AIOUSDT', 'TAUSDT', 'BMTUSDT', 'BLESSUSDT', 'XPINUSDT', 'VELVETUSDT', 'KERNELUSDT', 'SAHARAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 25 16:14:11 Trading-Agent python[465569]: [demo_binance] ora di Binance riletta: scarto -1132 ms
Nov 25 16:43:21 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 16:48:46 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3903 (registro 1428 · controllo 1426 · trade 886 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 16:48:50 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1957 ms
Nov 25 16:57:08 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 16:57:08 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 17:36:20 Trading-Agent python[465569]: [demo_binance] ora di Binance riletta: scarto -172 ms
Nov 25 17:36:37 Trading-Agent python[465569]: [demo_binance] errore nelle protezioni, si riprova fra un minuto: HTTPSConnectionPool(host='demo-fapi.binance.com', port=443): Read timed out. (read timeout=15)
Nov 25 17:43:50 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 17:49:00 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3902 (controllo 1426 · registro 1426 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 17:49:03 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1856 ms
Nov 25 17:58:08 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 17:58:08 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 18:44:11 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT', 'PIEVERSEUSDT']
Nov 25 18:49:20 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3904 (registro 1427 · controllo 1426 · trade 888 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 18:49:23 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1615 ms
Nov 25 18:58:30 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 18:58:30 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 19:44:23 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT', 'PIEVERSEUSDT']
Nov 25 19:49:48 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3907 (registro 1429 · controllo 1426 · trade 889 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 19:49:51 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1674 ms
Nov 25 19:52:29 Trading-Agent python[465569]: [main] market scan...
Nov 25 19:53:55 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 25 19:54:12 T

[... 3585 caratteri omessi (testa e coda conservate) ...]

tture ultime 24 h: 3910 (registro 1429 · controllo 1426 · trade 891 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 22:50:22 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1779 ms
Nov 25 23:04:28 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 23:04:28 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 23:45:12 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT', 'PIEVERSEUSDT']
Nov 25 23:50:29 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3912 (registro 1432 · controllo 1426 · trade 890 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 23:50:31 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1551 ms
Nov 25 23:50:32 Trading-Agent python[465569]: [learning] foto del 2026-11-26 scritta: 249 validate, 99 pesi strategia×regime
Nov 25 23:50:32 Trading-Agent python[465569]: [giorni] riga del 2026-11-25: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 25 23:52:54 Trading-Agent python[465569]: [main] market scan...
Nov 25 23:54:19 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 25 23:54:38 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 25 23:55:24 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 25 23:55:24 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['HUMAUSDT', 'USELESSUSDT', 'TRUMPUSDT', 'TUTUSDT', 'CATIUSDT', 'HOMEUSDT', 'HEMIUSDT', 'OPENUSDT', 'AINUSDT', 'PUMPUSDT', 'BMTUSDT', 'GPSUSDT', 'ENAUSDT', 'TAKEUSDT', 'RAYSOLUSDT', 'ZECUSDT', 'FLOCKUSDT', 'RUNEUSDT', 'IDOLUSDT', '0GUSDT', 'STXUSDT', 'SKYAIUSDT', 'XMRUSDT', 'HYPEUSDT', 'QUSDT', 'RENDERUSDT', 'PENGUUSDT', 'MAVIAUSDT', 'HUSDT', 'TAOUSDT', 'GUNUSDT', '1000PEPEUSDT', 'BLESSUSDT', 'PLUMEUSDT', 'ZORAUSDT', 'IDUSDT', 'PUNDIXUSDT', 'SPXUSDT', 'BULLAUSDT', 'PHAUSDT', 'KERNELUSDT', 'MYXUSDT', 'AIOUSDT', 'SYRUPUSDT', 'CAKEUSDT', 'PNUTUSDT', 'AKTUSDT', 'FORMUSDT', '1000BONKUSDT', 'UBUSDT', 'HEIUSDT', 'AVAAIUSDT', 'VELVETUSDT', 'ASTERUSDT', 'XVGUSDT', 'ARKMUSDT', 'SCRUSDT', 'BIOUSDT', 'JUPUSDT', 'GRASSUSDT', 'DEXEUSDT', 'HOLOUSDT', 'HIVEUSDT', 'BSVUSDT', 'AGTUSDT', 'BRUSDT', 'ALCHUSDT', 'CROSSUSDT', 'JTOUSDT', 'GALAUSDT', 'SAHARAUSDT', 'PARTIUSDT', 'MUBARAKUSDT', 'BANKUSDT', 'BTRUSDT', 'EIGENUSDT', 'XPINUSDT', 'TAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 26 00:09:38 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-26: universo 100, long 29, short 29, costo 0.31, equity 10426.75
Nov 26 00:13:49 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-26: universo 100, long 29, short 24, costo 0.77, equity 10407.72
Nov 26 00:18:40 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-26: universo 100, long 29, short 29, costo 0.36, equity 10745.94
Nov 26 00:18:52 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-26: 6 ordini limite sul conto, 4 rifiutati
Nov 26 00:19:23 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 00:19:23 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 00:50:32 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3906 (registro 1429 · controllo 1426 · trade 888 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 00:50:35 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1673 ms
Nov 26 01:05:10 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 01:05:10 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 01:06:06 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-26: 59 eseguiti su 59, costo 0.31 (tutto a mercato 1.09)
Nov 26 01:10:04 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-26: 55 eseguiti su 55, costo 0.77 (tutto a mercato 2.69)
Nov 26 01:14:34 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-26: 59 eseguiti su 59, costo 0.36 (tutto a mercato 1.26)
Nov 26 01:24:32 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 26 01:25:12 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 26 01:25:50 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 26 01:45:25 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 01:50:34 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3904 (registro 1428 · controllo 1426 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 01:50:37 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1459 ms
Nov 26 02:05:42 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 02:05:42 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 02:45:56 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 02:50:42 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3901 (registro 1428 · controllo 1426 · trade 885 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 02:50:45 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1636 ms
Nov 26 02:51:19 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 02:51:19 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 03:46:11 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 26 03:50:48 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3904 (registro 1432 · controllo 1426 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 26 03:50:51 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1586 ms
Nov 26 03:52:27 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 03:52:27 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 26 03:52:58 Trading-Agent python[465569]: [main] market scan...
Nov 26 03:54:27 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 26 03:54:44 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 26 03:55:30 Trading-Agent python[465569]: [scanner] 9 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 26 03:55:30 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['TAUSDT', 'SKYAIUSDT', 'BRUSDT', 'RAYSOLUSDT', '0GUSDT', 'PARTIUSDT', 'AVAAIUSDT', 'JTOUSDT', 'SYRUPUSDT', 'JUPUSDT', 'IDOLUSDT', 'PHAUSDT', 'ENAUSDT', 'MUBARAKUSDT', 'PUMPUSDT', '1000PEPEUSDT', 'USELESSUSDT', 'ZECUSDT', 'AGTUSDT', 'ASTERUSDT', 'BLESSUSDT', 'FORMUSDT', 'BULLAUSDT', 'AINUSDT', 'TAKEUSDT', 'TRUMPUSDT', 'ARKMUSDT', 'PENGUUSDT', '1000BONKUSDT', 'HEMIUSDT', 'IDUSDT', 'PUNDIXUSDT', 'BIOUSDT', 'RUNEUSDT', 'HUMAUSDT', 'KERNELUSDT', 'RENDERUSDT', 'PNUTUSDT', 'CROSSUSDT', 'ZORAUSDT', 'AKTUSDT', 'TAOUSDT', 'SPXUSDT', 'VELVETUSDT', 'CATIUSDT', 'HUSDT', 'HYPEUSDT', 'MYXUSDT', 'GPSUSDT', 'UBUSDT', 'EIGENUSDT', 'XPINUSDT', 'AIOUSDT', 'SCRUSDT', 'DEXEUSDT', 'SAHARAUSDT', 'BMTUSDT', 'FLOCKUSDT', 'XMRUSDT', 'HEIUSDT', 'PLUMEUSDT', 'BSVUSDT', 'GALAUSDT', 'GUNUSDT', 'CAKEUSDT', 'GRASSUSDT', 'HOLOUSDT', 'QUSDT', 'OPENUSDT', 'ALCHUSDT', 'XVGUSDT', 'HOMEUSDT', 'MAVIAUSDT', 'BTRUSDT', 'TUTUSDT', 'STXUSDT', 'BANKUSDT', 'HIVEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 26 04:07:36 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 26 04:07:36 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
