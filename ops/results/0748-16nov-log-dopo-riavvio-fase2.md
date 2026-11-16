# 0748-16nov-log-dopo-riavvio-fase2.req

_eseguito: 2026-11-16 07:37 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 15 22:33:31 Trading-Agent python[404046]: [scanner] 10 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 15 22:33:31 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 22:33:31 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 22:33:31 Trading-Agent python[404046]: [main] valutate 80 coin validate (80 nel registro): ['PHAUSDT', 'ALCHUSDT', 'GRASSUSDT', 'RAYSOLUSDT', 'CROSSUSDT', 'XMRUSDT', 'AINUSDT', 'TAOUSDT', 'PUMPUSDT', 'AIOUSDT', 'HYPEUSDT', 'AVAAIUSDT', 'ZECUSDT', 'TUTUSDT', 'HUSDT', 'TRUMPUSDT', 'CAKEUSDT', '1000PEPEUSDT', 'JTOUSDT', 'JUPUSDT', 'HEMIUSDT', 'GUNUSDT', 'SKYAIUSDT', 'RENDERUSDT', 'BIOUSDT', 'IDOLUSDT', 'PENGUUSDT', 'SYRUPUSDT', 'AKTUSDT', 'QUSDT', 'ENAUSDT', 'SPXUSDT', 'AGTUSDT', 'MAVIAUSDT', 'BTRUSDT', 'BLESSUSDT', 'ASTERUSDT', 'HOMEUSDT', 'USELESSUSDT', 'STXUSDT', 'MYXUSDT', 'SCRUSDT', '1000BONKUSDT', 'BANKUSDT', 'GALAUSDT', 'ZORAUSDT', 'HEIUSDT', 'OPENUSDT', '0GUSDT', 'TAUSDT', 'EIGENUSDT', 'DEXEUSDT', 'XVGUSDT', 'PLUMEUSDT', 'XPINUSDT', 'IDUSDT', 'FLOCKUSDT', 'ARKMUSDT', 'BSVUSDT', 'VELVETUSDT', 'KERNELUSDT', 'SAHARAUSDT', 'BMTUSDT', 'MUBARAKUSDT', 'PARTIUSDT', 'PUNDIXUSDT', 'HIVEUSDT', 'CATIUSDT', 'GPSUSDT', 'FORMUSDT', 'HOLOUSDT', 'HUMAUSDT', 'BRUSDT', 'TAKEUSDT', 'UBUSDT', 'PNUTUSDT', 'MITOUSDT', 'PTBUSDT', 'BULLAUSDT', 'RUNEUSDT']
Nov 15 22:36:36 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 2991 (controllo 992 · registro 984 · trade 852 · rifiutati 65 · pesi 49 · selettore 17 · deriva 16 · referti 16) — quota gratuita 50000/giorno
Nov 15 22:36:36 Trading-Agent python[404046]: [learning] filtrati 28/114 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 15 22:36:37 Trading-Agent python[404046]: [main] pesi ricalcolati: 73 coppie strat×regime da 114 trade (30g)
Nov 15 22:36:38 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 15 22:36:40 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1790 ms
Nov 15 22:49:19 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 22:49:19 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 15 23:23:40 Trading-Agent python[404046]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 23:36:39 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3128 (controllo 1054 · registro 1045 · trade 856 · rifiutati 69 · pesi 52 · selettore 18 · deriva 17 · referti 17) — quota gratuita 50000/giorno
Nov 15 23:36:39 Trading-Agent python[404046]: [learning] filtrati 28/114 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
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
Nov 16 02:33:54 Trading-Agent python[404046]: [main] valutate 80 coin validate (80 nel registro): ['BULLAUSDT', 'CROSSUSDT', 'USELESSUSDT', 'ZECUSDT', 'PUNDIXUSDT', 'FORMUSDT', 'XMRUSDT', 'SCRUSDT', 'ENAUSDT', 'RUNEUSDT', 'HUSDT', 'GALAUSDT', 'GRASSUSDT', '1000PEPEUSDT', 'HYPEUSDT', 'TRUMPUSDT', 'STXUSDT', 'PHAUSDT', 'JTOUSDT', 'TAKEUSDT', 'VELVETUSDT', 'FLOCKUSDT', 

[... 2481 caratteri omessi (testa e coda conservate) ...]

nt python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 03:37:39 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1704 ms
Nov 16 03:43:02 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 03:43:02 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 04:37:44 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3798 (controllo 1364 · registro 1335 · trade 877 · rifiutati 88 · pesi 67 · selettore 23 · deriva 22 · referti 22) — quota gratuita 50000/giorno
Nov 16 04:37:44 Trading-Agent python[404046]: [learning] filtrati 28/110 trade (esplorativi: 10 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 04:37:45 Trading-Agent python[404046]: [main] pesi ricalcolati: 70 coppie strat×regime da 110 trade (30g)
Nov 16 04:37:46 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 04:37:48 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1730 ms
Nov 16 04:43:30 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 04:43:30 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 05:38:13 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3938 (controllo 1426 · registro 1398 · trade 882 · rifiutati 92 · pesi 70 · selettore 24 · deriva 23 · referti 23) — quota gratuita 50000/giorno
Nov 16 05:38:13 Trading-Agent python[404046]: [learning] filtrati 27/109 trade (esplorativi: 9 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 05:38:14 Trading-Agent python[404046]: [main] pesi ricalcolati: 70 coppie strat×regime da 109 trade (30g)
Nov 16 05:38:15 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 05:38:17 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1730 ms
Nov 16 05:44:31 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 05:44:31 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 06:31:38 Trading-Agent python[404046]: [main] market scan...
Nov 16 06:33:06 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 16 06:33:23 Trading-Agent python[404046]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 16 06:34:10 Trading-Agent python[404046]: [scanner] 12 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 16 06:34:10 Trading-Agent python[404046]: [main] valutate 80 coin validate (80 nel registro): ['TAUSDT', 'XMRUSDT', 'USELESSUSDT', 'PENGUUSDT', 'IDOLUSDT', 'BRUSDT', '1000BONKUSDT', 'TAOUSDT', 'QUSDT', 'ASTERUSDT', 'BMTUSDT', 'AGTUSDT', 'PUMPUSDT', 'TAKEUSDT', 'HYPEUSDT', 'HOLOUSDT', 'ENAUSDT', 'JUPUSDT', 'HUSDT', 'CROSSUSDT', 'RENDERUSDT', 'MYXUSDT', 'BULLAUSDT', 'AINUSDT', 'MUBARAKUSDT', '1000PEPEUSDT', 'HEIUSDT', 'SPXUSDT', 'UBUSDT', 'HOMEUSDT', 'XPINUSDT', '0GUSDT', 'ZECUSDT', 'STXUSDT', 'AVAAIUSDT', 'RAYSOLUSDT', 'AKTUSDT', 'GUNUSDT', 'EIGENUSDT', 'IDUSDT', 'TRUMPUSDT', 'OPENUSDT', 'HEMIUSDT', 'HIVEUSDT', 'SKYAIUSDT', 'BIOUSDT', 'GPSUSDT', 'DEXEUSDT', 'BANKUSDT', 'MAVIAUSDT', 'PLUMEUSDT', 'BLESSUSDT', 'FLOCKUSDT', 'ARKMUSDT', 'PUNDIXUSDT', 'VELVETUSDT', 'TUTUSDT', 'ZORAUSDT', 'PARTIUSDT', 'HUMAUSDT', 'XVGUSDT', 'CATIUSDT', 'AIOUSDT', 'BSVUSDT', 'ALCHUSDT', 'SAHARAUSDT', 'GALAUSDT', 'JTOUSDT', 'GRASSUSDT', 'BTRUSDT', 'SYRUPUSDT', 'KERNELUSDT', 'PHAUSDT', 'PNUTUSDT', 'FORMUSDT', 'CAKEUSDT', 'SCRUSDT', 'MITOUSDT', 'PTBUSDT', 'RUNEUSDT']
Nov 16 06:38:25 Trading-Agent python[404046]: [firebase] letture ultime 24 h: 3180 (controllo 1426 · registro 1421 · trade 102 · rifiutati 93 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 16 06:38:25 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 06:38:25 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 06:38:27 Trading-Agent python[404046]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 06:38:27 Trading-Agent python[404046]:   q = q.where(order_by, "<=", max_value)
Nov 16 06:38:28 Trading-Agent python[404046]: [learning] filtrati 27/109 trade (esplorativi: 9 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 06:38:28 Trading-Agent python[404046]: [main] pesi ricalcolati: 70 coppie strat×regime da 109 trade (30g)
Nov 16 06:38:29 Trading-Agent python[404046]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 06:38:31 Trading-Agent python[404046]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1881 ms
Nov 16 06:45:40 Trading-Agent python[404046]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 06:45:40 Trading-Agent python[404046]:   return query.where(field_path, op_string, value)
Nov 16 07:36:02 Trading-Agent systemd[1]: Stopping trading-bot.service - Agentic Trading Bot...
Nov 16 07:36:02 Trading-Agent systemd[1]: trading-bot.service: Deactivated successfully.
Nov 16 07:36:02 Trading-Agent systemd[1]: Stopped trading-bot.service - Agentic Trading Bot.
Nov 16 07:36:02 Trading-Agent systemd[1]: trading-bot.service: Consumed 11min 7.366s CPU time.
Nov 16 07:36:02 Trading-Agent systemd[1]: Started trading-bot.service - Agentic Trading Bot.
Nov 16 07:36:04 Trading-Agent python[465569]: [config] ambiente: DRY_RUN=True, BINANCE_TESTNET=False, BACKTEST_PARITY=True
Nov 16 07:36:04 Trading-Agent python[465569]: [firebase] connesso (Firestore + RTDB)
Nov 16 07:36:05 Trading-Agent python[465569]: [main] avvio bot @ 2026-11-16T07:36:05.868778+00:00 DRY_RUN=True
Nov 16 07:36:08 Trading-Agent python[465569]: [main] equity riconciliata: 817.25 (base 1000.00 + realizzato -182.75 + fette aperte +0.00)
Nov 16 07:36:08 Trading-Agent python[465569]: [main] versione dell'avvio: commit 884b9b1a, config a3508539a199
Nov 16 07:36:08 Trading-Agent python[465569]: [main] cooldown ricaricati: 0 coin, 0 strategie in panchina (spenta in parita': non si applica)
Nov 16 07:36:08 Trading-Agent python[465569]: [selettore] modello caricato: 150015 righe, soglia 0.40, verdetto NON BATTE, stato ombra, generato 2026-10-12T17:49:35.922866+00:00 -> solo ombra, non decide
Nov 16 07:36:09 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 07:36:09 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
Nov 16 07:36:09 Trading-Agent python[465569]: [firebase] letture ultime 24 h: 792 (trade 784 · registro 5 · pesi 1 · rifiutati 1 · selettore 1) — quota gratuita 50000/giorno
Nov 16 07:36:09 Trading-Agent python[465569]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 07:36:09 Trading-Agent python[465569]:   q = q.where(order_by, "<=", max_value)
Nov 16 07:36:09 Trading-Agent python[465569]: [learning] filtrati 27/109 trade (esplorativi: 9 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 12)
Nov 16 07:36:09 Trading-Agent python[465569]: [main] pesi ricalcolati: 70 coppie strat×regime da 109 trade (30g)
Nov 16 07:36:10 Trading-Agent python[465569]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3)
Nov 16 07:36:12 Trading-Agent python[465569]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1552 ms
Nov 16 07:36:12 Trading-Agent python[465569]: [giorni] riga del 2026-11-15: cicli None/96, aperti None, rifiutati None, riavvii 1
Nov 16 07:36:15 Trading-Agent python[465569]: [main] market scan...
```
