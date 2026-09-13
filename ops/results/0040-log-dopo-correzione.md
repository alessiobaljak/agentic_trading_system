# 0040-log-dopo-correzione.req

_eseguito: 2026-09-13 06:30 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.8s

```
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] KAITOUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] XTZUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] PARTIUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] EDENUSDT: storia insufficiente, saltato
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] PIEVERSEUSDT: storia insufficiente, saltato
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] RUNEUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] BIGTIMEUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] ORCAUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] TUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] GRTUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [optimize] HEIUSDT: 8 coppie, 0 passate
Sep 13 06:12:27 Trading-Agent python[1184646]: [autopsy] 0/1264 passate · muoiono su: total_return 1123 · recovery 77 · regime 35 · consistency 16 · pf_ex_top 7
Sep 13 06:12:27 Trading-Agent python[1184646]: [autopsy] quasi-passaggi (un solo criterio, di poco): 2
Sep 13 06:12:28 Trading-Agent python[1184646]: ============================================================
Sep 13 06:12:28 Trading-Agent python[1184646]: [optimize] 1264 coppie valutate, 0 passate in QUESTO run.
Sep 13 06:12:28 Trading-Agent python[1184646]: [optimize] REGISTRO: 0/158 crypto (0%) con strategia validata (>= 3 pass). GATE 1 in corso (0% < 35%)
Sep 13 06:12:28 Trading-Agent python[1184646]: ============================================================
Sep 13 06:12:31 Trading-Agent python[1185394]: [firebase] connesso (Firestore + RTDB)
Sep 13 06:12:32 Trading-Agent python[1185394]: [ai-hypotheses] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011CezwjLjyN4Gfuxvx1Ednq'}) -> proseguo senza AI
Sep 13 06:12:32 Trading-Agent python[1185394]: [discover] 10 semi dai quasi-passaggi del run precedente
Sep 13 06:12:32 Trading-Agent python[1185394]: [discover] 439 candidate (219 con conferme ri-validate + 110 altre, 0 tagliate su 329 note) seed=79950 2022-01-01->2026-09-13
Sep 13 06:12:33 Trading-Agent python[1185394]: [ai-universe] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011CezwjSJbPSDDrth8BwzVB'}) -> proseguo senza AI
Sep 13 06:12:33 Trading-Agent python[1185394]: [discover] shard 0/1: 200/200 coin
Sep 13 06:12:33 Trading-Agent python[1185394]: [discover] 200 coin x 439 spec su 8 worker (core)
Sep 13 06:12:34 Trading-Agent python[1185526]: [backtest] dati da cache: 17715 candele (龙虾USDT 15m)
Sep 13 06:12:35 Trading-Agent python[1185526]: [backtest] dati da cache: 45079 candele (HYPEUSDT 15m)
Sep 13 06:12:35 Trading-Agent python[1185568]: [backtest] dati da cache: 57371 candele (VTHOUSDT 15m)
Sep 13 06:12:35 Trading-Agent python[1185463]: [backtest] dati da cache: 92296 candele (LSKUSDT 15m)
Sep 13 06:12:36 Trading-Agent python[1185484]: [backtest] dati da cache: 164641 candele (ZECUSDT 15m)
Sep 13 06:12:36 Trading-Agent python[1185505]: [backtest] dati da cache: 164641 candele (SOLUSDT 15m)
Sep 13 06:12:36 Trading-Agent python[1185547]: [backtest] dati da cache: 164641 candele (XRPUSDT 15m)
Sep 13 06:12:36 Trading-Agent python[1185421]: [backtest] dati da cache: 164641 candele (ETHUSDT 15m)
Sep 13 06:12:37 Trading-Agent python[1185442]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:14:28 Trading-Agent python[1185526]: [backtest] dati da cache: 1203 candele (牛来USDT 15m)
Sep 13 06:14:30 Trading-Agent python[1185526]: [backtest] dati da cache: 164641 candele (BNBUSDT 15m)
Sep 13 06:15:06 Trading-Agent python[1185568]: [backtest] dati da cache: 164641 candele (DOGEUSDT 15m)
Sep 13 06:16:43 Trading-Agent python[1185463]: [backtest] dati da cache: 164641 candele (UNIUSDT 15m)
Sep 13 06:19:45 Trading-Agent python[1185421]: [backtest] dati da cache: 29811 candele (UAIUSDT 15m)
Sep 13 06:19:46 Trading-Agent python[1185421]: [backtest] dati da cache: 35398 candele (FLOCKUSDT 15m)
Sep 13 06:19:48 Trading-Agent python[1185442]: [backtest] dati da cache: 117825 candele (SUIUSDT 15m)
Sep 13 06:19:50 Trading-Agent python[1185547]: [backtest] dati da cache: 41155 candele (PUMPUSDT 15m)
Sep 13 06:19:56 Trading-Agent python[1185505]: [backtest] dati da cache: 31623 candele (LABUSDT 15m)
Sep 13 06:19:59 Trading-Agent python[1185505]: [backtest] dati da cache: 164641 candele (NEARUSDT 15m)
Sep 13 06:20:39 Trading-Agent python[1185484]: [backtest] dati da cache: 117631 candele (1000PEPEUSDT 15m)
Sep 13 06:21:29 Trading-Agent python[1185421]: [backtest] dati da cache: 59275 candele (GRIFFAINUSDT 15m)
Sep 13 06:21:43 Trading-Agent python[1185547]: [backtest] dati da cache: 61489 candele (RAYSOLUSDT 15m)
Sep 13 06:22:05 Trading-Agent python[1185526]: [backtest] dati da cache: 87107 candele (ETHFIUSDT 15m)
Sep 13 06:22:42 Trading-Agent python[1185568]: [backtest] dati da cache: 550 candele (PONSUSDT 15m)
Sep 13 06:22:43 Trading-Agent python[1185568]: [backtest] dati da cache: 100887 candele (POWRUSDT 15m)
Sep 13 06:24:10 Trading-Agent python[1185421]: [backtest] dati da cache: 164641 candele (ADAUSDT 15m)
Sep 13 06:24:19 Trading-Agent python[1185463]: [backtest] dati da cache: 31622 candele (RIVERUSDT 15m)
Sep 13 06:24:21 Trading-Agent python[1185463]: [backtest] dati da cache: 85679 candele (ENAUSDT 15m)
Sep 13 06:24:48 Trading-Agent python[1185547]: [backtest] dati da cache: 37680 candele (USELESSUSDT 15m)
Sep 13 06:25:29 Trading-Agent python[1185442]: [backtest] dati da cache: 36927 candele (WLFIUSDT 15m)
Sep 13 06:26:03 Trading-Agent python[1185484]: [backtest] dati da cache: 109969 candele (WLDUSDT 15m)
Sep 13 06:26:21 Trading-Agent python[1185526]: [backtest] dati da cache: 1018 candele (MARSCOINUSDT 15m)
Sep 13 06:26:24 Trading-Agent python[1185526]: [backtest] dati da cache: 99783 candele (STEEMUSDT 15m)
Sep 13 06:26:35 Trading-Agent python[1185547]: [backtest] dati da cache: 22503 candele (我踏马来了USDT 15m)
Sep 13 06:26:38 Trading-Agent python[1185547]: [backtest] dati da cache: 164641 candele (LINKUSDT 15m)
Sep 13 06:27:13 Trading-Agent python[1185442]: [backtest] dati da cache: 82985 candele (REZUSDT 15m)
Sep 13 06:27:33 Trading-Agent python[1185568]: [backtest] dati da cache: 121765 candele (ARBUSDT 15m)
Sep 13 06:27:42 Trading-Agent python[1185505]: [backtest] dati da cache: 84807 candele (TAOUSDT 15m)
Sep 13 06:28:26 Trading-Agent python[1185463]: [backtest] dati da cache: 33647 candele (AKEUSDT 15m)
Sep 13 06:28:29 Trading-Agent python[1185463]: [backtest] dati da cache: 164641 candele (IOSTUSDT 15m)
Sep 13 06:28:41 Trading-Agent systemd[1]: trading-optimizer.service: Failed with result 'signal'.
Sep 13 06:28:41 Trading-Agent systemd[1]: Stopped trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Sep 13 06:28:41 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 7h 4min 15.035s CPU time, 14.5G memory peak, 0B memory swap peak.
Sep 13 06:28:41 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Sep 13 06:28:42 Trading-Agent python[1186917]: [firebase] connesso (Firestore + RTDB)
Sep 13 06:28:43 Trading-Agent python[1186917]: [optimize] universo: top 200 per volume -> 200 coin
Sep 13 06:28:43 Trading-Agent python[1186917]: [optimize] shard 0/1: 200/200 coin
Sep 13 06:28:43 Trading-Agent python[1186917]: [optimize] 200 coin su 8 worker (core)
Sep 13 06:28:46 Trading-Agent python[1186957]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186958]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186963]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186956]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186962]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186961]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186960]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
Sep 13 06:28:46 Trading-Agent python[1186959]: [backtest] dati da cache: 164641 candele (BTCUSDT 15m)
```
