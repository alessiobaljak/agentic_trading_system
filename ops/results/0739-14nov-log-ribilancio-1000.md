# 0739-14nov-log-ribilancio-1000.req

_eseguito: 2026-11-14 04:19 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Nov 13 17:07:31 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 17:07:31 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 13 17:54:02 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3983 (registro 1435 · controllo 1426 · trade 889 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 13 17:54:02 Trading-Agent python[4153716]: [learning] filtrati 41/178 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 20)
Nov 13 17:54:03 Trading-Agent python[4153716]: [main] pesi ricalcolati: 108 coppie strat×regime da 178 trade (30g)
Nov 13 17:54:04 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 13 17:54:06 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1925 ms
Nov 13 17:59:02 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 13 18:08:03 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 18:08:03 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 13 18:54:14 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3983 (registro 1435 · controllo 1426 · trade 889 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 13 18:54:14 Trading-Agent python[4153716]: [learning] filtrati 41/178 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 20)
Nov 13 18:54:15 Trading-Agent python[4153716]: [main] pesi ricalcolati: 108 coppie strat×regime da 178 trade (30g)
Nov 13 18:54:16 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 13 18:54:18 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1644 ms
Nov 13 18:59:06 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 13 19:08:53 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 19:08:53 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 13 19:10:54 Trading-Agent python[4153716]: [main] market scan...
Nov 13 19:12:23 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 13 19:12:42 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 13 19:13:30 Trading-Agent python[4153716]: [scanner] 10 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 13 19:13:30 Trading-Agent python[4153716]: [main] valutate 80 coin validate (80 nel registro): ['IDOLUSDT', 'GUNUSDT', 'USELESSUSDT', 'GRASSUSDT', 'AIOUSDT', 'TAOUSDT', 'FORMUSDT', 'BULLAUSDT', 'MAVIAUSDT', 'PNUTUSDT', 'ZORAUSDT', 'HOMEUSDT', 'TRUMPUSDT', 'PARTIUSDT', 'QUSDT', 'AGTUSDT', 'RAYSOLUSDT', '1000PEPEUSDT', 'GPSUSDT', 'GALAUSDT', 'PUMPUSDT', 'ZECUSDT', 'ENAUSDT', 'SCRUSDT', 'FLOCKUSDT', '1000BONKUSDT', 'ASTERUSDT', 'MYXUSDT', 'HUMAUSDT', 'SYRUPUSDT', 'BTRUSDT', 'HYPEUSDT', 'OPENUSDT', 'JTOUSDT', 'PENGUUSDT', 'BRUSDT', 'AVAAIUSDT', 'XPINUSDT', 'PLUMEUSDT', 'SPXUSDT', 'RENDERUSDT', 'HUSDT', 'XMRUSDT', 'JUPUSDT', 'STXUSDT', 'TAUSDT', 'HEIUSDT', 'VELVETUSDT', 'PHAUSDT', 'PUNDIXUSDT', 'AINUSDT', 'KERNELUSDT', 'EIGENUSDT', 'IDUSDT', 'CROSSUSDT', 'ARKMUSDT', 'SAHARAUSDT', 'AKTUSDT', 'TUTUSDT', 'BLESSUSDT', 'UBUSDT', '0GUSDT', 'MUBARAKUSDT', 'TAKEUSDT', 'XVGUSDT', 'RUNEUSDT', 'BIOUSDT', 'ALCHUSDT', 'CATIUSDT', 'SKYAIUSDT', 'HOLOUSDT', 'DEXEUSDT', 'HIVEUSDT', 'BANKUSDT', 'HEMIUSDT', 'CAKEUSDT', 'BSVUSDT', 'MITOUSDT', 'PTBUSDT', 'BMTUSDT']
Nov 13 19:24:06 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 19:24:06 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 13 19:54:27 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3198 (registro 1437 · controllo 1426 · trade 103 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 13 19:54:30 Trading-Agent python[4153716]: /root/agentic_trading_system/bot/core/firebase_client.py:525: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 19:54:30 Trading-Agent python[4153716]:   q = q.where(order_by, "<=", max_value)
Nov 13 19:54:30 Trading-Agent python[4153716]: [learning] filtrati 41/177 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 20)
Nov 13 19:54:30 Trading-Agent python[4153716]: [main] pesi ricalcolati: 108 coppie strat×regime da 177 trade (30g)
Nov 13 19:54:32 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 13 19:54:34 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 2030 ms
Nov 13 19:59:31 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 13 20:09:57 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 20:09:57 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 13 20:54:31 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3982 (registro 1437 · controllo 1426 · trade 887 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 13 20:54:31 Trading-Agent python[4153716]: [learning] filtrati 41/176 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 20)
Nov 13 20:54:31 Trading-Agent python[4153716]: [main] pesi ricalcolati: 107 coppie strat×regime da 176 trade (30g)
Nov 13 20:54:33 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 13 20:54:35 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1818 ms
Nov 13 20:55:09 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 13 20:55:09 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 13 21:54:43 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3980 (registro 1436 · controllo 1426 · trade 886 · rifiutati 94 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 13 21:54:43 Trading-Agent python[4153716]: [learning] filtrati 40/175 trade (esplorativi: 15 · external_exit: 4 · short_duration: 

[... 7376 caratteri omessi (testa e coda conservate) ...]

inance] decisione G1 del 2026-11-14: 6 ordini limite sul conto demo, 1 rifiutati
Nov 14 00:18:42 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 00:18:42 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 00:55:05 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3981 (registro 1436 · controllo 1426 · trade 886 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 00:55:06 Trading-Agent python[4153716]: [learning] filtrati 40/172 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 19)
Nov 14 00:55:06 Trading-Agent python[4153716]: [main] pesi ricalcolati: 105 coppie strat×regime da 172 trade (30g)
Nov 14 00:55:07 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 00:55:09 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1698 ms
Nov 14 01:04:32 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 01:04:32 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 01:06:01 Trading-Agent python[4153716]: [paper_g1] ordini limite del 2026-11-14: 53 eseguiti su 53, costo 0.34 (tutto a mercato 1.20)
Nov 14 01:09:55 Trading-Agent python[4153716]: [paper_g11] ordini limite del 2026-11-14: 53 eseguiti su 55, costo 1.58 (tutto a mercato 3.46)
Nov 14 01:14:11 Trading-Agent python[4153716]: [paper_g1n] ordini limite del 2026-11-14: 53 eseguiti su 53, costo 0.37 (tutto a mercato 1.30)
Nov 14 01:33:51 Trading-Agent python[4153716]: [telegram] invio fallito: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=8)
Nov 14 01:55:20 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3983 (registro 1437 · controllo 1426 · trade 887 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 01:55:20 Trading-Agent python[4153716]: [learning] filtrati 40/171 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 19)
Nov 14 01:55:20 Trading-Agent python[4153716]: [main] pesi ricalcolati: 104 coppie strat×regime da 171 trade (30g)
Nov 14 01:55:22 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 01:55:24 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1706 ms
Nov 14 02:00:50 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 02:05:35 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 02:05:35 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 02:55:31 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3984 (registro 1437 · controllo 1426 · trade 888 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 02:55:31 Trading-Agent python[4153716]: [learning] filtrati 39/164 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 18)
Nov 14 02:55:32 Trading-Agent python[4153716]: [main] pesi ricalcolati: 99 coppie strat×regime da 164 trade (30g)
Nov 14 02:55:33 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 02:55:35 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1755 ms
Nov 14 03:00:53 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 03:06:31 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 03:06:31 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 03:11:50 Trading-Agent python[4153716]: [main] market scan...
Nov 14 03:13:20 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=MITOUSDT
Nov 14 03:13:37 Trading-Agent python[4153716]: [price_agent] GET /fapi/v1/openInterest fallito: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/openInterest?symbol=PTBUSDT
Nov 14 03:14:26 Trading-Agent python[4153716]: [scanner] 8 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Nov 14 03:14:26 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 03:14:26 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
Nov 14 03:14:26 Trading-Agent python[4153716]: [main] valutate 80 coin validate (80 nel registro): ['HUSDT', 'BULLAUSDT', 'ASTERUSDT', 'USELESSUSDT', 'HYPEUSDT', '1000PEPEUSDT', 'CATIUSDT', 'TRUMPUSDT', 'ZECUSDT', 'AIOUSDT', 'GUNUSDT', 'IDOLUSDT', 'ENAUSDT', 'PENGUUSDT', 'SPXUSDT', 'AINUSDT', 'FLOCKUSDT', 'SKYAIUSDT', 'QUSDT', 'HUMAUSDT', 'HOLOUSDT', '1000BONKUSDT', 'TUTUSDT', 'JUPUSDT', 'JTOUSDT', 'STXUSDT', 'RAYSOLUSDT', 'AGTUSDT', 'EIGENUSDT', 'HEMIUSDT', 'PNUTUSDT', 'BSVUSDT', 'PLUMEUSDT', 'BTRUSDT', 'DEXEUSDT', 'GALAUSDT', 'PUNDIXUSDT', 'TAOUSDT', 'BANKUSDT', 'FORMUSDT', 'SYRUPUSDT', 'BIOUSDT', 'CAKEUSDT', 'VELVETUSDT', 'PUMPUSDT', 'GRASSUSDT', 'ALCHUSDT', 'AKTUSDT', 'IDUSDT', 'ARKMUSDT', 'OPENUSDT', 'RENDERUSDT', 'ZORAUSDT', 'BMTUSDT', 'CROSSUSDT', 'MYXUSDT', 'UBUSDT', 'SAHARAUSDT', 'HEIUSDT', 'MAVIAUSDT', 'XMRUSDT', 'PARTIUSDT', 'TAUSDT', '0GUSDT', 'PHAUSDT', 'AVAAIUSDT', 'GPSUSDT', 'HOMEUSDT', 'TAKEUSDT', 'RUNEUSDT', 'BLESSUSDT', 'BRUSDT', 'SCRUSDT', 'HIVEUSDT', 'XVGUSDT', 'XPINUSDT', 'MUBARAKUSDT', 'KERNELUSDT', 'MITOUSDT', 'PTBUSDT']
Nov 14 03:55:33 Trading-Agent python[4153716]: [firebase] letture ultime 24 h: 3986 (registro 1438 · controllo 1426 · trade 889 · rifiutati 95 · pesi 69 · deriva 23 · referti 23 · selettore 23) — quota gratuita 50000/giorno
Nov 14 03:55:33 Trading-Agent python[4153716]: [learning] filtrati 39/162 trade (esplorativi: 15 · external_exit: 4 · short_duration: 2 · wrong_timeframe: 18)
Nov 14 03:55:34 Trading-Agent python[4153716]: [main] pesi ricalcolati: 99 coppie strat×regime da 162 trade (30g)
Nov 14 03:55:35 Trading-Agent python[4153716]: [referti] 7 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_0aa0d29c: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3) | gen_0aa0d29c: solo_long — short 3/3 persi (campione 3) | gen_4c6df481: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 4 (campione 3) | gen_4c6df481: solo_long — short 4/4 persi (campione 4) | gen_be64073c: conferma_trend — 3 perdite controtrend (campione 3) | gen_be64073c: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3) | gen_f311acf9: solo_long — short 3/3 persi (campione 3)
Nov 14 03:55:37 Trading-Agent python[4153716]: [controllo] pubblicato: sistema verde, paper giallo, 3 anomalie, 1916 ms
Nov 14 04:01:05 Trading-Agent python[4153716]: [demo_binance] posizioni diverse da quelle volute: ['龙虾USDT']
Nov 14 04:07:51 Trading-Agent python[4153716]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Nov 14 04:07:51 Trading-Agent python[4153716]:   return query.where(field_path, op_string, value)
```
