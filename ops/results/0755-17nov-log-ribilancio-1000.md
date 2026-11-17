# 0755-17nov-log-ribilancio-1000.req

_eseguito: 2026-11-17 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 16 16:40:27 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2026 (trade 821 · controllo 558 · registro 554 · rifiutati 37 · pesi 28 · selettore 10 · deriva 9 · referti 9) — quota gratuita 50000/giorno
Nov 16 16:40:28 Trading-Agent python[465569]: [learning] filtrati 25/96 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 11)
Nov 16 16:40:28 Trading-Agent python[465569]: [main] pesi ricalcolati: 62 coppie strat×regime da 96 trade (30g)
Nov 16 16:40:29 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 16:40:32 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1828 ms
Nov 16 16:47:55 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 16:47:55 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 17:40:53 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2165 (trade 826 · controllo 620 · registro 616 · rifiutati 41 · pesi 31 · selettore 11 · deriva 10 · referti 10) — quota gratuita 50000/giorno
Nov 16 17:40:53 Trading-Agent python[465569]: [learning] filtrati 25/96 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 11)
Nov 16 17:40:54 Trading-Agent python[465569]: [main] pesi ricalcolati: 62 coppie strat×regime da 96 trade (30g)
Nov 16 17:40:55 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 17:40:57 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 2070 ms
Nov 16 17:49:31 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 17:49:31 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 18:41:13 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2303 (trade 831 · controllo 682 · registro 677 · rifiutati 45 · pesi 34 · selettore 12 · deriva 11 · referti 11) — quota gratuita 50000/giorno
Nov 16 18:41:13 Trading-Agent python[465569]: [learning] filtrati 25/96 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 11)
Nov 16 18:41:13 Trading-Agent python[465569]: [main] pesi ricalcolati: 62 coppie strat×regime da 96 trade (30g)
Nov 16 18:41:14 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 18:41:17 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1821 ms
Nov 16 18:51:01 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 18:51:01 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 19:36:38 Trading-Agent python[465569]: [main] market scan...
Nov 16 19:38:07 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 16 19:38:25 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 16 19:39:13 Trading-Agent python[465569]: [scanner] 12 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 16 19:39:13 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 19:39:13 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 19:39:14 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BULLAUSDT', 'CROSSUSDT', 'PARTIUSDT', 'QUSDT', 'SKYAIUSDT', 'SYRUPUSDT', 'GPSUSDT', 'IDOLUSDT', 'HUMAUSDT', 'PHAUSDT', 'CAKEUSDT', 'ASTERUSDT', 'XMRUSDT', '1000PEPEUSDT', 'USELESSUSDT', 'HYPEUSDT', 'ZECUSDT', 'GALAUSDT', 'AGTUSDT', 'HOMEUSDT', 'STXUSDT', 'FLOCKUSDT', 'JUPUSDT', 'BLESSUSDT', 'ENAUSDT', '0GUSDT', 'PUMPUSDT', 'BRUSDT', 'AINUSDT', 'VELVETUSDT', 'TRUMPUSDT', 'BSVUSDT', 'GUNUSDT', 'HEIUSDT', 'AVAAIUSDT', 'DEXEUSDT', 'EIGENUSDT', 'TAUSDT', 'ALCHUSDT', 'TAOUSDT', 'BMTUSDT', 'PENGUUSDT', 'SCRUSDT', 'HUSDT', 'BANKUSDT', '1000BONKUSDT', 'AIOUSDT', 'MYXUSDT', 'OPENUSDT', 'UBUSDT', 'PLUMEUSDT', 'PNUTUSDT', 'BTRUSDT', 'AKTUSDT', 'CATIUSDT', 'HEMIUSDT', 'TAKEUSDT', 'KERNELUSDT', 'GRASSUSDT', 'SAHARAUSDT', 'ARKMUSDT', 'RENDERUSDT', 'TUTUSDT', 'HOLOUSDT', 'XPINUSDT', 'MUBARAKUSDT', 'ZORAUSDT', 'SPXUSDT', 'BIOUSDT', 'MAVIAUSDT', 'PUNDIXUSDT', 'FORMUSDT', 'XVGUSDT', 'IDUSDT', 'JTOUSDT', 'HIVEUSDT', 'RAYSOLUSDT', 'MITOUSDT', 'PTBUSDT', 'RUNEUSDT']
Nov 16 19:41:18 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2439 (trade 836 · controllo 744 · registro 736 · rifiutati 49 · pesi 37 · selettore 13 · deriva 12 · referti 12) — quota gratuita 50000/giorno
Nov 16 19:41:18 Trading-Agent python[465569]: [learning] filtrati 25/94 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 11)
Nov 16 19:41:18 Trading-Agent python[465569]: [main] pesi ricalcolati: 60 coppie strat×regime da 94 trade (30g)
Nov 16 19:41:20 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 19:41:22 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1926 ms
Nov 16 19:55:01 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 19:55:01 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 20:41:49 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2576 (trade 840 · controllo 806 · registro 797 · rifiutati 53 · pesi 40 · selettore 14 · deriva 13 · referti 13) — quota gratuita 50000/giorno
Nov 16 20:41:49 Trading-Agent python[465569]: [learning] filtrati 25/93 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 11)
Nov 16 20:41:49 Trading-Agent python[465569]: [main] pesi ricalcolati: 60 coppie strat×regime da 93 trade (30g)
Nov 16 20:41:50 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 20:41:53 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1882 ms
Nov 16 20:56:05 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 20:56:05 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 21:42:03 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2713 (controllo 868 · registro 858 · trade 844 · rifiutati 57 · pesi 43 · selettore 15 · deriva 14 · referti 14) — quota gratuita 50000/giorno
Nov 16 21:42:03 Trading-Agent python[465569]: [learning] filtrati 24/86 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 10)
Nov 16 21:42:04 Trading-Agent python[465569]: [main] pesi ricalcolati: 56 coppie strat×regime da 86 trade (30g)
Nov 16 21:42:05 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 21:42:07 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1842 ms
Nov 16 21:56:44 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 21:56:44 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 21:58:54 Trading-Agent python[465569]: [telegram] invio fallito: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
Nov 16 22:42:23 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 2849 (controllo 930 · registro 920 · trade 847 · rifiutati 60 · pesi 46 · selettore 16 · deriva 15 · referti 15) — quota gratuita 50000/giorno
No

