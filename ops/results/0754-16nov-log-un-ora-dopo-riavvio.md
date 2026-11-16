# 0754-16nov-log-un-ora-dopo-riavvio.req

_eseguito: 2026-11-16 08:32 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
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
Nov 16 03:37:36 Tradi

[... 2564 caratteri omessi (testa e coda conservate) ...]

[main] pesi ricalcolati: 70 coppie strat×regime da 109 trade (30g)
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
Nov 16 07:37:43 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 16 07:38:00 Trading-Agent python[465569]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 16 07:38:47 Trading-Agent python[465569]: [scanner] 12 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 16 07:38:47 Trading-Agent python[465569]: [main] valutate 80 coin validate (80 nel registro): ['TAUSDT', 'BLESSUSDT', 'AGTUSDT', 'TAKEUSDT', 'CROSSUSDT', 'FLOCKUSDT', '1000PEPEUSDT', 'VELVETUSDT', 'HUMAUSDT', 'BULLAUSDT', '1000BONKUSDT', 'RENDERUSDT', 'SYRUPUSDT', 'XPINUSDT', 'IDOLUSDT', 'ALCHUSDT', 'ASTERUSDT', 'MUBARAKUSDT', 'BRUSDT', 'ENAUSDT', 'PUNDIXUSDT', 'BMTUSDT', 'USELESSUSDT', 'XMRUSDT', '0GUSDT', 'PUMPUSDT', 'GUNUSDT', 'TAOUSDT', 'RAYSOLUSDT', 'PNUTUSDT', 'HEIUSDT', 'PENGUUSDT', 'JUPUSDT', 'SPXUSDT', 'HYPEUSDT', 'HUSDT', 'TRUMPUSDT', 'DEXEUSDT', 'ZORAUSDT', 'SCRUSDT', 'ZECUSDT', 'PHAUSDT', 'GPSUSDT', 'OPENUSDT', 'FORMUSDT', 'AINUSDT', 'PLUMEUSDT', 'BTRUSDT', 'GALAUSDT', 'HEMIUSDT', 'KERNELUSDT', 'AKTUSDT', 'HOMEUSDT', 'EIGENUSDT', 'AVAAIUSDT', 'MYXUSDT', 'BANKUSDT', 'HIVEUSDT', 'BSVUSDT', 'BIOUSDT', 'STXUSDT', 'QUSDT', 'HOLOUSDT', 'SKYAIUSDT', 'UBUSDT', 'SAHARAUSDT', 'AIOUSDT', 'MAVIAUSDT', 'GRASSUSDT', 'TUTUSDT', 'JTOUSDT', 'IDUSDT', 'ARKMUSDT', 'XVGUSDT', 'CAKEUSDT', 'CATIUSDT', 'PARTIUSDT', 'RUNEUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 16 07:38:48 Trading-Agent python[465569]: [demo_binance] avvio: indirizzo demo-fapi.binance.com, leva 5, stop_sul_conto 0.35, capitale_nel_file 1000.0, capitale_errato None, capitale_massimo 10000.0, eventi_accesi False, filtri_del_conto_vero_del 2026-11-06, somma_pesi_massima 2.5, peso_massimo_moneta 0.6, eta_massima_decisione_ore 26, pavimento_riparti 0.65
Nov 16 07:38:49 Trading-Agent python[465569]: [conto_vero] spento: manca l'interruttore ops/conto_vero_acceso
Nov 16 07:51:16 Trading-Agent python[465569]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 16 07:51:16 Trading-Agent python[465569]:   return query.where(field_path, op_string, value)
```
