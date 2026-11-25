# 0773-25nov-log-ribilancio-1000.req

_eseguito: 2026-11-25 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 24 11:52:08 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 24 11:52:26 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 24 11:53:13 Trading-Agent python[465569]: [scanner] 7 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 24 11:53:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 11:53:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 11:53:13 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['0GUSDT', 'HUSDT', 'ZECUSDT', 'PENGUUSDT', 'MUBARAKUSDT', 'AINUSDT', 'RUNEUSDT', 'TAOUSDT', 'BIOUSDT', 'SYRUPUSDT', 'PHAUSDT', 'JUPUSDT', 'XPINUSDT', 'FLOCKUSDT', 'KERNELUSDT', 'HEIUSDT', 'IDOLUSDT', 'PUMPUSDT', 'BLESSUSDT', 'UBUSDT', 'PARTIUSDT', 'EIGENUSDT', 'RAYSOLUSDT', 'AIOUSDT', 'ENAUSDT', 'GUNUSDT', 'HEMIUSDT', 'AGTUSDT', 'SKYAIUSDT', 'BRUSDT', 'AKTUSDT', 'GALAUSDT', 'TUTUSDT', 'MYXUSDT', 'XVGUSDT', 'STXUSDT', 'BANKUSDT', 'USELESSUSDT', 'ARKMUSDT', 'TAUSDT', 'TRUMPUSDT', 'HYPEUSDT', 'BMTUSDT', 'AVAAIUSDT', 'ZORAUSDT', 'OPENUSDT', '1000BONKUSDT', 'VELVETUSDT', 'MAVIAUSDT', '1000PEPEUSDT', 'SPXUSDT', 'CROSSUSDT', 'BULLAUSDT', 'PUNDIXUSDT', 'HOLOUSDT', 'DEXEUSDT', 'PLUMEUSDT', 'CAKEUSDT', 'ALCHUSDT', 'IDUSDT', 'HOMEUSDT', 'PNUTUSDT', 'CATIUSDT', 'QUSDT', 'TAKEUSDT', 'JTOUSDT', 'GRASSUSDT', 'ASTERUSDT', 'HUMAUSDT', 'BTRUSDT', 'HIVEUSDT', 'XMRUSDT', 'RENDERUSDT', 'BSVUSDT', 'SCRUSDT', 'FORMUSDT', 'GPSUSDT', 'MITOUSDT', 'PTBUSDT', 'SAHARAUSDT']
Nov 24 12:35:41 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 12:40:51 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3898 (controllo 1426 · registro 1425 · trade 885 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 12:40:54 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1615 ms
Nov 24 12:48:48 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 12:48:48 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 13:36:08 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 13:41:02 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3897 (controllo 1426 · registro 1424 · trade 885 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 13:41:06 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1863 ms
Nov 24 13:49:31 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 13:49:31 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 14:36:11 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 14:41:20 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3898 (controllo 1426 · registro 1425 · trade 885 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 14:41:24 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1817 ms
Nov 24 14:50:45 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 14:50:45 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 15:36:14 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 15:41:40 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3899 (registro 1427 · controllo 1426 · trade 884 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 15:41:45 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2902 ms
Nov 24 15:51:06 Trading-Agent python[465569]: [main] market scan...
Nov 24 15:52:32 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 24 15:52:49 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 24 15:53:36 Trading-Agent python[465569]: [scanner] 9 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 24 15:53:36 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 15:53:36 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 15:53:36 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['SYRUPUSDT', 'HYPEUSDT', 'RAYSOLUSDT', 'USELESSUSDT', '1000PEPEUSDT', 'ZECUSDT', 'CROSSUSDT', '0GUSDT', 'PUMPUSDT', 'SPXUSDT', 'JUPUSDT', 'FLOCKUSDT', 'HEIUSDT', 'PHAUSDT', 'AKTUSDT', 'JTOUSDT', 'ASTERUSDT', 'PUNDIXUSDT', 'MYXUSDT', 'HEMIUSDT', 'PENGUUSDT', 'TRUMPUSDT', 'TAOUSDT', 'XMRUSDT', 'PLUMEUSDT', 'EIGENUSDT', 'TUTUSDT', 'HUSDT', 'AINUSDT', 'XPINUSDT', 'MUBARAKUSDT', '1000BONKUSDT', 'ENAUSDT', 'PNUTUSDT', 'BANKUSDT', 'GALAUSDT', 'HUMAUSDT', 'HOLOUSDT', 'CATIUSDT', 'GUNUSDT', 'GRASSUSDT', 'HOMEUSDT', 'DEXEUSDT', 'FORMUSDT', 'OPENUSDT', 'ALCHUSDT', 'IDOLUSDT', 'BLESSUSDT', 'BTRUSDT', 'RENDERUSDT', 'TAUSDT', 'SKYAIUSDT', 'RUNEUSDT', 'STXUSDT', 'BIOUSDT', 'BMTUSDT', 'CAKEUSDT', 'XVGUSDT', 'KERNELUSDT', 'HIVEUSDT', 'AGTUSDT', 'UBUSDT', 'IDUSDT', 'MAVIAUSDT', 'ARKMUSDT', 'ZORAUSDT', 'GPSUSDT', 'SCRUSDT', 'AIOUSDT', 'BSVUSDT', 'BULLAUSDT', 'PARTIUSDT', 'QUSDT', 'AVAAIUSDT', 'BRUSDT', 'TAKEUSDT', 'VELVETUSDT', 'MITOUSDT', 'PTBUSDT', 'SAHARAUSDT']
Nov 24 16:36:24 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 16:42:05 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3898 (controllo 1426 · registro 1425 · trade 884 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 16:42:09 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2213 ms
Nov 24 16:55:44 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 16:55:44 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 17:36:44 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 17:42:24 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3899 (controllo 1426 · registro 1426 · trade 884 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 17:42:27 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1621 ms
Nov 24 17:56:50 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 17:56:50 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 18:36:54 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 18:42:34 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3899 (controllo 1426 · registro 1426 · trade 884 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 18:42:37 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1679 ms
Nov 24 18:57:38 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 18:57:38 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 19:37:19 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 19:42:59 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3898 (registro 1427 · controllo 1426 · trade 883 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 19:43:03 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1861 ms
Nov 24 19:43:36 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 19

[... 3774 caratteri omessi (testa e coda conservate) ...]

[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 22:43:29 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3896 (controllo 1426 · registro 1425 · trade 883 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 22:43:32 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1759 ms
Nov 24 22:47:20 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 22:47:20 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 23:38:04 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 24 23:43:44 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3897 (controllo 1426 · registro 1426 · trade 883 · rifiutati 93 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 24 23:43:47 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1619 ms
Nov 24 23:43:47 Trading-Agent python[465569]: [learning] foto del 2026-11-25 scritta: 249 validate, 99 pesi strategia×regime
Nov 24 23:43:47 Trading-Agent python[465569]: [giorni] riga del 2026-11-24: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 24 23:48:36 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 23:48:36 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 23:51:50 Trading-Agent python[465569]: [main] market scan...
Nov 24 23:53:15 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 24 23:53:33 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 24 23:54:19 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 24 23:54:19 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 24 23:54:19 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 24 23:54:19 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['0GUSDT', 'QUSDT', 'SYRUPUSDT', 'MUBARAKUSDT', 'IDOLUSDT', 'TAKEUSDT', 'GALAUSDT', 'SCRUSDT', 'AKTUSDT', 'AGTUSDT', 'XMRUSDT', 'ASTERUSDT', 'PENGUUSDT', 'HUMAUSDT', 'ZECUSDT', '1000PEPEUSDT', 'SKYAIUSDT', 'BLESSUSDT', 'ALCHUSDT', 'HIVEUSDT', 'KERNELUSDT', 'HOLOUSDT', 'USELESSUSDT', 'ARKMUSDT', 'PUNDIXUSDT', 'BSVUSDT', 'HYPEUSDT', 'HEIUSDT', 'PLUMEUSDT', 'PUMPUSDT', 'HOMEUSDT', 'PHAUSDT', 'IDUSDT', 'FLOCKUSDT', 'AIOUSDT', 'AVAAIUSDT', 'CROSSUSDT', 'PNUTUSDT', 'RAYSOLUSDT', 'VELVETUSDT', 'HEMIUSDT', 'TAUSDT', 'UBUSDT', 'MYXUSDT', 'XVGUSDT', 'GRASSUSDT', 'PARTIUSDT', 'BIOUSDT', 'STXUSDT', '1000BONKUSDT', 'GPSUSDT', 'BRUSDT', 'BANKUSDT', 'ENAUSDT', 'JTOUSDT', 'JUPUSDT', 'TRUMPUSDT', 'TAOUSDT', 'EIGENUSDT', 'CAKEUSDT', 'TUTUSDT', 'HUSDT', 'GUNUSDT', 'BMTUSDT', 'CATIUSDT', 'ZORAUSDT', 'DEXEUSDT', 'BTRUSDT', 'MAVIAUSDT', 'BULLAUSDT', 'RENDERUSDT', 'OPENUSDT', 'FORMUSDT', 'AINUSDT', 'SPXUSDT', 'XPINUSDT', 'RUNEUSDT', 'SAHARAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 25 00:09:27 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-25: universo 100, long 30, short 29, costo 0.34, equity 10661.46
Nov 25 00:13:39 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-25: universo 100, long 29, short 24, costo 1.03, equity 10682.35
Nov 25 00:18:00 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-25: universo 100, long 30, short 29, costo 0.40, equity 10984.10
Nov 25 00:18:11 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-25: 4 ordini limite sul conto, 4 rifiutati
Nov 25 00:19:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 00:19:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 00:43:52 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3897 (controllo 1426 · registro 1423 · trade 885 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 00:43:55 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1419 ms
Nov 25 00:49:45 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 00:49:45 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 01:05:58 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-25: 60 eseguiti su 60, costo 0.34 (tutto a mercato 1.19)
Nov 25 01:09:54 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-25: 57 eseguiti su 57, costo 1.03 (tutto a mercato 3.61)
Nov 25 01:14:15 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-25: 60 eseguiti su 60, costo 0.40 (tutto a mercato 1.40)
Nov 25 01:38:27 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 01:44:07 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3899 (controllo 1426 · registro 1424 · trade 886 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 01:44:11 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2054 ms
Nov 25 01:51:03 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 01:51:03 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 02:38:55 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 02:44:35 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3900 (controllo 1426 · registro 1424 · trade 887 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 02:44:38 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1714 ms
Nov 25 02:51:46 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 02:51:46 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 03:38:57 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 25 03:44:52 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3903 (controllo 1426 · registro 1426 · trade 888 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 25 03:44:55 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1620 ms
Nov 25 03:51:56 Trading-Agent python[465569]: [main] market scan...
Nov 25 03:53:25 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 25 03:53:45 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 25 03:54:30 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 25 03:54:30 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 25 03:54:30 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 25 03:54:31 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['SKYAIUSDT', 'BULLAUSDT', 'ALCHUSDT', 'MUBARAKUSDT', 'RENDERUSDT', 'XMRUSDT', 'BRUSDT', 'FORMUSDT', 'KERNELUSDT', 'TAOUSDT', 'JUPUSDT', 'BLESSUSDT', 'IDOLUSDT', 'AVAAIUSDT', 'CAKEUSDT', 'HYPEUSDT', 'MAVIAUSDT', 'TRUMPUSDT', 'VELVETUSDT', 'UBUSDT', 'USELESSUSDT', 'BIOUSDT', 'ASTERUSDT', 'ENAUSDT', 'AINUSDT', 'GRASSUSDT', 'HUSDT', 'HUMAUSDT', 'CROSSUSDT', 'PNUTUSDT', 'CATIUSDT', 'ZORAUSDT', 'ARKMUSDT', 'PUMPUSDT', 'MYXUSDT', '0GUSDT', 'SAHARAUSDT', 'HOMEUSDT', '1000PEPEUSDT', '1000BONKUSDT', 'AGTUSDT', 'BANKUSDT', 'PHAUSDT', 'PENGUUSDT', 'RAYSOLUSDT', 'PARTIUSDT', 'ZECUSDT', 'QUSDT', 'AKTUSDT', 'HOLOUSDT', 'XVGUSDT', 'GPSUSDT', 'TAUSDT', 'AIOUSDT', 'SYRUPUSDT', 'PLUMEUSDT', 'TUTUSDT', 'STXUSDT', 'GALAUSDT', 'OPENUSDT', 'BTRUSDT', 'XPINUSDT', 'DEXEUSDT', 'JTOUSDT', 'RUNEUSDT', 'HEIUSDT', 'EIGENUSDT', 'IDUSDT', 'HEMIUSDT', 'HIVEUSDT', 'BSVUSDT', 'GUNUSDT', 'PUNDIXUSDT', 'FLOCKUSDT', 'SPXUSDT', 'SCRUSDT', 'BMTUSDT', 'TAKEUSDT', 'MITOUSDT', 'PTBUSDT']
```
