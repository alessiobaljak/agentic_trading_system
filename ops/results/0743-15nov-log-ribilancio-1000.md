# 0743-15nov-log-ribilancio-1000.req

_eseguito: 2026-11-15 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 14 19:00:38 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:01:17 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:01:56 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:02:34 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:03:14 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:03:52 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:04:31 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:05:10 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:05:49 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:05:55 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 19:06:33 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:07:13 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:07:51 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:08:30 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 19:09:32 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 19:09:32 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 19:12:58 Trading-Agent python[4153716]: [main] market scan...
Nov 14 19:14:29 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 14 19:14:46 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 14 19:15:34 Trading-Agent python[4153716]: [scanner] 5 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 14 19:15:34 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 19:15:34 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 19:15:34 Trading-Agent python[4153716]: [main] valutate 80 coin validate (80 nel registro): ['HUSDT', 'KERNELUSDT', 'IDOLUSDT', 'PARTIUSDT', 'PUMPUSDT', 'CATIUSDT', 'PENGUUSDT', 'FORMUSDT', 'SAHARAUSDT', '1000PEPEUSDT', 'HOMEUSDT', 'HOLOUSDT', 'MUBARAKUSDT', 'USELESSUSDT', 'TAOUSDT', 'XMRUSDT', 'ENAUSDT', 'HUMAUSDT', 'ZECUSDT', 'TRUMPUSDT', 'FLOCKUSDT', 'ASTERUSDT', 'HYPEUSDT', 'AKTUSDT', 'EIGENUSDT', 'RAYSOLUSDT', 'MYXUSDT', 'AGTUSDT', 'GUNUSDT', 'AIOUSDT', '1000BONKUSDT', 'IDUSDT', 'BANKUSDT', 'SYRUPUSDT', 'RENDERUSDT', 'TAKEUSDT', 'BIOUSDT', 'UBUSDT', 'TUTUSDT', 'OPENUSDT', 'RUNEUSDT', 'GRASSUSDT', 'SPXUSDT', 'GPSUSDT', 'XVGUSDT', 'PHAUSDT', 'ALCHUSDT', 'JTOUSDT', 'HIVEUSDT', 'GALAUSDT', 'ARKMUSDT', 'HEIUSDT', 'SKYAIUSDT', 'CAKEUSDT', 'DEXEUSDT', 'ZORAUSDT', 'MAVIAUSDT', 'PNUTUSDT', 'PLUMEUSDT', 'PUNDIXUSDT', 'QUSDT', 'STXUSDT', '0GUSDT', 'BRUSDT', 'TAUSDT', 'SCRUSDT', 'JUPUSDT', 'BLESSUSDT', 'VELVETUSDT', 'AINUSDT', 'HEMIUSDT', 'BSVUSDT', 'BMTUSDT', 'AVAAIUSDT', 'XPINUSDT', 'CROSSUSDT', 'BULLAUSDT', 'MITOUSDT', 'PTBUSDT', 'BTRUSDT']
Nov 14 19:59:26 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3180 (controllo 1426 · registro 1418 · trade 104 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 19:59:29 Trading-Agent python[4153716]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 19:59:29 Trading-Agent python[4153716]:   q = q.where(order_by, "<=", max_value)
Nov 14 19:59:29 Trading-Agent python[4153716]: [learning] filtrati 33/147 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 14 19:59:29 Trading-Agent python[4153716]: [main] pesi ricalcolati: 91 coppie strat×regime da 147 trade (30g)
Nov 14 19:59:31 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 19:59:33 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1884 ms
Nov 14 20:06:02 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 20:11:18 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 20:11:18 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 20:59:43 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3967 (controllo 1426 · registro 1419 · trade 889 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 20:59:43 Trading-Agent python[4153716]: [learning] filtrati 33/147 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 14 20:59:44 Trading-Agent python[4153716]: [main] pesi ricalcolati: 91 coppie strat×regime da 147 trade (30g)
Nov 14 20:59:45 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 20:59:47 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1869 ms
Nov 14 21:06:16 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 21:12:11 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 21:12:11 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 21:59:45 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3967 (controllo 1426 · registro 1419 · trade 889 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 21:59:45 Trading-Agent python[4153716]: [learning] filtrati 33/147 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 14 21:59:46 Trading-Agent python[4153716]: [main] pesi ricalcolati: 91 coppie strat×regime da 147 trade (30g)
Nov 14 21:59:47 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 21:59:49 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1898 ms
Nov 14 22:06:41 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 22:13:20 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 22:13:20 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 22:59:57 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3967 (controllo 1426 · registro 1419 · trade 889 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 22:59:57 

[... 4804 caratteri omessi (testa e coda conservate) ...]

09:14 Trading-Agent python[4153716]: [paper_g1] ribilancio del 2026-11-15: universo 100, long 25, short 26, costo 1.15, equity 11072.13
Nov 15 00:13:26 Trading-Agent python[4153716]: [paper_g11] ribilancio del 2026-11-15: universo 100, long 29, short 24, costo 1.40, equity 10981.33
Nov 15 00:17:43 Trading-Agent python[4153716]: [paper_g1n] ribilancio del 2026-11-15: universo 100, long 25, short 26, costo 1.13, equity 11299.91
Nov 15 00:18:22 Trading-Agent python[4153716]: [demo_binance] decisione G1 del 2026-11-15: 40 ordini limite sul conto demo, 1 rifiutati
Nov 15 00:18:59 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 00:18:59 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 15 01:00:12 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3827 (controllo 1364 · registro 1358 · trade 882 · rifiutati 91 · pesi 66 · deriva 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 15 01:00:12 Trading-Agent python[4153716]: [learning] filtrati 33/144 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 15 01:00:12 Trading-Agent python[4153716]: [main] pesi ricalcolati: 90 coppie strat×regime da 144 trade (30g)
Nov 15 01:00:14 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 15 01:00:16 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1854 ms
Nov 15 01:05:05 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 01:05:05 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 15 01:05:26 Trading-Agent python[4153716]: [paper_g1] ordini limite del 2026-11-15: 54 eseguiti su 54, costo 1.15 (tutto a mercato 4.01)
Nov 15 01:09:44 Trading-Agent python[4153716]: [paper_g11] ordini limite del 2026-11-15: 56 eseguiti su 57, costo 3.23 (tutto a mercato 4.91)
Nov 15 01:11:53 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 15 01:14:17 Trading-Agent python[4153716]: [paper_g1n] ordini limite del 2026-11-15: 53 eseguiti su 54, costo 2.06 (tutto a mercato 3.95)
Nov 15 01:18:39 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 02:00:34 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3825 (controllo 1364 · registro 1356 · trade 882 · rifiutati 91 · pesi 66 · deriva 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 15 02:00:34 Trading-Agent python[4153716]: [learning] filtrati 33/144 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 15 02:00:35 Trading-Agent python[4153716]: [main] pesi ricalcolati: 90 coppie strat×regime da 144 trade (30g)
Nov 15 02:00:36 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 15 02:00:38 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1501 ms
Nov 15 02:06:08 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 02:06:08 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 15 02:17:59 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 03:01:02 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3827 (controllo 1364 · registro 1358 · trade 882 · rifiutati 91 · pesi 66 · deriva 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 15 03:01:02 Trading-Agent python[4153716]: [learning] filtrati 33/141 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 15 03:01:02 Trading-Agent python[4153716]: [main] pesi ricalcolati: 88 coppie strat×regime da 141 trade (30g)
Nov 15 03:01:03 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 15 03:01:05 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1548 ms
Nov 15 03:07:24 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 03:07:24 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 15 03:13:54 Trading-Agent python[4153716]: [main] market scan...
Nov 15 03:15:22 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 15 03:15:39 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 15 03:16:27 Trading-Agent python[4153716]: [scanner] 3 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 15 03:16:27 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 03:16:27 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 15 03:16:27 Trading-Agent python[4153716]: [main] valutate 80 coin validate (80 nel registro): ['ZECUSDT', 'SKYAIUSDT', 'SPXUSDT', 'VELVETUSDT', 'AIOUSDT', 'STXUSDT', 'PUNDIXUSDT', 'HOMEUSDT', 'PENGUUSDT', 'GPSUSDT', 'TAOUSDT', 'PHAUSDT', 'HUSDT', 'JUPUSDT', 'AGTUSDT', 'SCRUSDT', 'RAYSOLUSDT', 'HYPEUSDT', 'OPENUSDT', 'XMRUSDT', 'PUMPUSDT', 'ZORAUSDT', 'JTOUSDT', 'PLUMEUSDT', 'QUSDT', 'GRASSUSDT', 'PNUTUSDT', 'UBUSDT', 'HEMIUSDT', 'USELESSUSDT', 'IDOLUSDT', 'ALCHUSDT', 'RENDERUSDT', 'XPINUSDT', 'CROSSUSDT', 'XVGUSDT', 'ENAUSDT', 'PARTIUSDT', '1000PEPEUSDT', 'CAKEUSDT', 'MUBARAKUSDT', 'TRUMPUSDT', 'TUTUSDT', 'AVAAIUSDT', 'TAKEUSDT', 'SAHARAUSDT', 'MYXUSDT', 'EIGENUSDT', 'GALAUSDT', 'ARKMUSDT', 'SYRUPUSDT', 'BLESSUSDT', 'IDUSDT', 'CATIUSDT', 'HUMAUSDT', 'KERNELUSDT', '1000BONKUSDT', 'BSVUSDT', 'MAVIAUSDT', 'AKTUSDT', 'AINUSDT', 'GUNUSDT', 'BRUSDT', 'DEXEUSDT', '0GUSDT', 'HEIUSDT', 'RUNEUSDT', 'ASTERUSDT', 'BIOUSDT', 'FLOCKUSDT', 'FORMUSDT', 'BANKUSDT', 'HOLOUSDT', 'TAUSDT', 'HIVEUSDT', 'BTRUSDT', 'BMTUSDT', 'MITOUSDT', 'PTBUSDT', 'BULLAUSDT']
Nov 15 03:18:26 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 15 04:01:33 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3827 (controllo 1364 · registro 1356 · trade 884 · rifiutati 91 · pesi 66 · deriva 22 · referti 22 · selettore 22) — quota gratuita 50000/giorno
Nov 15 04:01:33 Trading-Agent python[4153716]: [learning] filtrati 33/140 trade (esplorativi: 12 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 15)
Nov 15 04:01:33 Trading-Agent python[4153716]: [main] pesi ricalcolati: 88 coppie strat×regime da 140 trade (30g)
Nov 15 04:01:34 Trading-Agent python[4153716]: [referti] 5 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 15 04:01:37 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1751 ms
Nov 15 04:08:40 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 15 04:08:40 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 15 04:18:51 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
```
