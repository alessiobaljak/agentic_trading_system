# 0783-27nov-log-dopo-il-riavvio.req

_eseguito: 2026-11-27 13:12 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
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
Nov 27 04:53:10 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 04:58:50 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3917 (registro 1438 · controllo 1426 · trade 889 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 04:58:53 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1562 ms
Nov 27 05:09:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 05:09:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 05:53:11 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 05:58:59 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3917 (registro 1438 · controllo 1426 · trade 889 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 05:59:02 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1831 ms
Nov 27 06:10:33 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collec

[... 2651 caratteri omessi (testa e coda conservate) ...]

EIGENUSDT', 'BRUSDT', 'XVGUSDT', 'JTOUSDT', 'MYXUSDT', 'ASTERUSDT', 'JUPUSDT', 'ARKMUSDT', 'HOLOUSDT', 'BIOUSDT', 'SKYAIUSDT', 'BMTUSDT', 'XMRUSDT', 'BSVUSDT', 'OPENUSDT', 'SPXUSDT', 'IDUSDT', 'HIVEUSDT', 'SCRUSDT', 'MUBARAKUSDT', 'TRUMPUSDT', 'FLOCKUSDT', 'CROSSUSDT', 'QUSDT', 'AKTUSDT', 'SAHARAUSDT', 'BANKUSDT', 'CAKEUSDT', 'PLUMEUSDT', '1000BONKUSDT', 'HUSDT', 'PNUTUSDT', 'RAYSOLUSDT', 'TAKEUSDT', 'DEXEUSDT', 'PARTIUSDT', 'HEIUSDT', 'MAVIAUSDT', 'GALAUSDT', 'BULLAUSDT', 'UBUSDT', 'TAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 27 07:59:38 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3918 (registro 1439 · controllo 1426 · trade 889 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 07:59:41 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1664 ms
Nov 27 08:12:42 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 08:12:42 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 08:53:48 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 08:59:44 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3131 (registro 1439 · controllo 1426 · trade 103 · rifiutati 94 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 08:59:47 Trading-Agent python[465569]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 08:59:47 Trading-Agent python[465569]:   q = q.where(order_by, "<=", max_value)
Nov 27 08:59:50 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1964 ms
Nov 27 09:14:11 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 09:14:11 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 09:54:15 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 09:59:55 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3917 (registro 1440 · controllo 1426 · trade 887 · rifiutati 95 · pesi 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 27 09:59:57 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1679 ms
Nov 27 10:15:14 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 10:15:14 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 10:54:36 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 11:00:23 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3781 (registro 1379 · controllo 1364 · trade 881 · rifiutati 91 · pesi 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 27 11:00:27 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1959 ms
Nov 27 11:01:00 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 11:01:00 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 11:54:14 Trading-Agent python[465569]: [main] market scan...
Nov 27 11:55:43 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 27 11:56:01 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 27 11:56:47 Trading-Agent python[465569]: [scanner] 14 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 27 11:56:47 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 11:56:47 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 11:56:47 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'QUSDT', 'BLESSUSDT', 'XPINUSDT', 'CATIUSDT', 'XVGUSDT', 'GPSUSDT', 'USELESSUSDT', 'XMRUSDT', 'TUTUSDT', 'TAUSDT', 'ASTERUSDT', 'HOMEUSDT', 'HEIUSDT', 'AGTUSDT', 'ZORAUSDT', 'HUSDT', 'AINUSDT', '1000PEPEUSDT', 'RUNEUSDT', 'SAHARAUSDT', 'OPENUSDT', 'TAOUSDT', 'ENAUSDT', 'BRUSDT', 'SPXUSDT', '0GUSDT', 'GUNUSDT', 'STXUSDT', 'JUPUSDT', 'TRUMPUSDT', 'BIOUSDT', 'ZECUSDT', 'SCRUSDT', 'PUMPUSDT', 'GRASSUSDT', 'UBUSDT', 'SKYAIUSDT', 'VELVETUSDT', 'SYRUPUSDT', 'PHAUSDT', 'BANKUSDT', 'ARKMUSDT', 'DEXEUSDT', 'PNUTUSDT', 'RAYSOLUSDT', 'HYPEUSDT', 'PENGUUSDT', 'PLUMEUSDT', 'MUBARAKUSDT', 'RENDERUSDT', 'BULLAUSDT', 'HEMIUSDT', 'BSVUSDT', 'HUMAUSDT', 'FORMUSDT', '1000BONKUSDT', 'AIOUSDT', 'AKTUSDT', 'JTOUSDT', 'BTRUSDT', 'PARTIUSDT', 'BMTUSDT', 'ALCHUSDT', 'CROSSUSDT', 'KERNELUSDT', 'EIGENUSDT', 'AVAAIUSDT', 'IDUSDT', 'FLOCKUSDT', 'HOLOUSDT', 'MYXUSDT', 'PUNDIXUSDT', 'CAKEUSDT', 'TAKEUSDT', 'MAVIAUSDT', 'HIVEUSDT', 'GALAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 27 11:56:55 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 12:00:31 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3779 (registro 1377 · controllo 1364 · trade 881 · rifiutati 91 · pesi 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 27 12:00:34 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1773 ms
Nov 27 12:02:18 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 12:02:18 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 12:57:18 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 27 13:00:39 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3778 (registro 1376 · controllo 1364 · trade 881 · rifiutati 91 · pesi 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 27 13:00:43 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1888 ms
Nov 27 13:03:28 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 27 13:03:28 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 27 13:10:52 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Nov 27 13:10:52 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Nov 27 13:10:52 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Nov 27 13:10:52 Trading-Agent systemd[1]: trading-bot.service: Consumed 2h 5min 49.116s CPU time, 197.9M memory peak, 0B memory swap peak.
Nov 27 13:10:52 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Nov 27 13:10:54 Trading-Agent python[1171922]: [config] ambiente: DRY_RUN=True, BINANCE_TESTNET=False, BACKTEST_PARITY=True
Nov 27 13:10:54 Trading-Agent python[1171922]: [firebase] connesso (Firestore + RTDB)
Nov 27 13:10:56 Trading-Agent python[1171922]: [main] avvio bot @ 2026-11-27T13:10:56.104226+00:00 DRY_RUN=True
Nov 27 13:10:58 Trading-Agent python[1171922]: [main] equity riconciliata: 817.25 (base 1000.00 + realizzato -182.75 + fette aperte +0.00)
Nov 27 13:10:59 Trading-Agent python[1171922]: [main] versione dell'avvio: commit 2e2b7dc5, config a3508539a199
Nov 27 13:10:59 Trading-Agent python[1171922]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina (spenta in parita': non si applica)
Nov 27 13:10:59 Trading-Agent python[1171922]: [selettore] modello caricato: 150015 righe, soglia 0.40, verdetto NON BATTE, stato ombra, generato 2026-10-12T17:49:35.922866+00:00 -> solo ombra, non decide
Nov 27 13:10:59 Trading-Agent python[1171922]: [main] vecchio sistema FERMO (ops/gate_fermo, nessuna posizione del vecchio paper): niente regime, scansioni, pesi, controllo orario e ciclo di trading; restano i suoi comandi dalla dashboard. Paper, demo, conto vero ed eventi girano come prima
Nov 27 13:10:59 Trading-Agent python[1171922]: [firebase] letture ultime 24 h: 791 (trade 784 · registro 5 · pesi 1 · selettore 1) — quota gratuita 50000/giorno
Nov 27 13:10:59 Trading-Agent python[1171922]: [conto_vero] spento: manca l'interruttore ops/conto_vero_acceso
Nov 27 13:11:00 Trading-Agent python[1171922]: [demo_binance] avvio: indirizzo demo-fapi.binance.com, leva 5, stop_sul_conto 0.35, capitale_nel_file 1000.0, capitale_errato None, capitale_massimo 10000.0, eventi_accesi False, filtri_del_conto_vero_del 2026-11-06, somma_pesi_massima 2.5, peso_massimo_moneta 0.6, eta_massima_decisione_ore 26, pavimento_riparti 0.65, strategia G1, file_della_decisione paper_g1.json
```
