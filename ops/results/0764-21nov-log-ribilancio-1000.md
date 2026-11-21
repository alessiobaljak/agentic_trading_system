# 0764-21nov-log-ribilancio-1000.req

_eseguito: 2026-11-21 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 20 12:05:41 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3812 (registro 1384 · controllo 1364 · trade 889 · rifiutati 92 · pesi 39 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 12:05:44 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1728 ms
Nov 20 12:17:57 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 12:17:57 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 12:56:15 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 13:06:04 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3812 (registro 1385 · controllo 1364 · trade 889 · rifiutati 92 · pesi 38 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 13:06:07 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1755 ms
Nov 20 13:19:12 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 13:19:12 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 13:56:22 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 14:06:26 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3810 (registro 1384 · controllo 1364 · trade 889 · rifiutati 92 · pesi 37 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 14:06:29 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1834 ms
Nov 20 14:20:03 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 14:20:03 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 14:56:31 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 15:06:51 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3810 (registro 1387 · controllo 1364 · trade 887 · rifiutati 92 · pesi 36 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 15:06:54 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1798 ms
Nov 20 15:21:25 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 15:21:25 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 15:44:39 Trading-Agent python[465569]: [main] market scan...
Nov 20 15:46:13 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 20 15:46:32 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 20 15:47:23 Trading-Agent python[465569]: [scanner] 8 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 20 15:47:23 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 15:47:23 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 15:47:23 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['ZECUSDT', 'TRUMPUSDT', 'HUSDT', 'USELESSUSDT', 'PUMPUSDT', 'SYRUPUSDT', 'EIGENUSDT', 'MYXUSDT', 'XMRUSDT', 'RENDERUSDT', 'HYPEUSDT', 'ENAUSDT', 'AVAAIUSDT', '1000PEPEUSDT', 'TAOUSDT', 'PLUMEUSDT', 'JTOUSDT', 'GUNUSDT', 'BANKUSDT', 'DEXEUSDT', 'RAYSOLUSDT', 'GALAUSDT', '1000BONKUSDT', 'HOMEUSDT', 'TUTUSDT', 'FORMUSDT', 'ARKMUSDT', 'AIOUSDT', 'MUBARAKUSDT', 'OPENUSDT', 'GRASSUSDT', 'PENGUUSDT', 'BIOUSDT', 'SAHARAUSDT', 'PHAUSDT', '0GUSDT', 'PNUTUSDT', 'HOLOUSDT', 'CAKEUSDT', 'SPXUSDT', 'HEMIUSDT', 'HEIUSDT', 'PUNDIXUSDT', 'STXUSDT', 'RUNEUSDT', 'IDOLUSDT', 'AKTUSDT', 'HIVEUSDT', 'MAVIAUSDT', 'UBUSDT', 'TAKEUSDT', 'ALCHUSDT', 'FLOCKUSDT', 'VELVETUSDT', 'XVGUSDT', 'ASTERUSDT', 'SKYAIUSDT', 'BSVUSDT', 'BRUSDT', 'HUMAUSDT', 'JUPUSDT', 'BTRUSDT', 'SCRUSDT', 'AINUSDT', 'AGTUSDT', 'QUSDT', 'BULLAUSDT', 'TAUSDT', 'CROSSUSDT', 'XPINUSDT', 'BLESSUSDT', 'IDUSDT', 'GPSUSDT', 'CATIUSDT', 'PARTIUSDT', 'ZORAUSDT', 'BMTUSDT', 'KERNELUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 20 15:56:32 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 16:07:00 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3804 (registro 1385 · controllo 1364 · trade 885 · rifiutati 91 · pesi 35 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 16:07:03 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1724 ms
Nov 20 16:07:37 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 16:07:37 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 16:56:59 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 17:07:04 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3876 (controllo 1426 · registro 1392 · trade 885 · rifiutati 91 · pesi 36 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 20 17:07:08 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1795 ms
Nov 20 17:09:23 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 17:09:23 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 17:57:27 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 18:07:31 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3874 (controllo 1426 · registro 1392 · trade 884 · rifiutati 91 · pesi 35 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 20 18:07:35 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1898 ms
Nov 20 18:10:44 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 18:10:44 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 18:57:53 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 19:07:57 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3874 (controllo 1426 · registro 1394 · trade 883 · rifiutati 91 · pesi 34 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 20 19:08:01 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2183 ms
Nov 20 19:11:42 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 19:11:42 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 19:44:40 Trading-Agent python[465569]: [main] market scan...
Nov 20 19:46:13 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 20 19:46:30 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 20 19:47:20 Trading-Agent python[465569]: [scanner] 6 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 20 19:47:20 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'USELESSUSDT', 'OPENUSDT', 'HUSDT', 'HYPEUSDT', '0GUSDT', 'CROSSUSDT', '1000BONKUSDT', 'TAKEUSDT', 'SPXUSDT', 'ZECUSDT', 'HUMAUSDT', 'GRASSUSDT', 'RAYSOLUSDT', 'GUNUSDT', 'MUBARAKUSDT', 'JTOUSDT', 'SYRUPUSDT', 'AVAAIUSDT', 'SKYAIUSDT', 'ENAUSDT', 'HIVEUSDT', 'RUNEUSDT', 'RENDERUSDT', 'ARKMUSDT', 'IDUSDT', '1000PEPEUSDT', 'TAOUSDT', 'AIOUSDT', 'PHAUSDT', 'QUSDT', 'HEIUSDT', 'AINUSDT', 'EIGENUSDT', 'MYXUSDT', 'CAKEUSDT', 'XVGUSDT', 'AGTUSDT', 'XMRUSDT', 'TAUSDT', 'FLOCKUSDT', 'STXUSDT', 'HOLOUSDT', 'SCRUSDT', 'CATIUSDT', 'BLESSUSDT', 'PUMPUSDT', 'ASTERUSDT', 'BTRUSDT', 'TUTUSDT', 'GALAUSDT', 'AKTUSDT', 'FORMUSDT', 'MAVIAUSDT', 'BRUSDT', 'BSVUSDT', 'PUNDIXUSDT', 'PNUTUSDT', 'TRUMPUSDT', 'PLUMEUSDT', 'XPINUSDT', 'JUPUSDT', 'ZORAUSDT', 'HEMIUSDT', 'SAHARAUSDT', 'PENGUUSDT', 'BULLAUSDT', 'HOMEUSDT', 'BANKUSDT', 'BIOUSDT', 'VELVETUSDT', 'UBUSDT', 'ALCHUSDT', 'KERNELUSDT', 'DEXEUSDT', 'PARTIUSDT'

[... 2857 caratteri omessi (testa e coda conservate) ...]

ent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 23:08:59 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3876 (controllo 1426 · registro 1396 · trade 886 · rifiutati 92 · pesi 30 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 20 23:09:02 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1658 ms
Nov 20 23:09:02 Trading-Agent python[465569]: [learning] foto del 2026-11-21 scritta: 249 validate, 99 pesi strategia×regime
Nov 20 23:09:02 Trading-Agent python[465569]: [giorni] riga del 2026-11-20: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 20 23:16:25 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 23:16:25 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 23:45:07 Trading-Agent python[465569]: [main] market scan...
Nov 20 23:46:36 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 20 23:46:54 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 20 23:47:41 Trading-Agent python[465569]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 20 23:47:41 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 23:47:41 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 23:47:42 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BLESSUSDT', 'UBUSDT', 'BULLAUSDT', 'TRUMPUSDT', 'MAVIAUSDT', 'AGTUSDT', 'PUMPUSDT', 'IDOLUSDT', 'HEIUSDT', 'XMRUSDT', 'PARTIUSDT', 'BSVUSDT', 'VELVETUSDT', 'USELESSUSDT', 'ARKMUSDT', 'AVAAIUSDT', 'QUSDT', 'ALCHUSDT', 'HUMAUSDT', 'TAOUSDT', 'PLUMEUSDT', 'ENAUSDT', 'PENGUUSDT', '1000PEPEUSDT', 'SPXUSDT', 'TAKEUSDT', 'MUBARAKUSDT', 'DEXEUSDT', 'HUSDT', 'ZECUSDT', 'FLOCKUSDT', 'SKYAIUSDT', 'XVGUSDT', 'BRUSDT', 'STXUSDT', 'HYPEUSDT', 'ASTERUSDT', 'JUPUSDT', 'RENDERUSDT', 'EIGENUSDT', 'GPSUSDT', 'ZORAUSDT', 'GALAUSDT', 'CROSSUSDT', 'GRASSUSDT', 'BANKUSDT', 'PNUTUSDT', 'AIOUSDT', 'BIOUSDT', '1000BONKUSDT', 'PUNDIXUSDT', 'JTOUSDT', 'SYRUPUSDT', 'CATIUSDT', 'HOMEUSDT', 'CAKEUSDT', 'HEMIUSDT', 'RAYSOLUSDT', 'GUNUSDT', 'SCRUSDT', 'AKTUSDT', 'FORMUSDT', 'AINUSDT', 'SAHARAUSDT', 'BMTUSDT', 'RUNEUSDT', 'TAUSDT', 'PHAUSDT', 'HOLOUSDT', 'HIVEUSDT', '0GUSDT', 'XPINUSDT', 'MYXUSDT', 'IDUSDT', 'OPENUSDT', 'TUTUSDT', 'BTRUSDT', 'KERNELUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 20 23:59:01 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 00:00:11 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 21 00:00:49 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 21 00:09:24 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-21: universo 100, long 26, short 30, costo 0.57, equity 10996.05
Nov 21 00:13:43 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-21: universo 100, long 30, short 27, costo 0.86, equity 11047.25
Nov 21 00:18:00 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-21: universo 100, long 26, short 30, costo 0.62, equity 11300.72
Nov 21 00:18:22 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-21: 18 ordini limite sul conto, 3 rifiutati
Nov 21 00:18:53 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 00:18:53 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 00:18:53 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3882 (controllo 1426 · registro 1400 · trade 888 · rifiutati 93 · pesi 29 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 00:18:57 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1868 ms
Nov 21 00:34:19 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 00:34:19 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 01:05:51 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-21: 57 eseguiti su 57, costo 0.57 (tutto a mercato 1.99)
Nov 21 01:09:50 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-21: 60 eseguiti su 60, costo 0.86 (tutto a mercato 3.02)
Nov 21 01:14:13 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-21: 57 eseguiti su 57, costo 0.62 (tutto a mercato 2.15)
Nov 21 01:19:17 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3879 (controllo 1426 · registro 1400 · trade 887 · rifiutati 92 · pesi 28 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 01:19:20 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1765 ms
Nov 21 01:20:02 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 01:20:02 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 01:59:38 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 02:19:35 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3877 (controllo 1426 · registro 1399 · trade 887 · rifiutati 92 · pesi 27 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 02:19:38 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1691 ms
Nov 21 02:21:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 02:21:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 02:59:42 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 21 03:19:44 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3878 (controllo 1426 · registro 1402 · trade 886 · rifiutati 92 · pesi 26 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 21 03:19:47 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1848 ms
Nov 21 03:22:25 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 03:22:25 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 03:45:17 Trading-Agent python[465569]: [main] market scan...
Nov 21 03:46:50 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 21 03:47:09 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 21 03:47:57 Trading-Agent python[465569]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 21 03:47:57 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 21 03:47:57 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 21 03:47:57 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['ZECUSDT', 'HYPEUSDT', 'BRUSDT', 'ENAUSDT', 'PUMPUSDT', '1000PEPEUSDT', 'TAOUSDT', 'GRASSUSDT', 'XMRUSDT', 'JTOUSDT', 'JUPUSDT', 'RAYSOLUSDT', 'HUMAUSDT', 'PARTIUSDT', 'AKTUSDT', 'USELESSUSDT', 'CAKEUSDT', 'XPINUSDT', 'IDUSDT', 'ZORAUSDT', 'MYXUSDT', 'RENDERUSDT', 'STXUSDT', 'SYRUPUSDT', 'OPENUSDT', 'SKYAIUSDT', 'TRUMPUSDT', '0GUSDT', 'ASTERUSDT', 'BANKUSDT', 'EIGENUSDT', 'SPXUSDT', 'GALAUSDT', 'PENGUUSDT', '1000BONKUSDT', 'PHAUSDT', 'TUTUSDT', 'FORMUSDT', 'MUBARAKUSDT', 'ARKMUSDT', 'BSVUSDT', 'GUNUSDT', 'SAHARAUSDT', 'BIOUSDT', 'HOLOUSDT', 'AIOUSDT', 'XVGUSDT', 'RUNEUSDT', 'PNUTUSDT', 'BTRUSDT', 'PLUMEUSDT', 'HIVEUSDT', 'DEXEUSDT', 'HEMIUSDT', 'AGTUSDT', 'PUNDIXUSDT', 'AINUSDT', 'FLOCKUSDT', 'SCRUSDT', 'VELVETUSDT', 'HUSDT', 'HEIUSDT', 'ALCHUSDT', 'TAKEUSDT', 'BMTUSDT', 'CROSSUSDT', 'HOMEUSDT', 'AVAAIUSDT', 'MAVIAUSDT', 'TAUSDT', 'GPSUSDT', 'UBUSDT', 'BULLAUSDT', 'CATIUSDT', 'IDOLUSDT', 'QUSDT', 'BLESSUSDT', 'KERNELUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 21 03:59:56 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
```
