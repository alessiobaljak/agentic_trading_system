# 0762-20nov-log-ribilancio-1000.req

_eseguito: 2026-11-20 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 19 16:59:52 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1502 ms
Nov 19 17:07:47 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 17:07:47 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 17:50:45 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 18:00:10 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3789 (registro 1365 · controllo 1364 · trade 881 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 19 18:00:11 Trading-Agent python[465569]: [learning] filtrati 5/12 trade (esplorativi: 1 · external_exit: 4)
Nov 19 18:00:11 Trading-Agent python[465569]: [learning] solo 7 trade validi (servono 50): pesi INVARIATI
Nov 19 18:00:11 Trading-Agent python[465569]: [main] pesi ricalcolati: 7 coppie strat×regime da 12 trade (30g)
Nov 19 18:00:14 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1815 ms
Nov 19 18:09:02 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 18:09:02 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 18:51:17 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 19:00:11 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3792 (registro 1367 · controllo 1364 · trade 882 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 19 19:00:12 Trading-Agent python[465569]: [learning] filtrati 5/11 trade (esplorativi: 1 · external_exit: 4)
Nov 19 19:00:12 Trading-Agent python[465569]: [learning] solo 6 trade validi (servono 50): pesi INVARIATI
Nov 19 19:00:12 Trading-Agent python[465569]: [main] pesi ricalcolati: 6 coppie strat×regime da 11 trade (30g)
Nov 19 19:00:15 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2062 ms
Nov 19 19:10:10 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 19:10:10 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 19:42:45 Trading-Agent python[465569]: [main] market scan...
Nov 19 19:44:18 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 19 19:44:35 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 19 19:45:25 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 19 19:45:25 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['CROSSUSDT', 'ZECUSDT', 'GUNUSDT', '1000PEPEUSDT', 'JUPUSDT', 'AINUSDT', 'KERNELUSDT', 'USELESSUSDT', 'ENAUSDT', 'VELVETUSDT', 'SYRUPUSDT', 'EIGENUSDT', 'GRASSUSDT', 'AVAAIUSDT', 'BLESSUSDT', 'BRUSDT', 'MUBARAKUSDT', 'HUMAUSDT', 'TRUMPUSDT', 'HYPEUSDT', 'RENDERUSDT', 'PENGUUSDT', 'IDOLUSDT', 'HUSDT', 'ALCHUSDT', 'PUMPUSDT', '1000BONKUSDT', 'ASTERUSDT', 'UBUSDT', 'MAVIAUSDT', 'ZORAUSDT', 'TAOUSDT', 'HOLOUSDT', 'AIOUSDT', 'MYXUSDT', 'SPXUSDT', 'TUTUSDT', 'PHAUSDT', 'PLUMEUSDT', 'XVGUSDT', 'CATIUSDT', 'HOMEUSDT', 'STXUSDT', 'ARKMUSDT', '0GUSDT', 'SCRUSDT', 'SAHARAUSDT', 'DEXEUSDT', 'XMRUSDT', 'QUSDT', 'HEIUSDT', 'JTOUSDT', 'HEMIUSDT', 'FORMUSDT', 'BIOUSDT', 'AGTUSDT', 'RUNEUSDT', 'HIVEUSDT', 'CAKEUSDT', 'FLOCKUSDT', 'SKYAIUSDT', 'RAYSOLUSDT', 'BANKUSDT', 'BULLAUSDT', 'PUNDIXUSDT', 'TAKEUSDT', 'IDUSDT', 'BSVUSDT', 'PNUTUSDT', 'GPSUSDT', 'TAUSDT', 'AKTUSDT', 'BTRUSDT', 'GALAUSDT', 'PARTIUSDT', 'OPENUSDT', 'XPINUSDT', 'MITOUSDT', 'PTBUSDT', 'BMTUSDT']
Nov 19 19:51:20 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 19:55:59 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 19:55:59 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 20:00:22 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3794 (registro 1368 · controllo 1364 · trade 883 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 19 20:00:22 Trading-Agent python[465569]: [learning] filtrati 5/11 trade (esplorativi: 1 · external_exit: 4)
Nov 19 20:00:22 Trading-Agent python[465569]: [learning] solo 6 trade validi (servono 50): pesi INVARIATI
Nov 19 20:00:22 Trading-Agent python[465569]: [main] pesi ricalcolati: 6 coppie strat×regime da 11 trade (30g)
Nov 19 20:00:26 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1815 ms
Nov 19 20:11:27 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 20:11:27 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 20:51:28 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 21:00:30 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3804 (registro 1378 · controllo 1364 · trade 883 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 19 21:00:30 Trading-Agent python[465569]: [learning] filtrati 5/11 trade (esplorativi: 1 · external_exit: 4)
Nov 19 21:00:30 Trading-Agent python[465569]: [learning] solo 6 trade validi (servono 50): pesi INVARIATI
Nov 19 21:00:30 Trading-Agent python[465569]: [main] pesi ricalcolati: 6 coppie strat×regime da 11 trade (30g)
Nov 19 21:00:33 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1607 ms
Nov 19 21:12:59 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 21:12:59 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 21:52:01 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 22:00:46 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3806 (registro 1380 · controllo 1364 · trade 883 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 19 22:00:46 Trading-Agent python[465569]: [learning] filtrati 4/10 trade (external_exit: 4)
Nov 19 22:00:46 Trading-Agent python[465569]: [learning] solo 6 trade validi (servono 50): pesi INVARIATI
Nov 19 22:00:46 Trading-Agent python[465569]: [main] pesi ricalcolati: 6 coppie strat×regime da 10 trade (30g)
Nov 19 22:00:49 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1586 ms
Nov 19 22:14:07 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 22:14:07 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 22:52:06 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 23:01:14 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3807 (registro 1381 · controllo 1364 · trade 883 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 19 23:01:14 Trading-Agent python[465569]: [learning] filtrati 4/9 trade (external_exit: 4)
Nov 19 23:01:14 Trading-Agent python[465569]: [learning] solo 5 trade validi (servono 50): pesi INVARIATI
Nov 19 23:01:14 Trading-Agent python[465569]: [main] pesi ricalcolati: 5 coppie strat×regime da 9 trade (30g)
Nov 19 23:01:17 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1931 ms
Nov 19 23:01:18 Trading-Agent python[465569]: [learning] foto del 2026-11-20 scritta: 249 validate, 99 pesi strategia×regime
Nov 19 23:01:18 Trading-Agent python[465569]: [giorni] riga del 2026-11-19: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 19 23:15:38 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 23:15:38 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 23:43:02 Trading-Agent python[465569]: [main] market scan...
Nov 19 23:44:31 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 19 23:44:49 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol

[... 89 caratteri omessi (testa e coda conservate) ...]

a soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 19 23:45:36 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 23:45:36 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 23:45:37 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['HUMAUSDT', 'BLESSUSDT', 'XPINUSDT', 'AKTUSDT', 'GRASSUSDT', 'BTRUSDT', 'USELESSUSDT', 'BSVUSDT', 'IDUSDT', 'STXUSDT', 'JUPUSDT', 'VELVETUSDT', 'BRUSDT', 'SYRUPUSDT', 'TRUMPUSDT', 'PHAUSDT', 'PUMPUSDT', 'ENAUSDT', 'TAOUSDT', 'HYPEUSDT', 'SKYAIUSDT', 'PARTIUSDT', 'HIVEUSDT', '1000PEPEUSDT', 'MYXUSDT', 'ZECUSDT', '0GUSDT', 'PLUMEUSDT', 'GALAUSDT', 'PNUTUSDT', 'XVGUSDT', 'IDOLUSDT', 'PENGUUSDT', 'TUTUSDT', 'JTOUSDT', 'ASTERUSDT', 'RAYSOLUSDT', 'XMRUSDT', 'RENDERUSDT', 'SPXUSDT', 'KERNELUSDT', 'AVAAIUSDT', 'DEXEUSDT', 'RUNEUSDT', 'EIGENUSDT', 'CAKEUSDT', 'UBUSDT', 'HEMIUSDT', '1000BONKUSDT', 'BULLAUSDT', 'CROSSUSDT', 'ALCHUSDT', 'HUSDT', 'BANKUSDT', 'AGTUSDT', 'OPENUSDT', 'HOMEUSDT', 'MUBARAKUSDT', 'FLOCKUSDT', 'AINUSDT', 'TAKEUSDT', 'PUNDIXUSDT', 'BIOUSDT', 'GUNUSDT', 'HEIUSDT', 'ZORAUSDT', 'HOLOUSDT', 'SCRUSDT', 'TAUSDT', 'SAHARAUSDT', 'FORMUSDT', 'QUSDT', 'ARKMUSDT', 'MAVIAUSDT', 'CATIUSDT', 'AIOUSDT', 'GPSUSDT', 'BMTUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 19 23:52:33 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 00:01:35 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3817 (registro 1390 · controllo 1364 · trade 883 · rifiutati 92 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 00:01:35 Trading-Agent python[465569]: [learning] filtrati 4/9 trade (external_exit: 4)
Nov 20 00:01:35 Trading-Agent python[465569]: [learning] solo 5 trade validi (servono 50): pesi INVARIATI
Nov 20 00:01:35 Trading-Agent python[465569]: [main] pesi ricalcolati: 5 coppie strat×regime da 9 trade (30g)
Nov 20 00:01:37 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1660 ms
Nov 20 00:09:41 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-20: universo 100, long 27, short 30, costo 0.45, equity 10866.23
Nov 20 00:14:01 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-20: universo 100, long 28, short 27, costo 0.95, equity 10922.60
Nov 20 00:18:23 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-20: universo 100, long 27, short 30, costo 0.49, equity 11130.65
Nov 20 00:18:37 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-20: 7 ordini limite sul conto, 3 rifiutati
Nov 20 00:19:08 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 00:19:08 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 01:01:50 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3807 (registro 1382 · controllo 1364 · trade 882 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 01:01:50 Trading-Agent python[465569]: [learning] filtrati 4/9 trade (external_exit: 4)
Nov 20 01:01:50 Trading-Agent python[465569]: [learning] solo 5 trade validi (servono 50): pesi INVARIATI
Nov 20 01:01:50 Trading-Agent python[465569]: [main] pesi ricalcolati: 5 coppie strat×regime da 9 trade (30g)
Nov 20 01:01:53 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1930 ms
Nov 20 01:04:30 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 01:04:30 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 01:05:55 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-20: 58 eseguiti su 58, costo 0.45 (tutto a mercato 1.58)
Nov 20 01:10:42 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-20: 59 eseguiti su 59, costo 0.95 (tutto a mercato 3.31)
Nov 20 01:14:32 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-20: 58 eseguiti su 58, costo 0.49 (tutto a mercato 1.70)
Nov 20 01:53:26 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 02:02:19 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3806 (registro 1381 · controllo 1364 · trade 882 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 02:02:19 Trading-Agent python[465569]: [learning] filtrati 4/8 trade (external_exit: 4)
Nov 20 02:02:19 Trading-Agent python[465569]: [learning] solo 4 trade validi (servono 50): pesi INVARIATI
Nov 20 02:02:19 Trading-Agent python[465569]: [main] pesi ricalcolati: 4 coppie strat×regime da 8 trade (30g)
Nov 20 02:02:22 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1623 ms
Nov 20 02:06:31 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 02:06:31 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 02:53:31 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 03:02:47 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3808 (registro 1384 · controllo 1364 · trade 881 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 03:02:47 Trading-Agent python[465569]: [learning] filtrati 4/8 trade (external_exit: 4)
Nov 20 03:02:47 Trading-Agent python[465569]: [learning] solo 4 trade validi (servono 50): pesi INVARIATI
Nov 20 03:02:47 Trading-Agent python[465569]: [main] pesi ricalcolati: 4 coppie strat×regime da 8 trade (30g)
Nov 20 03:02:50 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1526 ms
Nov 20 03:07:23 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 03:07:23 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 03:43:27 Trading-Agent python[465569]: [main] market scan...
Nov 20 03:44:58 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 20 03:45:15 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 20 03:46:03 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 20 03:46:03 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 03:46:03 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 20 03:46:03 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['GRASSUSDT', 'JUPUSDT', 'TUTUSDT', 'UBUSDT', 'ENAUSDT', 'ARKMUSDT', 'XVGUSDT', 'PUMPUSDT', 'HUMAUSDT', 'ZORAUSDT', 'ZECUSDT', 'BRUSDT', 'MUBARAKUSDT', 'HUSDT', 'USELESSUSDT', 'AVAAIUSDT', 'RENDERUSDT', '1000PEPEUSDT', 'TAUSDT', 'TAOUSDT', 'SCRUSDT', 'BIOUSDT', '1000BONKUSDT', 'IDOLUSDT', 'BMTUSDT', 'EIGENUSDT', 'PARTIUSDT', 'HYPEUSDT', 'ASTERUSDT', 'PENGUUSDT', 'FORMUSDT', 'HEMIUSDT', 'SPXUSDT', 'STXUSDT', 'AGTUSDT', 'HOMEUSDT', 'CROSSUSDT', 'TRUMPUSDT', 'AKTUSDT', 'SAHARAUSDT', 'BULLAUSDT', 'OPENUSDT', 'PLUMEUSDT', 'PHAUSDT', 'HEIUSDT', 'VELVETUSDT', 'GUNUSDT', 'GALAUSDT', '0GUSDT', 'MYXUSDT', 'SYRUPUSDT', 'BLESSUSDT', 'BANKUSDT', 'XPINUSDT', 'JTOUSDT', 'AIOUSDT', 'ALCHUSDT', 'FLOCKUSDT', 'HIVEUSDT', 'DEXEUSDT', 'SKYAIUSDT', 'MAVIAUSDT', 'TAKEUSDT', 'PNUTUSDT', 'XMRUSDT', 'AINUSDT', 'IDUSDT', 'BSVUSDT', 'HOLOUSDT', 'RUNEUSDT', 'CATIUSDT', 'KERNELUSDT', 'QUSDT', 'PUNDIXUSDT', 'CAKEUSDT', 'GPSUSDT', 'RAYSOLUSDT', 'BTRUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 20 03:54:02 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 20 04:03:11 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3808 (registro 1383 · controllo 1364 · trade 882 · rifiutati 91 · pesi 44 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 20 04:03:11 Trading-Agent python[465569]: [learning] filtrati 4/6 trade (external_exit: 4)
Nov 20 04:03:11 Trading-Agent python[465569]: [learning] solo 2 trade validi (servono 50): pesi INVARIATI
Nov 20 04:03:11 Trading-Agent python[465569]: [main] pesi ricalcolati: 2 coppie strat×regime da 6 trade (30g)
Nov 20 04:03:14 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1634 ms
Nov 20 04:08:06 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 20 04:08:06 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
