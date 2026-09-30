# 0365-30set-log-gate.req

_eseguito: 2026-09-30 06:12 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 30 05:09:28 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 12h 9min 20.890s CPU time.
Sep 30 06:08:46 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Sep 30 06:08:48 Trading-Agent python[1902019]: [firebase] connesso (Firestore + RTDB)
Sep 30 06:08:49 Trading-Agent python[1902019]: [optimize] universo: top 200 per volume -> 200 coin
Sep 30 06:08:49 Trading-Agent python[1902019]: [optimize] shard 0/1: 200/200 coin
Sep 30 06:08:49 Trading-Agent python[1902019]: [optimize] strategie BASE saltate (OPTIMIZER_SKIP_BASE): 0 validate su 1312 valutazioni nella storia del registro — il calcolo va alla discovery. Faccio solo la manutenzione del registro.
Sep 30 06:08:50 Trading-Agent python[1902019]: [optimize] registro: 202 validate · copertura 35.0%
Sep 30 06:08:51 Trading-Agent python[1902019]: [optimize] passata extra: discovery a 1h su 30 coin (auto30: 5 fisse + 15 con coppie a 1h + 10 con validate + 0 top volume) (max 40 min) · ~12 min stimati: 2 min per 5 coin misurati il 26 set
Sep 30 06:08:51 Trading-Agent python[1902019]: [optimize] passata extra: coin BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT,BCHUSDT,BANKUSDT,BICOUSDT,CVCUSDT,DEXEUSDT,DOTUSDT,HEIUSDT,HEMIUSDT,JTOUSDT,ORCAUSDT,QUSDT,SPXUSDT,STXUSDT,SYRUPUSDT,TRUMPUSDT,USELESSUSDT,UBUSDT,SKYAIUSDT,HUMAUSDT,MUBARAKUSDT,BULLAUSDT,GPSUSDT,SAHARAUSDT,AVAAIUSDT,VETUSDT,BMTUSDT
Sep 30 06:08:52 Trading-Agent python[1902052]: [firebase] connesso (Firestore + RTDB)
Sep 30 06:08:53 Trading-Agent python[1902052]: [discover] prove del paper passate all'AI:
Sep 30 06:08:53 Trading-Agent python[1902052]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 30 06:08:53 Trading-Agent python[1902052]: - PAPER (vissuto, 182 trade chiusi): profit factor 0.698 contro 2.024 promesso dal gate.
Sep 30 06:08:53 Trading-Agent python[1902052]: - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 30 06:08:53 Trading-Agent python[1902052]: - Direzione long: 80 trade, 42 vinti, PnL -31.22.
Sep 30 06:08:53 Trading-Agent python[1902052]: - Direzione short: 109 trade, 64 vinti, PnL -37.43.
Sep 30 06:08:53 Trading-Agent python[1902052]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su trades 6 · regime 22 · total_return 1207 · holdout 1.
Sep 30 06:09:09 Trading-Agent python[1902052]: [ai-autopsia] ok in 15.6s · 3216+737 token
Sep 30 06:09:09 Trading-Agent python[1902052]: [ai-autopsia] schema: Dominano strategie mean-reversion su oscillatori estremi (stoch_momentum + rsi_extreme, spesso con bb_touch) su timeframe 15m, quasi tutte con adx>=0.0 (nessun filtro di trend) e atr elevato (2.0-2.5). Il criterio che ferma di gran lunga di piu' e' pf_ex_top (profit factor escludendo i top trade), s
Sep 30 06:09:09 Trading-Agent python[1902052]: [ai-autopsia] consigli: Per superare pf_ex_top puntate su edge piu' distribuito, non dipendente da pochi outlier: riducete l'atr (usate 1.0-1.5, gia' presente in alcuni setup vwap/htf_fade che si fermano su altro) e valutate filtri direzionali/trend invece di adx>=0.0 puro. Evitate setup con <40 trade attesi (falliranno su
Sep 30 06:09:54 Trading-Agent python[1902052]: [ai-hypotheses] ok in 44.8s · 2026+3325 token
Sep 30 06:09:54 Trading-Agent python[1902052]: [discover] 20 ipotesi AI (motivate) + 40 casuali
Sep 30 06:09:54 Trading-Agent python[1902052]: [cervello] sessione oraria: 99 spec note su 667 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] rivalutazione completa: 617 spec note su 667
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] semi: 13 da coin NON coperte (su 70 gia' coperte)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] 16 semi dai quasi-passaggi del run precedente
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] 1 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] 129 candidate (617 con conferme ri-validate + 0 altre, 50 tagliate su 667 note) seed=48532 2022-01-01->2026-09-30
Sep 30 06:09:55 Trading-Agent python[1902052]: [discover] universo RISTRETTO a 30 coin (--symbols)
Sep 30 06:10:00 Trading-Agent python[1902052]: [ai-universe] ok in 5.0s · 760+403 token
Sep 30 06:10:00 Trading-Agent python[1902052]: [ai-universe] escluse 10/30 coin dal ciclo di validazione
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso TRUMPUSDT: prezzo guidato da eventi discreti, non dinamica mercato
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso HEIUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso HEMIUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso MUBARAKUSDT: meme recente, storia corta e non rappresentativa
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso BULLAUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso SKYAIUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso AVAAIUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso UBUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso SAHARAUSDT: listing recente, storia troppo corta
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover]   escluso USELESSUSDT: meme recente, storia corta non rappresentativa
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover] shard 0/1: 20/20 coin
Sep 30 06:10:00 Trading-Agent python[1902052]: [parallel] worker ridotti da 8 a 6: 14.1 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 30 06:10:00 Trading-Agent python[1902052]: [discover] 20 coin x 129 spec su 6 worker (core)
Sep 30 06:10:00 Trading-Agent python[1902052]: [paper] 70 verdetti trailing (29 prematuri, 41 protetti) -> nessun candidato in piu' (sotto il 60%)
Sep 30 06:10:00 Trading-Agent python[1902052]: [paper] 189 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 30 06:10:00 Trading-Agent python[1902052]: [paper] scale per strategia dal vissuto: 10 strategie con >= 5 trade (es. gen_2031005e -> 0.75/1/1.25)
Sep 30 06:10:00 Trading-Agent python[1902052]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.72 del tragitto entry->TP su 79 trade
Sep 30 06:10:01 Trading-Agent python[1902133]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:01 Trading-Agent python[1902154]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:01 Trading-Agent python[1902196]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:01 Trading-Agent python[1902175]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:01 Trading-Agent python[1902217]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:01 Trading-Agent python[1902238]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:26 Trading-Agent python[1902238]: [backtest] dati da cache: 41569 candele (BTCUSDT 1h)
Sep 30 06:10:26 Trading-Agent python[1902154]: [backtest] dati da cache: 41569 candele (ETHUSDT 1h)
Sep 30 06:10:27 Trading-Agent python[1902196]: [backtest] dati da cache: 41569 candele (SOLUSDT 1h)
Sep 30 06:10:27 Trading-Agent python[1902175]: [backtest] dati da cache: 41569 candele (ADAUSDT 1h)
Sep 30 06:10:27 Trading-Agent python[1902133]: [backtest] dati da cache: 41569 candele (BCHUSDT 1h)
Sep 30 06:10:27 Trading-Agent python[1902217]: [backtest] dati da cache: 12679 candele (BANKUSDT 1h)
Sep 30 06:11:09 Trading-Agent python[1902217]: [backtest] dati da cache: 26341 candele (BICOUSDT 1h)
Sep 30 06:11:41 Trading-Agent python[1902238]: [backtest] dati da cache: 12041 candele (CVCUSDT 1h)
Sep 30 06:11:42 Trading-Agent python[1902196]: [backtest] dati da cache: 15470 candele (DEXEUSDT 1h)
Sep 30 06:11:42 Trading-Agent python[1902133]: [backtest] dati da cache: 41593 candele (DOTUSDT 1h)
Sep 30 06:12:04 Trading-Agent python[1902154]: [backtest] dati da cache: 24639 candele (JTOUSDT 1h)
Sep 30 06:12:06 Trading-Agent python[1902238]: [backtest] dati da cache: 15898 candele (ORCAUSDT 1h)
Sep 30 06:12:07 Trading-Agent python[1902175]: [backtest] dati da cache: 9426 candele (QUSDT 1h)
Sep 30 06:12:08 Trading-Agent python[1902217]: [backtest] dati da cache: 15805 candele (SPXUSDT 1h)
Sep 30 06:12:25 Trading-Agent python[1902196]: [backtest] dati da cache: 31595 candele (STXUSDT 1h)
Sep 30 06:12:39 Trading-Agent python[1902175]: [backtest] dati da cache: 12257 candele (SYRUPUSDT 1h)
Sep 30 06:12:40 Trading-Agent python[1902238]: [backtest] dati da cache: 11796 candele (HUMAUSDT 1h)
Sep 30 06:12:42 Trading-Agent python[1902217]: [backtest] dati da cache: 14144 candele (GPSUSDT 1h)
```
