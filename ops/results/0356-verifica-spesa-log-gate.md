# 0356-verifica-spesa-log-gate.req

_eseguito: 2026-09-29 09:28 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 29 09:08:47 Trading-Agent python[1859569]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Sep 29 09:08:47 Trading-Agent python[1859569]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 29 09:08:47 Trading-Agent python[1859569]: [cervello] keep del lock scelto dal gate: 0.35 x2 · 0.5 x3 · 0.65 x27
Sep 29 09:08:47 Trading-Agent python[1859569]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 29 09:08:47 Trading-Agent python[1859569]: [cervello] declassate: 142 (nuove 0, tornate piene 0) · validate bocciate nel giro 0 · passate solo con la propria configurazione 0
Sep 29 09:08:47 Trading-Agent python[1859569]: [discover] GIRO FINITO in 0h 6m (2772 valutazioni, 32 passate)
Sep 29 09:08:47 Trading-Agent python[1859569]: ============================================================
Sep 29 09:08:47 Trading-Agent python[1859569]: [discover] 2772 valutazioni, 32 coppie nuove passate in QUESTO run.
Sep 29 09:08:47 Trading-Agent python[1859569]: [discover] coppie validate totali nel registro (base+generate): 199
Sep 29 09:08:47 Trading-Agent python[1859569]: ============================================================
Sep 29 09:08:47 Trading-Agent python[1859536]: [optimize] passata extra finita in 6 min (codice 0)
Sep 29 09:08:49 Trading-Agent python[1859901]: [firebase] connesso (Firestore + RTDB)
Sep 29 09:08:50 Trading-Agent python[1859901]: [discover] prove del paper passate all'AI:
Sep 29 09:08:50 Trading-Agent python[1859901]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 29 09:08:50 Trading-Agent python[1859901]: - PAPER (vissuto, 169 trade chiusi): profit factor 0.699 contro 2.031 promesso dal gate.
Sep 29 09:08:50 Trading-Agent python[1859901]: - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 29 09:08:50 Trading-Agent python[1859901]: - Direzione long: 71 trade, 37 vinti, PnL -28.33.
Sep 29 09:08:50 Trading-Agent python[1859901]: - Direzione short: 104 trade, 60 vinti, PnL -38.50.
Sep 29 09:08:50 Trading-Agent python[1859901]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su consistency 17 · regime 22 · holdout 1 · total_return 1207.
Sep 29 09:09:07 Trading-Agent python[1859901]: [ai-autopsia] ok in 16.9s · 2465+764 token
Sep 29 09:09:07 Trading-Agent python[1859901]: [ai-autopsia] schema: La stragrande maggioranza (25 su 30) si ferma su 'holdout' con scarto 0.000, cioe' falliscono l'ultima finestra out-of-sample nonostante PF in-sample buoni (1.4-2.6). C'e' forte concentrazione su poche coin (BANKUSDT ~10 casi, DEXEUSDT 4, QUSDT 3) e ricorrono feature trend-following con filtro adx_b
Sep 29 09:09:07 Trading-Agent python[1859901]: [ai-autopsia] consigli: Concentrarsi su coin con storia lunga e liquidita' alta e chiedere piu' trade nell'holdout stesso (non solo in-sample), scartando i PF gonfiati da campioni piccoli. Evitare di ottimizzare su BANKUSDT e simili e privilegiare logiche coerenti (trend con adx alto O mean-reversion con adx basso, non fil
Sep 29 09:09:52 Trading-Agent python[1859901]: [ai-hypotheses] ok in 44.6s · 2049+3276 token
Sep 29 09:09:52 Trading-Agent python[1859901]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 29 09:09:52 Trading-Agent python[1859901]: [cervello] sessione oraria: 96 spec note su 642 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] rivalutazione solo urgenti: 34 spec note su 642
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] semi: 2 da coin NON coperte (su 69 gia' coperte)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] 16 semi dai quasi-passaggi del run precedente
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] 1 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 29 09:09:53 Trading-Agent python[1859901]: [discover] 111 candidate (592 con conferme ri-validate + -558 altre, 608 tagliate su 642 note) seed=72929 2022-01-01->2026-09-29
Sep 29 09:10:18 Trading-Agent python[1859901]: [ai-universe] risposta senza JSON valido · 2119+2000 token · troncata: finito lo spazio max_tokens -> ignorata
Sep 29 09:10:18 Trading-Agent python[1859901]: [discover] 77 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (ZORAUSDT, DEXEUSDT, SKYAIUSDT, HEIUSDT, TSTUSDT, SCRUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT, PNUTUSDT, HOMEUSDT, SOLVUSDT ...)
Sep 29 09:10:18 Trading-Agent python[1859901]: [discover] maturazione: 125 coin a un passo dalla validazione (mai tagliate) + 52 con una conferma · 0 tagliate dalla coda
Sep 29 09:10:18 Trading-Agent python[1859901]: [discover] shard 0/1: 277/277 coin
Sep 29 09:10:18 Trading-Agent python[1859901]: [parallel] worker ridotti da 8 a 6: 14.5 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 29 09:10:18 Trading-Agent python[1859901]: [discover] 277 coin x 111 spec su 6 worker (core)
Sep 29 09:10:18 Trading-Agent python[1859901]: [paper] 65 verdetti trailing (27 prematuri, 38 protetti) -> nessun candidato in piu' (sotto il 60%)
Sep 29 09:10:18 Trading-Agent python[1859901]: [paper] 175 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 29 09:10:18 Trading-Agent python[1859901]: [paper] scale per strategia dal vissuto: 8 strategie con >= 5 trade (es. gen_2031005e -> 0.75/1/1.25)
Sep 29 09:10:18 Trading-Agent python[1859901]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.71 del tragitto entry->TP su 72 trade
Sep 29 09:10:21 Trading-Agent python[1860111]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:10:21 Trading-Agent python[1860026]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:10:21 Trading-Agent python[1860090]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:10:21 Trading-Agent python[1860005]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:10:21 Trading-Agent python[1860068]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:10:21 Trading-Agent python[1860047]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:12:32 Trading-Agent python[1860090]: [backtest] dati da cache: 166177 candele (ZECUSDT 15m)
Sep 29 09:12:32 Trading-Agent python[1860005]: [backtest] dati da cache: 166177 candele (ETHUSDT 15m)
Sep 29 09:12:32 Trading-Agent python[1860068]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 09:12:33 Trading-Agent python[1860111]: [backtest] dati da cache: 166177 candele (SOLUSDT 15m)
Sep 29 09:12:36 Trading-Agent python[1860047]: [backtest] dati da cache: 138135 candele (QNTUSDT 15m)
Sep 29 09:12:37 Trading-Agent python[1860026]: [backtest] dati da cache: 166177 candele (XRPUSDT 15m)
Sep 29 09:16:54 Trading-Agent python[1860047]: [backtest] dati da cache: 166177 candele (NEARUSDT 15m)
Sep 29 09:17:37 Trading-Agent python[1860111]: [backtest] dati da cache: 46615 candele (HYPEUSDT 15m)
Sep 29 09:17:39 Trading-Agent python[1860068]: [backtest] dati da cache: 166177 candele (HBARUSDT 15m)
Sep 29 09:17:40 Trading-Agent python[1860005]: [backtest] dati da cache: 166177 candele (LINKUSDT 15m)
Sep 29 09:17:45 Trading-Agent python[1860026]: [backtest] dati da cache: 119361 candele (SUIUSDT 15m)
Sep 29 09:18:50 Trading-Agent python[1860090]: [backtest] dati da cache: 166177 candele (DOGEUSDT 15m)
Sep 29 09:19:17 Trading-Agent python[1860111]: [backtest] dati da cache: 42691 candele (PUMPUSDT 15m)
Sep 29 09:20:38 Trading-Agent python[1860111]: [backtest] dati da cache: 166177 candele (UNIUSDT 15m)
Sep 29 09:21:55 Trading-Agent python[1860026]: [backtest] dati da cache: 111505 candele (WLDUSDT 15m)
Sep 29 09:22:37 Trading-Agent python[1860047]: [backtest] dati da cache: 87215 candele (ENAUSDT 15m)
Sep 29 09:23:20 Trading-Agent python[1860068]: [backtest] dati da cache: 166177 candele (BNBUSDT 15m)
Sep 29 09:23:22 Trading-Agent python[1860005]: [backtest] dati da cache: 166177 candele (AVAXUSDT 15m)
Sep 29 09:24:02 Trading-Agent python[1860090]: [backtest] dati da cache: 94221 candele (ONDOUSDT 15m)
Sep 29 09:25:28 Trading-Agent python[1860047]: [backtest] dati da cache: 166177 candele (XLMUSDT 15m)
Sep 29 09:25:39 Trading-Agent python[1860026]: [backtest] dati da cache: 11080 candele (BTWUSDT 15m)
Sep 29 09:25:41 Trading-Agent python[1860026]: [backtest] dati da cache: 114577 candele (NMRUSDT 15m)
Sep 29 09:26:15 Trading-Agent python[1860111]: [backtest] dati da cache: 166177 candele (ADAUSDT 15m)
Sep 29 09:27:04 Trading-Agent python[1860090]: [backtest] dati da cache: 86343 candele (TAOUSDT 15m)
```
