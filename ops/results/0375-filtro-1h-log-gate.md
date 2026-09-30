# 0375-filtro-1h-log-gate.req

_eseguito: 2026-09-30 12:13 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 30 12:09:27 Trading-Agent python[1912386]: [discover] GPSUSDT: worker rss 564 MB
Sep 30 12:09:27 Trading-Agent python[1912386]: [discover] AVAAIUSDT: worker rss 548 MB
Sep 30 12:09:27 Trading-Agent python[1912386]: [discover] VETUSDT: worker rss 697 MB
Sep 30 12:09:27 Trading-Agent python[1912386]: [discover] BMTUSDT: worker rss 550 MB
Sep 30 12:09:27 Trading-Agent python[1912386]: [selettore] 7865 righe (60 coppie) -> data/selettore/2026-09-30_1h.w*.jsonl
Sep 30 12:09:27 Trading-Agent python[1912386]: [controllo-gruppi] salvate 50 bocciate su 3395 idonee (seme 662850470) · foto conferme: 1551 coppie [1h]
Sep 30 12:09:27 Trading-Agent python[1912386]: [autopsy] 60/4050 passate · muoiono su: total_return 2365 · recovery 543 · regime 436 · trades 377 · consistency 144
Sep 30 12:09:27 Trading-Agent python[1912386]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 40
Sep 30 12:09:28 Trading-Agent python[1912386]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Sep 30 12:09:28 Trading-Agent python[1912386]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 30 12:09:28 Trading-Agent python[1912386]: [cervello] keep del lock scelto dal gate: 0.35 x6 · 0.5 x7 · 0.65 x47
Sep 30 12:09:28 Trading-Agent python[1912386]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 30 12:09:28 Trading-Agent python[1912386]: [cervello] declassate: 160 (nuove 0, tornate piene 0) · validate bocciate nel giro 0 · passate solo con la propria configurazione 0
Sep 30 12:09:28 Trading-Agent python[1912386]: [discover] GIRO FINITO in 0h 7m (4050 valutazioni, 60 passate)
Sep 30 12:09:28 Trading-Agent python[1912386]: ============================================================
Sep 30 12:09:28 Trading-Agent python[1912386]: [discover] 4050 valutazioni, 60 coppie nuove passate in QUESTO run.
Sep 30 12:09:28 Trading-Agent python[1912386]: [discover] coppie validate totali nel registro (base+generate): 202
Sep 30 12:09:28 Trading-Agent python[1912386]: ============================================================
Sep 30 12:09:37 Trading-Agent python[1912340]: [optimize] passata extra finita in 7 min (codice 0)
Sep 30 12:09:39 Trading-Agent python[1912737]: [firebase] connesso (Firestore + RTDB)
Sep 30 12:09:40 Trading-Agent python[1912737]: [discover] prove del paper passate all'AI:
Sep 30 12:09:40 Trading-Agent python[1912737]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 30 12:09:40 Trading-Agent python[1912737]: - PAPER (vissuto, 187 trade chiusi): profit factor 0.702 contro 2.023 promesso dal gate.
Sep 30 12:09:40 Trading-Agent python[1912737]: - Escursione favorevole mediana 0.86R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 30 12:09:40 Trading-Agent python[1912737]: - Direzione long: 83 trade, 45 vinti, PnL -29.56.
Sep 30 12:09:40 Trading-Agent python[1912737]: - Direzione short: 111 trade, 65 vinti, PnL -38.77.
Sep 30 12:09:40 Trading-Agent python[1912737]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su regime 22 · pf_ex_top 3 · trades 6 · holdout 1.
Sep 30 12:09:54 Trading-Agent python[1912737]: [ai-autopsia] ok in 13.5s · 3351+655 token
Sep 30 12:09:54 Trading-Agent python[1912737]: [ai-autopsia] schema: Dominano due cluster: (1) fermate su pf_ex_top con scarti minimi (da -0.002 a -0.087) su strategie di breakout, quasi tutte bb_break+volume_surge; (2) fermate su holdout con scarto 0.000 ma PF in-sample molto alto (1.48-1.95), concentrate su DEXEUSDT, BANKUSDT, ADAUSDT ed ETHUSDT con relative_streng
Sep 30 12:09:54 Trading-Agent python[1912737]: [ai-autopsia] consigli: Evitare di puntare su breakout+volume_surge puri che vivono di pochi trade estremi; privilegiare edge distribuiti su piu' trade e coin. Per superare holdout servono ipotesi meno fittate al passato: variare le feature oltre bb_break/relative_strength e testare robustezza cross-coin invece di ottimizz
Sep 30 12:10:42 Trading-Agent python[1912737]: [ai-hypotheses] ok in 48.3s · 1982+3531 token
Sep 30 12:10:42 Trading-Agent python[1912737]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 30 12:10:42 Trading-Agent python[1912737]: [cervello] sessione oraria: 102 spec note su 689 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] rivalutazione solo urgenti: 27 spec note su 689
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] semi: 6 da coin NON coperte (su 70 gia' coperte)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] 24 semi dai quasi-passaggi del run precedente
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 30 12:10:43 Trading-Agent python[1912737]: [discover] 113 candidate (639 con conferme ri-validate + -612 altre, 662 tagliate su 689 note) seed=70178 2022-01-01->2026-09-30
Sep 30 12:11:01 Trading-Agent python[1912737]: [ai-universe] ok in 17.7s · 2175+1872 token
Sep 30 12:11:01 Trading-Agent python[1912737]: [ai-universe] escluse 58/200 coin dal ciclo di validazione
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso BTWUSDT: illiquida, storia troppo corta
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso 0GUSDT: listing recente, price discovery
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso SOONUSDT: listing recente, storia corta
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso PONSUSDT: illiquida, poco nota
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso USUSDT: illiquida, listing recente
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso MARSCOINUSDT: illiquida, evento-driven
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso XPLUSDT: listing recente, price discovery
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso AKEUSDT: illiquida, storia corta
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso 龙虾USDT: ticker anomalo, illiquida
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover]   escluso ESPORTSUSDT: illiquida, listing recente
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover] 93 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (ZORAUSDT, ZKUSDT, XPLUSDT, DEXEUSDT, ORCAUSDT, SKYAIUSDT, HEIUSDT, MUBARAKUSDT, HEMIUSDT, TUTUSDT, FORMUSDT, BULLAUSDT ...)
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover] maturazione: 130 coin a un passo dalla validazione (mai tagliate) + 50 con una conferma · 0 tagliate dalla coda
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover] shard 0/1: 235/235 coin
Sep 30 12:11:01 Trading-Agent python[1912737]: [parallel] worker ridotti da 8 a 6: 14.5 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 30 12:11:01 Trading-Agent python[1912737]: [discover] 235 coin x 113 spec su 6 worker (core)
Sep 30 12:11:02 Trading-Agent python[1912737]: [paper] 72 verdetti trailing (30 prematuri, 42 protetti) -> nessun candidato in piu' (sotto il 60%)
Sep 30 12:11:02 Trading-Agent python[1912737]: [paper] 194 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 30 12:11:02 Trading-Agent python[1912737]: [paper] scale per strategia dal vissuto: 10 strategie con >= 5 trade (es. gen_2031005e -> 0.75/1/1.25)
Sep 30 12:11:02 Trading-Agent python[1912737]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.72 del tragitto entry->TP su 81 trade
Sep 30 12:11:04 Trading-Agent python[1912859]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:11:05 Trading-Agent python[1912838]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:11:05 Trading-Agent python[1912943]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:11:05 Trading-Agent python[1912880]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:11:05 Trading-Agent python[1912922]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:11:05 Trading-Agent python[1912901]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:13:22 Trading-Agent python[1912838]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 12:13:22 Trading-Agent python[1912922]: [backtest] dati da cache: 166369 candele (ETHUSDT 15m)
Sep 30 12:13:23 Trading-Agent python[1912880]: [backtest] dati da cache: 166369 candele (SOLUSDT 15m)
Sep 30 12:13:26 Trading-Agent python[1912901]: [backtest] dati da cache: 138327 candele (QNTUSDT 15m)
Sep 30 12:13:26 Trading-Agent python[1912859]: [backtest] dati da cache: 166369 candele (ZECUSDT 15m)
Sep 30 12:13:27 Trading-Agent python[1912943]: [backtest] dati da cache: 166369 candele (XRPUSDT 15m)
```
