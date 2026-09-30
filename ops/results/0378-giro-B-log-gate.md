# 0378-giro-B-log-gate.req

_eseguito: 2026-09-30 15:22 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 30 15:12:35 Trading-Agent python[1917265]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 30 15:12:35 Trading-Agent python[1917265]: [cervello] keep del lock scelto dal gate: 0.35 x6 · 0.5 x7 · 0.65 x56
Sep 30 15:12:35 Trading-Agent python[1917265]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 30 15:12:35 Trading-Agent python[1917265]: [cervello] declassate: 160 (nuove 0, tornate piene 0) · validate bocciate nel giro 0 · passate solo con la propria configurazione 0
Sep 30 15:12:35 Trading-Agent python[1917265]: [discover] GIRO FINITO in 0h 7m (4380 valutazioni, 69 passate)
Sep 30 15:12:36 Trading-Agent python[1917265]: ============================================================
Sep 30 15:12:36 Trading-Agent python[1917265]: [discover] 4380 valutazioni, 69 coppie nuove passate in QUESTO run.
Sep 30 15:12:36 Trading-Agent python[1917265]: [discover] coppie validate totali nel registro (base+generate): 202
Sep 30 15:12:36 Trading-Agent python[1917265]: ============================================================
Sep 30 15:12:36 Trading-Agent python[1917232]: [optimize] passata extra finita in 7 min (codice 0)
Sep 30 15:12:38 Trading-Agent python[1917666]: [firebase] connesso (Firestore + RTDB)
Sep 30 15:12:39 Trading-Agent python[1917666]: [discover] prove del paper passate all'AI:
Sep 30 15:12:39 Trading-Agent python[1917666]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 30 15:12:39 Trading-Agent python[1917666]: - PAPER (vissuto, 191 trade chiusi): profit factor 0.693 contro 2.024 promesso dal gate.
Sep 30 15:12:39 Trading-Agent python[1917666]: - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 30 15:12:39 Trading-Agent python[1917666]: - Direzione long: 85 trade, 46 vinti, PnL -31.99.
Sep 30 15:12:39 Trading-Agent python[1917666]: - Direzione short: 113 trade, 66 vinti, PnL -39.62.
Sep 30 15:12:39 Trading-Agent python[1917666]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su total_return 1207 · holdout 1 · recovery 64 · consistency 17.
Sep 30 15:12:59 Trading-Agent python[1917666]: [ai-autopsia] ok in 19.3s · 3179+847 token
Sep 30 15:12:59 Trading-Agent python[1917666]: [ai-autopsia] schema: La stragrande maggioranza dei quasi-passaggi si ferma su pf_ex_top (profit factor escludendo i top trade) con scarti spesso minimi (fino a -0.001), mentre un secondo blocco netto si ferma su holdout con scarto esatto 0.000. Dominano feature basate su breakout di banda (bb_break) e conferme di trend
Sep 30 15:12:59 Trading-Agent python[1917666]: [ai-autopsia] consigli: Per superare pf_ex_top puntate su strategie con edge piu' distribuito (piu' trade, PF meno dipendente dagli outlier): valutate exit piu' regolari o filtri che riducano i trade marginali senza tagliare i mediani. Per i casi holdout a scarto 0.000, aumentate il numero di trade/robustezza fuori campion
Sep 30 15:13:49 Trading-Agent python[1917666]: [ai-hypotheses] ok in 49.7s · 2033+3505 token
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 30 15:13:49 Trading-Agent python[1917666]: [cervello] sessione oraria: 102 spec note su 700 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] rivalutazione solo urgenti: 27 spec note su 700
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] semi: 5 da coin NON coperte (su 70 gia' coperte)
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] 20 semi dai quasi-passaggi del run precedente
Sep 30 15:13:49 Trading-Agent python[1917666]: [discover] 3 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 30 15:13:50 Trading-Agent python[1917666]: [discover] 105 candidate (650 con conferme ri-validate + -623 altre, 673 tagliate su 700 note) seed=81158 2022-01-01->2026-09-30
Sep 30 15:14:09 Trading-Agent python[1917666]: [ai-universe] ok in 19.2s · 2179+1812 token
Sep 30 15:14:09 Trading-Agent python[1917666]: [ai-universe] escluse 51/200 coin dal ciclo di validazione
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso 龙虾USDT: token illiquido, ticker anomalo
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso 牛来USDT: token illiquido, ticker anomalo
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso PONSUSDT: microcap illiquida, storia troppo corta
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso MARSCOINUSDT: microcap illiquida, poco rappresentativa
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso AKEUSDT: listing recente, liquidita' dubbia
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso SOONUSDT: listing recente, solo fase scoperta prezzo
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso USUSDT: listing recente, storia troppo corta
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso RAVEUSDT: microcap illiquida, storia corta
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso NOMUSDT: microcap illiquida, storia corta
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover]   escluso LYNUSDT: microcap illiquida, storia corta
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover] 86 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (ZORAUSDT, ZKUSDT, DEXEUSDT, ORCAUSDT, SKYAIUSDT, HEIUSDT, FORMUSDT, BULLAUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT, PNUTUSDT ...)
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover] maturazione: 130 coin a un passo dalla validazione (mai tagliate) + 51 con una conferma · 0 tagliate dalla coda
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover] shard 0/1: 235/235 coin
Sep 30 15:14:09 Trading-Agent python[1917666]: [parallel] worker ridotti da 8 a 6: 14.5 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 30 15:14:09 Trading-Agent python[1917666]: [discover] 235 coin x 105 spec su 6 worker (core)
Sep 30 15:14:10 Trading-Agent python[1917666]: [paper] 76 verdetti trailing (33 prematuri, 43 protetti) -> nessun candidato in piu' (sotto il 60%)
Sep 30 15:14:10 Trading-Agent python[1917666]: [paper] 198 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 30 15:14:10 Trading-Agent python[1917666]: [paper] scale per strategia dal vissuto: 10 strategie con >= 5 trade (es. gen_2031005e -> 0.75/1/1.25)
Sep 30 15:14:10 Trading-Agent python[1917666]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.72 del tragitto entry->TP su 85 trade
Sep 30 15:14:12 Trading-Agent python[1917820]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:14:12 Trading-Agent python[1917841]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:14:12 Trading-Agent python[1917778]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:14:12 Trading-Agent python[1917799]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:14:12 Trading-Agent python[1917862]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:14:13 Trading-Agent python[1917883]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:16:17 Trading-Agent python[1917841]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 15:16:17 Trading-Agent python[1917799]: [backtest] dati da cache: 166369 candele (ETHUSDT 15m)
Sep 30 15:16:17 Trading-Agent python[1917820]: [backtest] dati da cache: 166369 candele (SOLUSDT 15m)
Sep 30 15:16:18 Trading-Agent python[1917862]: [backtest] dati da cache: 166369 candele (ZECUSDT 15m)
Sep 30 15:16:19 Trading-Agent python[1917778]: [backtest] dati da cache: 138327 candele (QNTUSDT 15m)
Sep 30 15:16:20 Trading-Agent python[1917883]: [backtest] dati da cache: 166369 candele (XRPUSDT 15m)
Sep 30 15:19:51 Trading-Agent python[1917778]: [backtest] dati da cache: 166369 candele (NEARUSDT 15m)
Sep 30 15:20:25 Trading-Agent python[1917799]: [backtest] dati da cache: 46807 candele (HYPEUSDT 15m)
Sep 30 15:20:30 Trading-Agent python[1917883]: [backtest] dati da cache: 42883 candele (PUMPUSDT 15m)
Sep 30 15:20:30 Trading-Agent python[1917841]: [backtest] dati da cache: 96719 candele (MOVRUSDT 15m)
Sep 30 15:20:32 Trading-Agent python[1917820]: [backtest] dati da cache: 166369 candele (DOGEUSDT 15m)
Sep 30 15:20:48 Trading-Agent python[1917862]: [backtest] dati da cache: 119553 candele (SUIUSDT 15m)
Sep 30 15:21:48 Trading-Agent python[1917799]: [backtest] dati da cache: 111697 candele (WLDUSDT 15m)
Sep 30 15:21:50 Trading-Agent python[1917883]: [backtest] dati da cache: 87407 candele (ENAUSDT 15m)
```
