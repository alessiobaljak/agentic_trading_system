# 0745-16nov-log-ribilancio-1000.req

_eseguito: 2026-11-16 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 15 16:40:15 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 16:40:15 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 17:22:00 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 17:35:47 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 2303 (trade 827 · controllo 682 · registro 681 · rifiutati 45 · pesi 34 · selettore 12 · deriva 11 · referti 11) — quota gratuita 50000/giorno
Nov 15 17:35:47 Trading-Agent python[404046]: [learning] filtrati 29/117 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 13)
Nov 15 17:35:48 Trading-Agent python[404046]: [main] pesi ricalcolati: 75 coppie strat×regime da 117 trade (30g)
Nov 15 17:35:49 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 17:35:51 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1888 ms
Nov 15 17:41:34 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 17:41:34 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 18:22:09 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 18:30:47 Trading-Agent python[404046]: [main] market scan...
Nov 15 18:32:18 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 15 18:32:36 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 15 18:33:23 Trading-Agent python[404046]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 15 18:33:23 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 18:33:23 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 18:33:24 Trading-Agent python[404046]: [main] valutate 80 coin validate (80 nel registro): ['PUMPUSDT', 'MYXUSDT', 'AVAAIUSDT', 'HIVEUSDT', 'HUMAUSDT', 'AINUSDT', 'JTOUSDT', 'TRUMPUSDT', 'HUSDT', '1000PEPEUSDT', 'IDOLUSDT', 'ASTERUSDT', 'FLOCKUSDT', 'AIOUSDT', 'HYPEUSDT', '0GUSDT', 'CAKEUSDT', 'DEXEUSDT', 'PUNDIXUSDT', '1000BONKUSDT', 'PLUMEUSDT', 'PNUTUSDT', 'PHAUSDT', 'ALCHUSDT', 'BANKUSDT', 'BSVUSDT', 'GRASSUSDT', 'HOMEUSDT', 'OPENUSDT', 'IDUSDT', 'PENGUUSDT', 'EIGENUSDT', 'RENDERUSDT', 'ZECUSDT', 'SAHARAUSDT', 'VELVETUSDT', 'TAKEUSDT', 'USELESSUSDT', 'GUNUSDT', 'TAOUSDT', 'HEIUSDT', 'QUSDT', 'MAVIAUSDT', 'JUPUSDT', 'RAYSOLUSDT', 'ENAUSDT', 'ARKMUSDT', 'SKYAIUSDT', 'HEMIUSDT', 'SYRUPUSDT', 'BRUSDT', 'BIOUSDT', 'BLESSUSDT', 'STXUSDT', 'XMRUSDT', 'FORMUSDT', 'PARTIUSDT', 'XVGUSDT', 'SPXUSDT', 'SCRUSDT', 'CATIUSDT', 'ZORAUSDT', 'KERNELUSDT', 'HOLOUSDT', 'MUBARAKUSDT', 'GPSUSDT', 'TUTUSDT', 'AGTUSDT', 'BTRUSDT', 'XPINUSDT', 'UBUSDT', 'GALAUSDT', 'AKTUSDT', 'BMTUSDT', 'CROSSUSDT', 'TAUSDT', 'MITOUSDT', 'PTBUSDT', 'BULLAUSDT', 'RUNEUSDT']
Nov 15 18:35:59 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 2440 (trade 833 · controllo 744 · registro 740 · rifiutati 49 · pesi 37 · selettore 13 · deriva 12 · referti 12) — quota gratuita 50000/giorno
Nov 15 18:35:59 Trading-Agent python[404046]: [learning] filtrati 29/117 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 13)
Nov 15 18:35:59 Trading-Agent python[404046]: [main] pesi ricalcolati: 75 coppie strat×regime da 117 trade (30g)
Nov 15 18:36:00 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 18:36:03 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1959 ms
Nov 15 18:43:02 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 18:43:02 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 19:22:14 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 19:36:08 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 2577 (trade 837 · controllo 806 · registro 801 · rifiutati 53 · pesi 40 · selettore 14 · deriva 13 · referti 13) — quota gratuita 50000/giorno
Nov 15 19:36:08 Trading-Agent python[404046]: [learning] filtrati 28/115 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 15 19:36:09 Trading-Agent python[404046]: [main] pesi ricalcolati: 74 coppie strat×regime da 115 trade (30g)
Nov 15 19:36:10 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 19:36:12 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1942 ms
Nov 15 19:44:08 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 19:44:08 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 20:22:29 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 20:36:16 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 2716 (controllo 868 · registro 863 · trade 842 · rifiutati 57 · pesi 43 · selettore 15 · deriva 14 · referti 14) — quota gratuita 50000/giorno
Nov 15 20:36:16 Trading-Agent python[404046]: [learning] filtrati 28/115 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 15 20:36:16 Trading-Agent python[404046]: [main] pesi ricalcolati: 74 coppie strat×regime da 115 trade (30g)
Nov 15 20:36:18 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 20:36:20 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1888 ms
Nov 15 20:45:47 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 20:45:47 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 21:22:57 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 21:36:35 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 2855 (controllo 930 · registro 925 · trade 847 · rifiutati 61 · pesi 46 · selettore 16 · deriva 15 · referti 15) — quota gratuita 50000/giorno
Nov 15 21:36:35 Trading-Agent python[404046]: [learning] filtrati 28/114 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 15 21:36:36 Trading-Agent python[404046]: [main] pesi ricalcolati: 73 coppie strat×regime da 114 trade (30g)
Nov 15 21:36:37 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 21:36:39 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1798 ms
Nov 15 21:46:37 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 21:46:37 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 22:23:27 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 22:30:58 Trading-Agent python[404046]: [main] market scan...
Nov 15 22:32:27 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 15 22:32:44 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 15 22:33:31 Trading-Agent python[404046]: [scanner] 10 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro co

