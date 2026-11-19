# 0760-19nov-log-ribilancio-1000.req

_eseguito: 2026-11-19 04:18 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 18 21:51:03 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:51:50 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:52:29 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:53:08 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:53:47 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:54:17 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3922 (controllo 1426 · registro 1420 · trade 885 · rifiutati 94 · pesi 46 · referti 23 · selettore 23 · deriva 5) — quota gratuita 50000/giorno
Nov 18 21:54:17 Trading-Agent python[465569]: [learning] filtrati 12/32 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 4)
Nov 18 21:54:17 Trading-Agent python[465569]: [learning] solo 20 trade validi (servono 50): pesi INVARIATI
Nov 18 21:54:17 Trading-Agent python[465569]: [main] pesi ricalcolati: 18 coppie strat×regime da 32 trade (30g)
Nov 18 21:54:20 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1624 ms
Nov 18 21:54:31 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:55:10 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:55:49 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:56:28 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:57:14 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:57:45 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 21:57:45 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 21:58:02 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:58:40 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:59:19 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 21:59:58 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:00:45 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:01:24 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:02:03 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:02:41 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:03:20 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:03:59 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:04:38 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:05:24 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:06:04 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:06:42 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:07:21 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:08:00 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:08:39 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:09:17 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:10:05 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:11:05 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:11:43 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:12:23 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:13:09 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:13:48 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:14:51 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:15:29 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:16:08 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 18 22:45:41 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 18 22:54:27 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3917 (controllo 1426 · registro 1416 · trade 885 · rifiutati 94 · pesi 46 · referti 23 · selettore 23 · deriva 4) — quota gratuita 50000/giorno
Nov 18 22:54:27 Trading-Agent python[465569]: [learning] filtrati 12/31 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 4)
Nov 18 22:54:27 Trading-Agent python[465569]: [learning] solo 19 trade validi (servono 50): pesi INVARIATI
Nov 18 22:54:27 Trading-Agent python[465569]: [main] pesi ricalcolati: 17 coppie strat×regime da 31 trade (30g)
Nov 18 22:54:30 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1739 ms
Nov 18 22:58:17 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 22:58:17 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 23:41:19 Trading-Agent python[465569]: [main] market scan...
Nov 18 23:42:45 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 18 23:43:03 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 18 23:43:49 Trading-Agent python[465569]: [scanner] 14 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 18 23:43:49 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 23:43:49 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 18 23:43:49 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['VELVETUSDT', 'JUPUSDT', 'ASTERUSDT', 'HEMIUSDT', 'ENAUSDT', 'MUBARAKUSDT', 'XPINUSDT', 'BTRUSDT', 'IDUSDT', 'MAVIAUSDT', 'PARTIUSDT', 'KERNELUSDT', 'CROSSUSDT', 'RENDERUSDT', 'AINUSDT', 'GRASSUSDT', 'IDOLUSDT', 'BANKUSDT', 'USELESSUSDT', 'XMRUSDT', 'FLOCKUSDT', 'PUMPUSDT', 'BMTUSDT', 'ALCHUSDT', 'PHAUSDT', 'TRUMPUSDT', 'PNUTUSDT', 'AGTUSDT', 'EIGENUSDT', 'BLESSUSDT', 'ZECUSDT', 'BRUSDT', 'HYPEUSDT', '1000BONKUSDT', 'PENGUUSDT', 'JTOUSDT', '0GUSDT', 'HUSDT', '1000PEPEUSDT', 'ZORAUSDT', 'MYXUSDT', 'TAOUSDT', 'HUMAUSDT', 'HIVEUSDT', 'RUNEUSDT', 'TUTUSDT', 'XVGUSDT', 'DEXEUSDT', 'STXUSDT', 'HEIUSDT', 'SYRUPUSDT', 'CATIUSDT', 'SPXUSDT', 'SCRUSDT', 'BIOUSDT', 'BSVUSDT', 'BULLAUSDT', 'RAYSOLUSDT', 'CAKEUSDT', 'TAKEUSDT', 'GALAUS

[... 233 caratteri omessi (testa e coda conservate) ...]

8 23:46:00 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 18 23:54:45 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3917 (controllo 1426 · registro 1418 · trade 884 · rifiutati 94 · pesi 46 · referti 23 · selettore 23 · deriva 3) — quota gratuita 50000/giorno
Nov 18 23:54:45 Trading-Agent python[465569]: [learning] filtrati 12/31 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 4)
Nov 18 23:54:45 Trading-Agent python[465569]: [learning] solo 19 trade validi (servono 50): pesi INVARIATI
Nov 18 23:54:45 Trading-Agent python[465569]: [main] pesi ricalcolati: 17 coppie strat×regime da 31 trade (30g)
Nov 18 23:54:48 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1641 ms
Nov 18 23:54:48 Trading-Agent python[465569]: [learning] foto del 2026-11-19 scritta: 249 validate, 99 pesi strategia×regime
Nov 18 23:54:48 Trading-Agent python[465569]: [giorni] riga del 2026-11-18: cicli 0/96, aperti 0, rifiutati 0, riavvii 0
Nov 18 23:59:29 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 18 23:59:29 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 00:09:35 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-19: universo 100, long 28, short 29, costo 0.62, equity 11002.55
Nov 19 00:13:49 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-19: universo 100, long 29, short 28, costo 0.77, equity 10976.87
Nov 19 00:18:01 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-19: universo 100, long 28, short 29, costo 0.69, equity 11266.52
Nov 19 00:18:19 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-19: 13 ordini limite sul conto, 3 rifiutati
Nov 19 00:18:50 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 00:18:50 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 00:54:52 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3919 (controllo 1426 · registro 1419 · trade 885 · rifiutati 95 · pesi 46 · referti 23 · selettore 23 · deriva 2) — quota gratuita 50000/giorno
Nov 19 00:54:52 Trading-Agent python[465569]: [learning] filtrati 12/30 trade (esplorativi: 4 · external_exit: 4 · wrong_timeframe: 4)
Nov 19 00:54:52 Trading-Agent python[465569]: [learning] solo 18 trade validi (servono 50): pesi INVARIATI
Nov 19 00:54:52 Trading-Agent python[465569]: [main] pesi ricalcolati: 16 coppie strat×regime da 30 trade (30g)
Nov 19 00:54:55 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1762 ms
Nov 19 01:04:22 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 01:04:22 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 01:06:25 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-19: 58 eseguiti su 58, costo 0.62 (tutto a mercato 2.16)
Nov 19 01:10:15 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-19: 62 eseguiti su 62, costo 0.77 (tutto a mercato 2.70)
Nov 19 01:12:25 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 19 01:13:04 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 19 01:13:43 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 19 01:14:21 Trading-Agent python[465569]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 19 01:14:43 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-19: 58 eseguiti su 58, costo 0.69 (tutto a mercato 2.40)
Nov 19 01:46:09 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 01:55:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3919 (controllo 1426 · registro 1419 · trade 886 · rifiutati 95 · pesi 46 · referti 23 · selettore 23 · deriva 1) — quota gratuita 50000/giorno
Nov 19 01:55:09 Trading-Agent python[465569]: [learning] filtrati 10/27 trade (esplorativi: 2 · external_exit: 4 · wrong_timeframe: 4)
Nov 19 01:55:09 Trading-Agent python[465569]: [learning] solo 17 trade validi (servono 50): pesi INVARIATI
Nov 19 01:55:09 Trading-Agent python[465569]: [main] pesi ricalcolati: 15 coppie strat×regime da 27 trade (30g)
Nov 19 01:55:12 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1419 ms
Nov 19 02:05:26 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 02:05:26 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 02:46:31 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 02:55:23 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3917 (controllo 1426 · registro 1418 · trade 886 · rifiutati 95 · pesi 46 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 19 02:55:24 Trading-Agent python[465569]: [learning] filtrati 10/27 trade (esplorativi: 2 · external_exit: 4 · wrong_timeframe: 4)
Nov 19 02:55:24 Trading-Agent python[465569]: [learning] solo 17 trade validi (servono 50): pesi INVARIATI
Nov 19 02:55:24 Trading-Agent python[465569]: [main] pesi ricalcolati: 15 coppie strat×regime da 27 trade (30g)
Nov 19 02:55:27 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1832 ms
Nov 19 03:06:33 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 03:06:33 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 03:41:45 Trading-Agent python[465569]: [main] market scan...
Nov 19 03:43:14 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 19 03:43:31 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 19 03:44:18 Trading-Agent python[465569]: [scanner] 14 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 19 03:44:18 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 03:44:18 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 19 03:44:19 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'BULLAUSDT', 'XPINUSDT', 'CROSSUSDT', 'BLESSUSDT', 'HUMAUSDT', '0GUSDT', 'JUPUSDT', 'OPENUSDT', 'PUMPUSDT', '1000PEPEUSDT', 'KERNELUSDT', 'ASTERUSDT', 'ZECUSDT', 'BSVUSDT', 'USELESSUSDT', 'HYPEUSDT', 'TRUMPUSDT', 'ZORAUSDT', 'RENDERUSDT', 'SKYAIUSDT', 'GPSUSDT', '1000BONKUSDT', 'MYXUSDT', 'AKTUSDT', 'ENAUSDT', 'BRUSDT', 'XVGUSDT', 'BMTUSDT', 'PENGUUSDT', 'TAUSDT', 'QUSDT', 'SCRUSDT', 'BTRUSDT', 'XMRUSDT', 'AVAAIUSDT', 'HUSDT', 'UBUSDT', 'JTOUSDT', 'IDUSDT', 'TAOUSDT', 'EIGENUSDT', 'GRASSUSDT', 'RAYSOLUSDT', 'ARKMUSDT', 'HIVEUSDT', 'HEMIUSDT', 'VELVETUSDT', 'DEXEUSDT', 'HEIUSDT', 'AIOUSDT', 'BANKUSDT', 'GUNUSDT', 'AINUSDT', 'HOLOUSDT', 'PNUTUSDT', 'PLUMEUSDT', 'FORMUSDT', 'STXUSDT', 'MUBARAKUSDT', 'PARTIUSDT', 'AGTUSDT', 'PHAUSDT', 'HOMEUSDT', 'BIOUSDT', 'CATIUSDT', 'FLOCKUSDT', 'CAKEUSDT', 'TUTUSDT', 'RUNEUSDT', 'SPXUSDT', 'GALAUSDT', 'SYRUPUSDT', 'PUNDIXUSDT', 'SAHARAUSDT', 'TAKEUSDT', 'ALCHUSDT', 'MAVIAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 19 03:47:00 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 19 03:55:53 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3918 (controllo 1426 · registro 1419 · trade 886 · rifiutati 95 · pesi 46 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 19 03:55:53 Trading-Agent python[465569]: [learning] filtrati 9/26 trade (esplorativi: 2 · external_exit: 4 · wrong_timeframe: 3)
Nov 19 03:55:53 Trading-Agent python[465569]: [learning] solo 17 trade validi (servono 50): pesi INVARIATI
Nov 19 03:55:53 Trading-Agent python[465569]: [main] pesi ricalcolati: 15 coppie strat×regime da 26 trade (30g)
Nov 19 03:55:56 Trading-Agent python[465569]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1664 ms
Nov 19 04:07:35 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 19 04:07:35 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
