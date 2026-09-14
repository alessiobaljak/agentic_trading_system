# 0049-verifica-riaggiunta-2.req

_eseguito: 2026-09-14 07:00 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 14 06:26:16 Trading-Agent python[1233965]: ============================================================
Sep 14 06:26:16 Trading-Agent python[1233965]: [optimize] 1296 coppie valutate, 0 passate in QUESTO run.
Sep 14 06:26:16 Trading-Agent python[1233965]: [optimize] REGISTRO: 0/162 crypto (0%) con strategia validata (>= 3 pass). GATE 1 in corso (0% < 35%)
Sep 14 06:26:16 Trading-Agent python[1233965]: ============================================================
Sep 14 06:26:18 Trading-Agent python[1235443]: [firebase] connesso (Firestore + RTDB)
Sep 14 06:26:19 Trading-Agent python[1235443]: [ai-hypotheses] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011Cf2rbD2ajCewrkRGEUwiR'}) -> proseguo senza AI
Sep 14 06:26:19 Trading-Agent python[1235443]: [discover] 10 semi dai quasi-passaggi del run precedente
Sep 14 06:26:19 Trading-Agent python[1235443]: [discover] 453 candidate (240 con conferme ri-validate + 103 altre, 0 tagliate su 343 note) seed=67178 2022-01-01->2026-09-14
Sep 14 06:26:20 Trading-Agent python[1235443]: [ai-universe] non disponibile (AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011Cf2rbJhtqorkyYyhBnxas'}) -> proseguo senza AI
Sep 14 06:26:20 Trading-Agent python[1235443]: [discover] 13 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (ZKUSDT, BICOUSDT, ORCAUSDT, SPXUSDT, SKYAIUSDT, HEIUSDT, TSTUSDT, NEIROUSDT, SCRUSDT, JASMYUSDT, SYRUPUSDT, SAHARAUSDT ...)
Sep 14 06:26:20 Trading-Agent python[1235443]: [discover] shard 0/1: 213/213 coin
Sep 14 06:26:20 Trading-Agent python[1235443]: [discover] 213 coin x 453 spec su 8 worker (core)
Sep 14 06:26:21 Trading-Agent python[1235595]: [backtest] dati da cache: 45271 candele (HYPEUSDT 15m)
Sep 14 06:26:22 Trading-Agent python[1235511]: [backtest] dati da cache: 92296 candele (LSKUSDT 15m)
Sep 14 06:26:23 Trading-Agent python[1235574]: [backtest] dati da cache: 164833 candele (XRPUSDT 15m)
Sep 14 06:26:23 Trading-Agent python[1235469]: [backtest] dati da cache: 164833 candele (BTCUSDT 15m)
Sep 14 06:26:23 Trading-Agent python[1235616]: [backtest] dati da cache: 164833 candele (FILUSDT 15m)
Sep 14 06:26:23 Trading-Agent python[1235490]: [backtest] dati da cache: 164833 candele (ETHUSDT 15m)
Sep 14 06:26:23 Trading-Agent python[1235553]: [backtest] dati da cache: 164833 candele (SOLUSDT 15m)
Sep 14 06:26:23 Trading-Agent python[1235532]: [backtest] dati da cache: 164833 candele (ZECUSDT 15m)
Sep 14 06:28:08 Trading-Agent python[1235595]: [backtest] dati da cache: 164833 candele (DOGEUSDT 15m)
Sep 14 06:30:07 Trading-Agent python[1235511]: [backtest] dati da cache: 46527 candele (CVCUSDT 15m)
Sep 14 06:32:22 Trading-Agent python[1235511]: [backtest] dati da cache: 164833 candele (BNBUSDT 15m)
Sep 14 06:32:56 Trading-Agent python[1235469]: [backtest] dati da cache: 118017 candele (SUIUSDT 15m)
Sep 14 06:32:59 Trading-Agent python[1235490]: [backtest] dati da cache: 17907 candele (龙虾USDT 15m)
Sep 14 06:32:59 Trading-Agent python[1235490]: [backtest] dati da cache: 57563 candele (VTHOUSDT 15m)
Sep 14 06:33:12 Trading-Agent python[1235574]: [backtest] dati da cache: 9736 candele (BTWUSDT 15m)
Sep 14 06:33:14 Trading-Agent python[1235616]: [backtest] dati da cache: 164833 candele (NEARUSDT 15m)
Sep 14 06:33:14 Trading-Agent python[1235574]: [backtest] dati da cache: 117823 candele (1000PEPEUSDT 15m)
Sep 14 06:33:19 Trading-Agent python[1235553]: [backtest] dati da cache: 99783 candele (STEEMUSDT 15m)
Sep 14 06:33:35 Trading-Agent python[1235532]: [backtest] dati da cache: 164833 candele (UNIUSDT 15m)
Sep 14 06:35:00 Trading-Agent python[1235595]: [backtest] dati da cache: 1395 candele (牛来USDT 15m)
Sep 14 06:35:02 Trading-Agent python[1235595]: [backtest] dati da cache: 104679 candele (ARKUSDT 15m)
Sep 14 06:35:25 Trading-Agent python[1235490]: [backtest] dati da cache: 164833 candele (ADAUSDT 15m)
Sep 14 06:37:41 Trading-Agent python[1235553]: [backtest] dati da cache: 164833 candele (LINKUSDT 15m)
Sep 14 06:38:09 Trading-Agent python[1235574]: [backtest] dati da cache: 41347 candele (PUMPUSDT 15m)
Sep 14 06:38:15 Trading-Agent python[1235469]: [backtest] dati da cache: 83177 candele (REZUSDT 15m)
Sep 14 06:39:25 Trading-Agent python[1235511]: [backtest] dati da cache: 35398 candele (FLOCKUSDT 15m)
Sep 14 06:39:38 Trading-Agent python[1235595]: [backtest] dati da cache: 742 candele (PONSUSDT 15m)
Sep 14 06:39:40 Trading-Agent python[1235595]: [backtest] dati da cache: 85871 candele (ENAUSDT 15m)
Sep 14 06:40:04 Trading-Agent python[1235574]: [backtest] dati da cache: 84999 candele (TAOUSDT 15m)
Sep 14 06:40:33 Trading-Agent python[1235616]: [backtest] dati da cache: 110161 candele (WLDUSDT 15m)
Sep 14 06:41:07 Trading-Agent python[1235532]: [backtest] dati da cache: 164833 candele (MTLUSDT 15m)
Sep 14 06:41:09 Trading-Agent python[1235511]: [backtest] dati da cache: 121957 candele (ARBUSDT 15m)
Sep 14 06:41:59 Trading-Agent python[1235469]: [backtest] dati da cache: 25371 candele (LITUSDT 15m)
Sep 14 06:42:00 Trading-Agent python[1235469]: [backtest] dati da cache: 51886 candele (BRUSDT 15m)
Sep 14 06:42:49 Trading-Agent python[1235490]: [backtest] dati da cache: 57933 candele (TRUMPUSDT 15m)
Sep 14 06:43:34 Trading-Agent python[1235595]: [backtest] dati da cache: 26941 candele (POWERUSDT 15m)
Sep 14 06:43:34 Trading-Agent python[1235595]: [backtest] dati da cache: 1210 candele (MARSCOINUSDT 15m)
Sep 14 06:43:37 Trading-Agent python[1235595]: [backtest] dati da cache: 164833 candele (AVAXUSDT 15m)
Sep 14 06:43:42 Trading-Agent python[1235574]: [backtest] dati da cache: 48153 candele (PUNDIXUSDT 15m)
Sep 14 06:44:22 Trading-Agent python[1235469]: [backtest] dati da cache: 37872 candele (USELESSUSDT 15m)
Sep 14 06:44:57 Trading-Agent python[1235553]: [backtest] dati da cache: 164833 candele (AAVEUSDT 15m)
Sep 14 06:45:21 Trading-Agent python[1235616]: [backtest] dati da cache: 164833 candele (LTCUSDT 15m)
Sep 14 06:45:28 Trading-Agent python[1235490]: [backtest] dati da cache: 31815 candele (LABUSDT 15m)
Sep 14 06:45:30 Trading-Agent python[1235490]: [backtest] dati da cache: 164833 candele (BCHUSDT 15m)
Sep 14 06:45:56 Trading-Agent python[1235574]: [backtest] dati da cache: 92877 candele (ONDOUSDT 15m)
Sep 14 06:46:04 Trading-Agent python[1235469]: [backtest] dati da cache: 61681 candele (RAYSOLUSDT 15m)
Sep 14 06:46:11 Trading-Agent python[1235511]: [backtest] dati da cache: 101079 candele (POWRUSDT 15m)
Sep 14 06:48:04 Trading-Agent python[1235532]: [backtest] dati da cache: 56896 candele (VVVUSDT 15m)
Sep 14 06:48:55 Trading-Agent python[1235469]: [backtest] dati da cache: 142934 candele (INJUSDT 15m)
Sep 14 06:49:51 Trading-Agent python[1235574]: [backtest] dati da cache: 87299 candele (ETHFIUSDT 15m)
Sep 14 06:50:38 Trading-Agent python[1235532]: [backtest] dati da cache: 164833 candele (DOTUSDT 15m)
Sep 14 06:50:38 Trading-Agent python[1235511]: [backtest] dati da cache: 164833 candele (DASHUSDT 15m)
Sep 14 06:50:39 Trading-Agent python[1235595]: [backtest] dati da cache: 164833 candele (XMRUSDT 15m)
Sep 14 06:52:11 Trading-Agent python[1235553]: [backtest] dati da cache: 60992 candele (PENGUUSDT 15m)
Sep 14 06:52:29 Trading-Agent python[1235490]: [backtest] dati da cache: 34513 candele (ASTERUSDT 15m)
Sep 14 06:52:30 Trading-Agent python[1235490]: [backtest] dati da cache: 29811 candele (UAIUSDT 15m)
Sep 14 06:52:31 Trading-Agent python[1235490]: [backtest] dati da cache: 33839 candele (AKEUSDT 15m)
Sep 14 06:52:34 Trading-Agent python[1235490]: [backtest] dati da cache: 164833 candele (TRXUSDT 15m)
Sep 14 06:52:35 Trading-Agent python[1235616]: [backtest] dati da cache: 164833 candele (XLMUSDT 15m)
Sep 14 06:54:03 Trading-Agent python[1235574]: [backtest] dati da cache: 164833 candele (CRVUSDT 15m)
Sep 14 06:55:17 Trading-Agent python[1235553]: [backtest] dati da cache: 136889 candele (APTUSDT 15m)
Sep 14 06:55:24 Trading-Agent python[1235469]: [backtest] dati da cache: 164833 candele (KAVAUSDT 15m)
Sep 14 06:58:33 Trading-Agent python[1235595]: [backtest] dati da cache: 164833 candele (IOSTUSDT 15m)
Sep 14 06:58:47 Trading-Agent python[1235511]: [backtest] dati da cache: 51415 candele (PAXGUSDT 15m)
Sep 14 06:59:24 Trading-Agent python[1235532]: [backtest] dati da cache: 138999 candele (ICPUSDT 15m)
Sep 14 07:00:06 Trading-Agent python[1235616]: [backtest] dati da cache: 31814 candele (RIVERUSDT 15m)
Sep 14 07:00:08 Trading-Agent python[1235616]: [backtest] dati da cache: 61680 candele (KOMAUSDT 15m)
Sep 14 07:00:13 Trading-Agent python[1235490]: [backtest] dati da cache: 37211 candele (XPLUSDT 15m)
```