[... 3379 caratteri omessi (testa e coda conservate) ...]

(esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 10)
Nov 16 23:42:45 Trading-Agent python[465569]: [main] pesi ricalcolati: 56 coppie strat×regime da 85 trade (30g)
Nov 16 23:42:46 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 23:42:48 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1797 ms
Nov 16 23:42:49 Trading-Agent python[465569]: [learning] foto del 2026-11-17 scritta: 249 validate, 118 pesi strategia×regime
Nov 16 23:42:49 Trading-Agent python[465569]: [giorni] riga del 2026-11-16: cicli 0/96, aperti 0, rifiutati 0, riavvii 1
Nov 16 23:43:54 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 23:43:54 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 00:09:25 Trading-Agent python[465569]: [paper_g1] ribilancio del 2026-11-17: universo 100, long 26, short 30, costo 0.93, equity 11200.92
Nov 17 00:13:40 Trading-Agent python[465569]: [paper_g11] ribilancio del 2026-11-17: universo 100, long 28, short 30, costo 0.44, equity 11162.52
Nov 17 00:17:57 Trading-Agent python[465569]: [paper_g1n] ribilancio del 2026-11-17: universo 100, long 26, short 30, costo 1.01, equity 11480.16
Nov 17 00:18:20 Trading-Agent python[465569]: [demo_binance] decisione G1 del 2026-11-17: 14 ordini limite sul conto, 3 rifiutati
Nov 17 00:18:51 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 00:18:51 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 00:43:06 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3112 (controllo 1054 · registro 1031 · trade 855 · rifiutati 68 · pesi 52 · selettore 18 · deriva 17 · referti 17) — quota gratuita 50000/giorno
Nov 17 00:43:06 Trading-Agent python[465569]: [learning] filtrati 24/85 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 10)
Nov 17 00:43:07 Trading-Agent python[465569]: [main] pesi ricalcolati: 56 coppie strat×regime da 85 trade (30g)
Nov 17 00:43:08 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 17 00:43:10 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1922 ms
Nov 17 00:49:32 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 00:49:32 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 01:06:00 Trading-Agent python[465569]: [paper_g1] ordini limite del 2026-11-17: 58 eseguiti su 58, costo 0.93 (tutto a mercato 3.26)
Nov 17 01:09:49 Trading-Agent python[465569]: [paper_g11] ordini limite del 2026-11-17: 57 eseguiti su 58, costo 0.66 (tutto a mercato 1.54)
Nov 17 01:14:03 Trading-Agent python[465569]: [paper_g1n] ordini limite del 2026-11-17: 58 eseguiti su 58, costo 1.01 (tutto a mercato 3.52)
Nov 17 01:30:09 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 01:43:17 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3249 (controllo 1116 · registro 1091 · trade 860 · rifiutati 72 · pesi 55 · selettore 19 · deriva 18 · referti 18) — quota gratuita 50000/giorno
Nov 17 01:43:17 Trading-Agent python[465569]: [learning] filtrati 24/84 trade (esplorativi: 9 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 10)
Nov 17 01:43:17 Trading-Agent python[465569]: [main] pesi ricalcolati: 56 coppie strat×regime da 84 trade (30g)
Nov 17 01:43:18 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 17 01:43:21 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1955 ms
Nov 17 01:51:06 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 01:51:06 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 02:30:29 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 02:43:21 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3387 (controllo 1178 · registro 1152 · trade 865 · rifiutati 76 · pesi 58 · selettore 20 · deriva 19 · referti 19) — quota gratuita 50000/giorno
Nov 17 02:43:21 Trading-Agent python[465569]: [learning] filtrati 23/81 trade (esplorativi: 8 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 10)
Nov 17 02:43:22 Trading-Agent python[465569]: [main] pesi ricalcolati: 55 coppie strat×regime da 81 trade (30g)
Nov 17 02:43:22 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 17 02:43:24 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1602 ms
Nov 17 02:52:44 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 02:52:44 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 03:30:36 Trading-Agent python[465569]: [demo_binance] posizioni diverse da quelle volute: ['LITUSDT']
Nov 17 03:37:25 Trading-Agent python[465569]: [main] market scan...
Nov 17 03:38:54 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 17 03:39:11 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 17 03:39:57 Trading-Agent python[465569]: [scanner] 11 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 17 03:39:57 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 03:39:57 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 17 03:39:57 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['BLESSUSDT', 'ZECUSDT', '1000BONKUSDT', '1000PEPEUSDT', 'TAOUSDT', 'PUMPUSDT', 'GUNUSDT', 'PHAUSDT', 'HOMEUSDT', 'SCRUSDT', 'TRUMPUSDT', 'FORMUSDT', 'KERNELUSDT', 'JUPUSDT', 'MUBARAKUSDT', 'GPSUSDT', 'ENAUSDT', 'SKYAIUSDT', 'AGTUSDT', 'PNUTUSDT', 'RAYSOLUSDT', 'BULLAUSDT', 'CATIUSDT', 'PENGUUSDT', 'SAHARAUSDT', 'USELESSUSDT', 'XMRUSDT', 'CROSSUSDT', 'BTRUSDT', 'RENDERUSDT', 'GALAUSDT', 'AKTUSDT', 'SPXUSDT', 'ASTERUSDT', 'ZORAUSDT', 'BSVUSDT', 'STXUSDT', 'OPENUSDT', 'TAKEUSDT', 'ARKMUSDT', 'BMTUSDT', 'FLOCKUSDT', 'XPINUSDT', 'HYPEUSDT', 'HEIUSDT', 'AINUSDT', 'GRASSUSDT', 'EIGENUSDT', 'AVAAIUSDT', 'RUNEUSDT', 'ALCHUSDT', 'PUNDIXUSDT', 'XVGUSDT', 'HEMIUSDT', 'CAKEUSDT', 'HUSDT', 'TUTUSDT', 'IDUSDT', 'QUSDT', 'AIOUSDT', 'PARTIUSDT', 'MYXUSDT', 'HOLOUSDT', 'PLUMEUSDT', 'HIVEUSDT', 'UBUSDT', 'JTOUSDT', 'DEXEUSDT', 'SYRUPUSDT', 'IDOLUSDT', 'MAVIAUSDT', 'BIOUSDT', 'HUMAUSDT', 'BANKUSDT', '0GUSDT', 'VELVETUSDT', 'BRUSDT', 'TAUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 17 03:43:42 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 3523 (controllo 1240 · registro 1211 · trade 870 · rifiutati 80 · pesi 61 · selettore 21 · deriva 20 · referti 20) — quota gratuita 50000/giorno
Nov 17 03:43:42 Trading-Agent python[465569]: [learning] filtrati 23/81 trade (esplorativi: 8 · external_exit: 4 · short_duration: 1 · wrong_timeframe: 10)
Nov 17 03:43:42 Trading-Agent python[465569]: [main] pesi ricalcolati: 55 coppie strat×regime da 81 trade (30g)
Nov 17 03:43:43 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 17 03:43:46 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1823 ms
Nov 17 03:56:02 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 17 03:56:02 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
