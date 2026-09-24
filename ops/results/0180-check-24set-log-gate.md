# 0180-check-24set-log-gate.req

_eseguito: 2026-09-24 06:13 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.6s

```
Sep 24 06:02:07 Trading-Agent python[1622398]: [ai-hypotheses] non disponibile (NotFoundError: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-opus-4.8 was not found. Did you mean claude-opus-4-8?'}, 'request_id': 'req_011CfMkqMueCTcPqShR3S7Mj'}) -> proseguo senza AI
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] rivalutazione completa: 470 spec note su 522
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] semi: 24 da coin NON coperte (su 27 gia' coperte)
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] 30 semi dai quasi-passaggi del run precedente
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] 89 candidate (470 con conferme ri-validate + 0 altre, 52 tagliate su 522 note) seed=29725 2022-01-01->2026-09-24
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] universo RISTRETTO a 5 coin (--symbols)
Sep 24 06:02:08 Trading-Agent python[1622398]: [ai-universe] non disponibile (NotFoundError: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-opus-4.8 was not found. Did you mean claude-opus-4-8?'}, 'request_id': 'req_011CfMkqRNk7SGqTGrbgRmnz'}) -> proseguo senza AI
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] shard 0/1: 5/5 coin
Sep 24 06:02:08 Trading-Agent python[1622398]: [discover] 5 coin x 89 spec su 8 worker (core)
Sep 24 06:02:08 Trading-Agent python[1622398]: [paper] 44 trade chiusi -> scala candidata dal vissuto: [0.75, 1.5, 2.25] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 24 06:02:09 Trading-Agent python[1622478]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622457]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622436]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622583]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622541]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622562]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622499]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:09 Trading-Agent python[1622520]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:33 Trading-Agent python[1622478]: [backtest] dati da cache: 41425 candele (BTCUSDT 1h)
Sep 24 06:02:33 Trading-Agent python[1622583]: [backtest] dati da cache: 41425 candele (ETHUSDT 1h)
Sep 24 06:02:33 Trading-Agent python[1622436]: [backtest] dati da cache: 41425 candele (SOLUSDT 1h)
Sep 24 06:02:33 Trading-Agent python[1622541]: [backtest] dati da cache: 41425 candele (ADAUSDT 1h)
Sep 24 06:02:34 Trading-Agent python[1622457]: [backtest] dati da cache: 41425 candele (BCHUSDT 1h)
Sep 24 06:03:11 Trading-Agent python[1622398]: [discover] ADAUSDT: 1 coppie passate ✅
Sep 24 06:03:11 Trading-Agent python[1622398]: [selettore] 165 righe (1 coppie) -> data/selettore/2026-09-24_1h.jsonl
Sep 24 06:03:12 Trading-Agent python[1622398]: [autopsy] 1/445 passate · muoiono su: total_return 283 · recovery 79 · trades 33 · regime 28 · consistency 13
Sep 24 06:03:12 Trading-Agent python[1622398]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 0
Sep 24 06:03:12 Trading-Agent python[1622398]: [discover] GIRO FINITO in 0h 1m (445 valutazioni, 1 passate)
Sep 24 06:03:12 Trading-Agent python[1622398]: ============================================================
Sep 24 06:03:12 Trading-Agent python[1622398]: [discover] 445 valutazioni, 1 coppie nuove passate in QUESTO run.
Sep 24 06:03:12 Trading-Agent python[1622398]: [discover] coppie validate totali nel registro (base+generate): 59
Sep 24 06:03:12 Trading-Agent python[1622398]: ============================================================
Sep 24 06:03:13 Trading-Agent python[1622360]: [optimize] passata extra finita in 1 min (codice 0)
Sep 24 06:03:15 Trading-Agent python[1622640]: [firebase] connesso (Firestore + RTDB)
Sep 24 06:03:15 Trading-Agent python[1622640]: [discover] prove del paper passate all'AI:
Sep 24 06:03:15 Trading-Agent python[1622640]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 24 06:03:15 Trading-Agent python[1622640]: - PAPER (vissuto, 44 trade chiusi): profit factor 0.601 contro 1.885 promesso dal gate.
Sep 24 06:03:15 Trading-Agent python[1622640]: - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 24 06:03:15 Trading-Agent python[1622640]: - Direzione long: 18 trade, 6 vinti, PnL -16.28.
Sep 24 06:03:15 Trading-Agent python[1622640]: - Direzione short: 26 trade, 10 vinti, PnL -32.87.
Sep 24 06:03:15 Trading-Agent python[1622640]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su trades 6 · total_return 1207 · holdout 1 · recovery 64.
Sep 24 06:03:16 Trading-Agent python[1622640]: [ai-hypotheses] non disponibile (NotFoundError: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-opus-4.8 was not found. Did you mean claude-opus-4-8?'}, 'request_id': 'req_011CfMkvRpfqrcGa3pe3Junk'}) -> proseguo senza AI
Sep 24 06:03:16 Trading-Agent python[1622640]: [discover] 2 varianti dai referti del paper (B8): gen_ba3a671f -> gen_54d1beed (solo_short) · gen_fa304106 -> gen_9998083f (solo_long)
Sep 24 06:03:16 Trading-Agent python[1622640]: [discover] rivalutazione solo urgenti: 223 spec note su 522
Sep 24 06:03:17 Trading-Agent python[1622640]: [discover] 1 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Sep 24 06:03:17 Trading-Agent python[1622640]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 24 06:03:17 Trading-Agent python[1622640]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 24 06:03:17 Trading-Agent python[1622640]: [discover] 352 candidate (470 con conferme ri-validate + -247 altre, 299 tagliate su 522 note) seed=29794 2022-01-01->2026-09-24
Sep 24 06:03:18 Trading-Agent python[1622640]: [ai-universe] non disponibile (NotFoundError: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-opus-4.8 was not found. Did you mean claude-opus-4-8?'}, 'request_id': 'req_011CfMkvZ9xKiPmcpnqHKhVB'}) -> proseguo senza AI
Sep 24 06:03:18 Trading-Agent python[1622640]: [discover] 66 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (BICOUSDT, SKYAIUSDT, HEIUSDT, TSTUSDT, JASMYUSDT, SCRUSDT, SYRUPUSDT, BULLAUSDT, MITOUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT ...)
Sep 24 06:03:18 Trading-Agent python[1622640]: [discover] maturazione: 83 coin a un passo dalla validazione (mai tagliate) + 81 con una conferma · 0 tagliate dalla coda
Sep 24 06:03:18 Trading-Agent python[1622640]: [discover] shard 0/1: 266/266 coin
Sep 24 06:03:18 Trading-Agent python[1622640]: [discover] 266 coin x 352 spec su 8 worker (core)
Sep 24 06:03:18 Trading-Agent python[1622640]: [paper] 44 trade chiusi -> scala candidata dal vissuto: [0.75, 1.5, 2.25] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 24 06:03:20 Trading-Agent python[1622763]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:20 Trading-Agent python[1622805]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:20 Trading-Agent python[1622784]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:20 Trading-Agent python[1622721]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:21 Trading-Agent python[1622679]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:21 Trading-Agent python[1622826]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:21 Trading-Agent python[1622700]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:03:21 Trading-Agent python[1622742]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:05:29 Trading-Agent python[1622721]: [backtest] dati da cache: 165793 candele (BTCUSDT 15m)
Sep 24 06:05:30 Trading-Agent python[1622763]: [backtest] dati da cache: 165793 candele (ETHUSDT 15m)
Sep 24 06:05:30 Trading-Agent python[1622700]: [backtest] dati da cache: 165793 candele (ZECUSDT 15m)
Sep 24 06:05:30 Trading-Agent python[1622679]: [backtest] dati da cache: 165793 candele (XRPUSDT 15m)
Sep 24 06:05:31 Trading-Agent python[1622805]: [backtest] dati da cache: 165793 candele (SOLUSDT 15m)
Sep 24 06:05:32 Trading-Agent python[1622826]: [backtest] dati da cache: 165793 candele (NEARUSDT 15m)
Sep 24 06:05:33 Trading-Agent python[1622784]: [backtest] dati da cache: 46231 candele (HYPEUSDT 15m)
Sep 24 06:05:34 Trading-Agent python[1622742]: [backtest] dati da cache: 165793 candele (DOGEUSDT 15m)
Sep 24 06:07:19 Trading-Agent python[1622784]: [backtest] dati da cache: 165793 candele (BCHUSDT 15m)
Sep 24 06:12:06 Trading-Agent python[1622679]: [backtest] dati da cache: 165793 candele (UNIUSDT 15m)
Sep 24 06:12:08 Trading-Agent python[1622721]: [backtest] dati da cache: 36916 candele (TAKEUSDT 15m)
Sep 24 06:12:12 Trading-Agent python[1622763]: [backtest] dati da cache: 118783 candele (1000PEPEUSDT 15m)
Sep 24 06:12:25 Trading-Agent python[1622805]: [backtest] dati da cache: 165793 candele (BNBUSDT 15m)
Sep 24 06:12:27 Trading-Agent python[1622742]: [backtest] dati da cache: 118977 candele (SUIUSDT 15m)
Sep 24 06:12:33 Trading-Agent python[1622826]: [backtest] dati da cache: 52557 candele (NILUSDT 15m)
Sep 24 06:12:55 Trading-Agent python[1622700]: [backtest] dati da cache: 165793 candele (LTCUSDT 15m)
```
