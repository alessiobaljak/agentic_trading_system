# 0758-18nov-log-ribilancio-1000.req

_eseguito: 2026-11-18 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 17 16:46:46 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 2120 ms
Nov 17 16:57:24 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 16:57:24 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 17:34:20 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 17:46:51 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3972 (registro 1427 · controllo 1426 · trade 887 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 17:46:51 Trading-Agent python[465569]: [learning] filtrati 20/71 trade (esplorativi: 7 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 8)
Nov 17 17:46:52 Trading-Agent python[465569]: [main] pesi ricalcolati: 48 coppie strat×regime da 71 trade (30g)
Nov 17 17:46:55 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1805 ms
Nov 17 17:59:06 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 17:59:06 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 18:34:36 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 18:47:14 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3973 (registro 1429 · controllo 1426 · trade 886 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 18:47:14 Trading-Agent python[465569]: [learning] filtrati 20/71 trade (esplorativi: 7 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 8)
Nov 17 18:47:14 Trading-Agent python[465569]: [main] pesi ricalcolati: 48 coppie strat×regime da 71 trade (30g)
Nov 17 18:47:18 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1969 ms
Nov 17 19:01:10 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 19:01:10 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 19:35:07 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 19:38:42 Trading-Agent python[465569]: [main] market scan...
Nov 17 19:40:10 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 17 19:40:27 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 17 19:41:13 Trading-Agent python[465569]: [scanner] 10 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 17 19:41:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 19:41:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 19:41:13 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['PENGUUSDT', 'AINUSDT', 'HUMAUSDT', 'IDOLUSDT', 'TAUSDT', 'BULLAUSDT', 'RUNEUSDT', 'USELESSUSDT', 'PUMPUSDT', 'HUSDT', 'PARTIUSDT', 'ZECUSDT', 'PHAUSDT', 'ENAUSDT', 'GALAUSDT', '1000PEPEUSDT', 'HYPEUSDT', 'VELVETUSDT', 'UBUSDT', 'XPINUSDT', 'TAOUSDT', 'XMRUSDT', 'KERNELUSDT', 'JUPUSDT', 'TRUMPUSDT', 'HIVEUSDT', 'HEMIUSDT', 'BTRUSDT', '1000BONKUSDT', 'ALCHUSDT', 'MAVIAUSDT', 'AVAAIUSDT', 'ASTERUSDT', 'PLUMEUSDT', 'HOLOUSDT', 'FORMUSDT', 'CROSSUSDT', 'MYXUSDT', 'CATIUSDT', 'SCRUSDT', 'MUBARAKUSDT', 'BIOUSDT', 'XVGUSDT', 'EIGENUSDT', 'HOMEUSDT', 'ARKMUSDT', 'BANKUSDT', 'AIOUSDT', 'SPXUSDT', 'BMTUSDT', 'GUNUSDT', 'TUTUSDT', 'BSVUSDT', 'BLESSUSDT', 'RAYSOLUSDT', 'IDUSDT', 'SYRUPUSDT', 'TAKEUSDT', 'PNUTUSDT', '0GUSDT', 'RENDERUSDT', 'AGTUSDT', 'AKTUSDT', 'HEIUSDT', 'QUSDT', 'SAHARAUSDT', 'PUNDIXUSDT', 'SKYAIUSDT', 'JTOUSDT', 'STXUSDT', 'BRUSDT', 'GRASSUSDT', 'GPSUSDT', 'FLOCKUSDT', 'DEXEUSDT', 'CAKEUSDT', 'ZORAUSDT', 'OPENUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 17 19:47:33 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3974 (registro 1429 · controllo 1426 · trade 887 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 19:47:33 Trading-Agent python[465569]: [learning] filtrati 18/65 trade (esplorativi: 6 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 7)
Nov 17 19:47:33 Trading-Agent python[465569]: [learning] solo 47 trade validi (servono 50): pesi INVARIATI
Nov 17 19:47:33 Trading-Agent python[465569]: [main] pesi ricalcolati: 44 coppie strat×regime da 65 trade (30g)
Nov 17 19:47:37 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1941 ms
Nov 17 20:02:21 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 20:02:21 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 20:35:21 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 20:47:51 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3972 (registro 1428 · controllo 1426 · trade 887 · rifiutati 94 · pesi 68 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 20:47:51 Trading-Agent python[465569]: [learning] filtrati 16/61 trade (esplorativi: 6 · external_exit: 4 · wrong_timeframe: 6)
Nov 17 20:47:51 Trading-Agent python[465569]: [learning] solo 45 trade validi (servono 50): pesi INVARIATI
Nov 17 20:47:51 Trading-Agent python[465569]: [main] pesi ricalcolati: 42 coppie strat×regime da 61 trade (30g)
Nov 17 20:47:54 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1691 ms
Nov 17 21:02:55 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 21:02:55 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 21:35:31 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 21:48:01 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3970 (registro 1429 · controllo 1426 · trade 886 · rifiutati 93 · pesi 67 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 21:48:01 Trading-Agent python[465569]: [learning] filtrati 16/59 trade (esplorativi: 6 · external_exit: 4 · wrong_timeframe: 6)
Nov 17 21:48:01 Trading-Agent python[465569]: [learning] solo 43 trade validi (servono 50): pesi INVARIATI
Nov 17 21:48:01 Trading-Agent python[465569]: [main] pesi ricalcolati: 40 coppie strat×regime da 59 trade (30g)
Nov 17 21:48:05 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1648 ms
Nov 17 21:48:38 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 21:48:38 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 22:35:58 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 22:48:28 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3970 (registro 1430 · controllo 1426 · trade 886 · rifiutati 93 · pesi 66 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 22:48:28 Trading-Agent python[465569]: [learning] filtrati 16/56 trade (esplorativi: 6 · external_exit: 4 · wrong_timeframe: 6)
Nov 17 22:48:28 Trading-Agent python[465569]: [learning] solo 40 trade validi (servono 50): pesi INVARIATI
Nov 17 22:48:28 Trading-Agent python[465569]: [main] pesi ricalcolati: 38 coppie strat×regime da 56 trade (30g)
Nov 17 22:48:31 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1593 ms
Nov 17 22:50:07 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 22:50:07 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 23:35:59 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 23:39:12 Trading-Agent python[465569]: [main] market scan...
Nov 17 23:40:44 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 17 23:41:02 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 17 23:41:48 Trading-Agent pyth

[... 824 caratteri omessi (testa e coda conservate) ...]

DT', 'HYPEUSDT', 'PENGUUSDT', 'SKYAIUSDT', 'RAYSOLUSDT', 'TRUMPUSDT', 'HEIUSDT', 'GUNUSDT', 'JTOUSDT', 'HUSDT', '1000BONKUSDT', 'ZORAUSDT', 'AGTUSDT', 'PNUTUSDT', 'RUNEUSDT', 'BLESSUSDT', 'IDUSDT', 'BRUSDT', 'PUNDIXUSDT', 'EIGENUSDT', 'TUTUSDT', 'BMTUSDT', 'BULLAUSDT', 'IDOLUSDT', 'SAHARAUSDT', 'PLUMEUSDT', 'KERNELUSDT', 'VELVETUSDT', 'ALCHUSDT', 'MYXUSDT', 'OPENUSDT', 'HUMAUSDT', 'MAVIAUSDT', 'FORMUSDT', 'BANKUSDT', 'HIVEUSDT', 'DEXEUSDT', 'CATIUSDT', 'BIOUSDT', 'CAKEUSDT', 'BSVUSDT', 'QUSDT', 'GALAUSDT', 'ARKMUSDT', 'UBUSDT', 'XMRUSDT', '0GUSDT', 'BTRUSDT', 'AIOUSDT', 'MUBARAKUSDT', 'HOLOUSDT', 'SYRUPUSDT', 'TAKEUSDT', 'HOMEUSDT', 'PHAUSDT', 'PARTIUSDT', 'SCRUSDT', 'TAUSDT', 'XPINUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 17 23:48:38 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3969 (registro 1429 · controllo 1426 · trade 887 · rifiutati 93 · pesi 65 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 17 23:48:39 Trading-Agent python[465569]: [learning] filtrati 15/52 trade (esplorativi: 6 · external_exit: 4 · wrong_timeframe: 5)
Nov 17 23:48:39 Trading-Agent python[465569]: [learning] solo 37 trade validi (servono 50): pesi INVARIATI
Nov 17 23:48:39 Trading-Agent python[465569]: [main] pesi ricalcolati: 35 coppie strat×regime da 52 trade (30g)
Nov 17 23:48:42 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1605 ms
Nov 17 23:48:42 Trading-Agent python[465569]: [learning] foto del 2026-11-18 scritta: 249 validate, 99 pesi strategia×regime
Nov 17 23:48:42 Trading-Agent python[465569]: [giorni] riga del 2026-11-17: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 17 23:51:58 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 23:51:58 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 00:09:24 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-18: universo 100, long 26, short 30, costo 0.19, equity 11143.37
Nov 18 00:13:37 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-18: universo 100, long 31, short 30, costo 0.73, equity 11167.58
Nov 18 00:17:49 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-18: universo 100, long 26, short 30, costo 0.20, equity 11408.14
Nov 18 00:18:03 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-18: 8 ordini limite sul conto, 3 rifiutati
Nov 18 00:18:34 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 00:18:34 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 00:48:53 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3969 (registro 1429 · controllo 1426 · trade 887 · rifiutati 94 · pesi 64 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 18 00:48:53 Trading-Agent python[465569]: [learning] filtrati 14/50 trade (esplorativi: 5 · external_exit: 4 · wrong_timeframe: 5)
Nov 18 00:48:53 Trading-Agent python[465569]: [learning] solo 36 trade validi (servono 50): pesi INVARIATI
Nov 18 00:48:53 Trading-Agent python[465569]: [main] pesi ricalcolati: 34 coppie strat×regime da 50 trade (30g)
Nov 18 00:48:56 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1644 ms
Nov 18 01:03:56 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 01:03:56 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 01:05:59 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-18: 56 eseguiti su 56, costo 0.19 (tutto a mercato 0.68)
Nov 18 01:09:56 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-18: 61 eseguiti su 61, costo 0.73 (tutto a mercato 2.54)
Nov 18 01:14:01 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-18: 56 eseguiti su 56, costo 0.20 (tutto a mercato 0.71)
Nov 18 01:36:48 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 18 01:49:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3966 (registro 1430 · controllo 1426 · trade 885 · rifiutati 93 · pesi 63 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 18 01:49:09 Trading-Agent python[465569]: [learning] filtrati 13/48 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 5)
Nov 18 01:49:09 Trading-Agent python[465569]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Nov 18 01:49:09 Trading-Agent python[465569]: [main] pesi ricalcolati: 33 coppie strat×regime da 48 trade (30g)
Nov 18 01:49:12 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1582 ms
Nov 18 01:49:46 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 01:49:46 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 02:36:59 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 18 02:49:13 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3965 (registro 1431 · controllo 1426 · trade 884 · rifiutati 93 · pesi 62 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 18 02:49:13 Trading-Agent python[465569]: [learning] filtrati 13/48 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 5)
Nov 18 02:49:13 Trading-Agent python[465569]: [learning] solo 35 trade validi (servono 50): pesi INVARIATI
Nov 18 02:49:13 Trading-Agent python[465569]: [main] pesi ricalcolati: 33 coppie strat×regime da 48 trade (30g)
Nov 18 02:49:16 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 4 anomalie, 1513 ms
Nov 18 02:50:20 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 02:50:20 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 03:37:22 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 18 03:39:24 Trading-Agent python[465569]: [main] market scan...
Nov 18 03:40:49 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 18 03:41:06 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 18 03:41:55 Trading-Agent python[465569]: [scanner] 10 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 18 03:41:55 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 03:41:55 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 03:41:55 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'ASTERUSDT', 'XMRUSDT', 'BLESSUSDT', 'AKTUSDT', 'AINUSDT', 'AIOUSDT', 'PUMPUSDT', 'ENAUSDT', 'CROSSUSDT', '1000PEPEUSDT', '0GUSDT', 'TAKEUSDT', 'GPSUSDT', 'SKYAIUSDT', 'RUNEUSDT', 'BMTUSDT', 'PENGUUSDT', 'BIOUSDT', 'UBUSDT', 'TRUMPUSDT', 'AGTUSDT', 'HYPEUSDT', 'KERNELUSDT', 'ZECUSDT', 'MAVIAUSDT', 'BULLAUSDT', 'TAOUSDT', 'PHAUSDT', 'SYRUPUSDT', 'RENDERUSDT', 'HUSDT', 'HEMIUSDT', 'TAUSDT', 'EIGENUSDT', 'BRUSDT', 'GALAUSDT', 'USELESSUSDT', 'HUMAUSDT', 'JUPUSDT', 'HEIUSDT', 'FORMUSDT', 'PNUTUSDT', 'STXUSDT', 'MYXUSDT', 'XPINUSDT', 'FLOCKUSDT', 'SCRUSDT', 'HOLOUSDT', 'RAYSOLUSDT', '1000BONKUSDT', 'JTOUSDT', 'MUBARAKUSDT', 'GRASSUSDT', 'HOMEUSDT', 'DEXEUSDT', 'PLUMEUSDT', 'XVGUSDT', 'CATIUSDT', 'QUSDT', 'PARTIUSDT', 'BANKUSDT', 'GUNUSDT', 'VELVETUSDT', 'BSVUSDT', 'ZORAUSDT', 'OPENUSDT', 'TUTUSDT', 'CAKEUSDT', 'ARKMUSDT', 'IDUSDT', 'BTRUSDT', 'ALCHUSDT', 'SPXUSDT', 'SAHARAUSDT', 'AVAAIUSDT', 'HIVEUSDT', 'PUNDIXUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 18 03:49:24 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3965 (registro 1431 · controllo 1426 · trade 885 · rifiutati 93 · pesi 61 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 18 03:49:24 Trading-Agent python[465569]: [learning] filtrati 13/46 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 5)
Nov 18 03:49:24 Trading-Agent python[465569]: [learning] solo 33 trade validi (servono 50): pesi INVARIATI
Nov 18 03:49:24 Trading-Agent python[465569]: [main] pesi ricalcolati: 31 coppie strat×regime da 46 trade (30g)
Nov 18 03:49:27 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1674 ms
Nov 18 03:51:41 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 03:51:41 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