[... 3079 caratteri omessi (testa e coda conservate) ...]

ning] filtrati 28/114 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 15 23:36:39 Trading-Agent python[404046]: [main] pesi ricalcolati: 73 coppie strat×regime da 114 trade (30g)
Nov 15 23:36:40 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 23:36:42 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1677 ms
Nov 15 23:36:43 Trading-Agent python[404046]: [learning] foto del 2026-11-16 scritta: 249 validate, 130 pesi strategia×regime
Nov 15 23:36:43 Trading-Agent python[404046]: [giorni] riga del 2026-11-15: cicli 0/96, aperti 0, rifiutati 0, riavvii 1
Nov 15 23:50:16 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 23:50:16 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 00:09:44 Trading-Agent python[404046]: [paper_f5] ribilancio del 2026-11-16: universo 100, long 26, short 27, costo 2.42, equity 10584.77
Nov 16 00:13:58 Trading-Agent python[404046]: [paper_g1] ribilancio del 2026-11-16: universo 100, long 24, short 28, costo 1.85, equity 11044.36
Nov 16 00:18:17 Trading-Agent python[404046]: [paper_g11] ribilancio del 2026-11-16: universo 100, long 26, short 29, costo 1.61, equity 11045.54
Nov 16 00:22:37 Trading-Agent python[404046]: [paper_g1n] ribilancio del 2026-11-16: universo 100, long 24, short 28, costo 1.98, equity 11296.37
Nov 16 00:23:21 Trading-Agent python[404046]: [demo_binance] decisione G1 del 2026-11-16: 33 ordini limite sul conto, 2 rifiutati
Nov 16 00:23:53 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 00:23:53 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 00:36:51 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3249 (controllo 1116 · registro 1092 · trade 859 · rifiutati 72 · pesi 55 · selettore 19 · deriva 18 · referti 18) — quota gratuita 50000/giorno
Nov 16 00:36:51 Trading-Agent python[404046]: [learning] filtrati 28/113 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 00:36:52 Trading-Agent python[404046]: [main] pesi ricalcolati: 73 coppie strat×regime da 113 trade (30g)
Nov 16 00:36:53 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 00:36:55 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1618 ms
Nov 16 00:39:09 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 00:39:09 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 01:06:14 Trading-Agent python[404046]: [paper_f5] ordini limite del 2026-11-16: 66 eseguiti su 66, costo 2.42 (tutto a mercato 8.47)
Nov 16 01:10:44 Trading-Agent python[404046]: [paper_g1] ordini limite del 2026-11-16: 62 eseguiti su 62, costo 1.85 (tutto a mercato 6.48)
Nov 16 01:14:41 Trading-Agent python[404046]: [paper_g11] ordini limite del 2026-11-16: 64 eseguiti su 64, costo 1.61 (tutto a mercato 5.65)
Nov 16 01:19:20 Trading-Agent python[404046]: [paper_g1n] ordini limite del 2026-11-16: 62 eseguiti su 62, costo 1.98 (tutto a mercato 6.92)
Nov 16 01:37:05 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3385 (controllo 1178 · registro 1152 · trade 863 · rifiutati 76 · pesi 58 · selettore 20 · deriva 19 · referti 19) — quota gratuita 50000/giorno
Nov 16 01:37:06 Trading-Agent python[404046]: [learning] filtrati 28/112 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 01:37:06 Trading-Agent python[404046]: [main] pesi ricalcolati: 72 coppie strat×regime da 112 trade (30g)
Nov 16 01:37:07 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 01:37:09 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1748 ms
Nov 16 01:40:25 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 01:40:25 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 02:31:20 Trading-Agent python[404046]: [main] market scan...
Nov 16 02:32:50 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 16 02:33:08 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 16 02:33:54 Trading-Agent python[404046]: [scanner] 12 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 16 02:33:54 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 02:33:54 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 02:33:54 Trading-Agent python[404046]: [main] valutate 80 coin validate (80 nel registro): ['BULLAUSDT', 'CROSSUSDT', 'USELESSUSDT', 'ZECUSDT', 'PUNDIXUSDT', 'FORMUSDT', 'XMRUSDT', 'SCRUSDT', 'ENAUSDT', 'RUNEUSDT', 'HUSDT', 'GALAUSDT', 'GRASSUSDT', '1000PEPEUSDT', 'HYPEUSDT', 'TRUMPUSDT', 'STXUSDT', 'PHAUSDT', 'JTOUSDT', 'TAKEUSDT', 'VELVETUSDT', 'FLOCKUSDT', 'HEMIUSDT', 'AKTUSDT', 'TAOUSDT', '0GUSDT', 'PUMPUSDT', 'TAUSDT', '1000BONKUSDT', 'KERNELUSDT', 'JUPUSDT', 'ZORAUSDT', 'PENGUUSDT', 'BRUSDT', 'GUNUSDT', 'HUMAUSDT', 'BLESSUSDT', 'SPXUSDT', 'XVGUSDT', 'TUTUSDT', 'ASTERUSDT', 'RENDERUSDT', 'EIGENUSDT', 'BIOUSDT', 'RAYSOLUSDT', 'IDOLUSDT', 'AVAAIUSDT', 'DEXEUSDT', 'AGTUSDT', 'ARKMUSDT', 'QUSDT', 'SKYAIUSDT', 'BSVUSDT', 'BANKUSDT', 'MUBARAKUSDT', 'HOMEUSDT', 'PNUTUSDT', 'MAVIAUSDT', 'SAHARAUSDT', 'GPSUSDT', 'MYXUSDT', 'HEIUSDT', 'UBUSDT', 'AINUSDT', 'XPINUSDT', 'CATIUSDT', 'IDUSDT', 'HOLOUSDT', 'CAKEUSDT', 'HIVEUSDT', 'SYRUPUSDT', 'ALCHUSDT', 'PLUMEUSDT', 'OPENUSDT', 'PARTIUSDT', 'AIOUSDT', 'BTRUSDT', 'BMTUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 16 02:37:08 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3522 (controllo 1240 · registro 1212 · trade 868 · rifiutati 80 · pesi 61 · selettore 21 · deriva 20 · referti 20) — quota gratuita 50000/giorno
Nov 16 02:37:08 Trading-Agent python[404046]: [learning] filtrati 28/112 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 02:37:08 Trading-Agent python[404046]: [main] pesi ricalcolati: 72 coppie strat×regime da 112 trade (30g)
Nov 16 02:37:09 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 02:37:11 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1734 ms
Nov 16 02:42:08 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 02:42:08 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 03:37:35 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3659 (controllo 1302 · registro 1273 · trade 872 · rifiutati 84 · pesi 64 · selettore 22 · deriva 21 · referti 21) — quota gratuita 50000/giorno
Nov 16 03:37:35 Trading-Agent python[404046]: [learning] filtrati 28/112 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 03:37:36 Trading-Agent python[404046]: [main] pesi ricalcolati: 72 coppie strat×regime da 112 trade (30g)
Nov 16 03:37:37 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 03:37:39 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1704 ms
Nov 16 03:43:02 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 03:43:02 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
```
