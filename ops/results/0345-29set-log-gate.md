# 0345-29set-log-gate.req

_eseguito: 2026-09-29 06:12 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] QUSDT: 10 coppie passate ✅
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] QUSDT: worker rss 552 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] SPXUSDT: 1 coppie passate ✅
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] SPXUSDT: worker rss 546 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] STXUSDT: 3 coppie passate ✅
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] STXUSDT: worker rss 551 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] SYRUPUSDT: 1 coppie passate ✅
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] SYRUPUSDT: worker rss 552 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] USELESSUSDT: worker rss 562 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] DOTUSDT: 1 coppie passate ✅
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] DOTUSDT: worker rss 552 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] HUMAUSDT: worker rss 546 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] GPSUSDT: worker rss 609 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] VETUSDT: worker rss 562 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [discover] BMTUSDT: worker rss 552 MB
Sep 29 06:06:27 Trading-Agent python[1852122]: [selettore] 4340 righe (29 coppie) -> data/selettore/2026-09-29_1h.w*.jsonl
Sep 29 06:06:27 Trading-Agent python[1852122]: [autopsy] 29/2520 passate · muoiono su: total_return 1605 · recovery 356 · regime 216 · trades 168 · consistency 82
Sep 29 06:06:27 Trading-Agent python[1852122]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 32
Sep 29 06:06:28 Trading-Agent python[1852122]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Sep 29 06:06:28 Trading-Agent python[1852122]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 29 06:06:28 Trading-Agent python[1852122]: [cervello] keep del lock scelto dal gate: 0.35 x2 · 0.5 x3 · 0.65 x24
Sep 29 06:06:28 Trading-Agent python[1852122]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 29 06:06:28 Trading-Agent python[1852122]: [cervello] declassate: 142 (nuove 0, tornate piene 0) · validate bocciate nel giro 0 · passate solo con la propria configurazione 0
Sep 29 06:06:28 Trading-Agent python[1852122]: [discover] GIRO FINITO in 0h 5m (2520 valutazioni, 29 passate)
Sep 29 06:06:28 Trading-Agent python[1852122]: ============================================================
Sep 29 06:06:28 Trading-Agent python[1852122]: [discover] 2520 valutazioni, 29 coppie nuove passate in QUESTO run.
Sep 29 06:06:28 Trading-Agent python[1852122]: [discover] coppie validate totali nel registro (base+generate): 199
Sep 29 06:06:28 Trading-Agent python[1852122]: ============================================================
Sep 29 06:06:28 Trading-Agent python[1852074]: [optimize] passata extra finita in 5 min (codice 0)
Sep 29 06:06:30 Trading-Agent python[1852650]: [firebase] connesso (Firestore + RTDB)
Sep 29 06:06:32 Trading-Agent python[1852650]: [discover] prove del paper passate all'AI:
Sep 29 06:06:32 Trading-Agent python[1852650]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 29 06:06:32 Trading-Agent python[1852650]: - PAPER (vissuto, 168 trade chiusi): profit factor 0.697 contro 2.035 promesso dal gate.
Sep 29 06:06:32 Trading-Agent python[1852650]: - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 29 06:06:32 Trading-Agent python[1852650]: - Direzione long: 70 trade, 36 vinti, PnL -28.83.
Sep 29 06:06:32 Trading-Agent python[1852650]: - Direzione short: 104 trade, 60 vinti, PnL -38.50.
Sep 29 06:06:32 Trading-Agent python[1852650]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su regime 22 · trades 6 · holdout 1 · recovery 64.
Sep 29 06:06:48 Trading-Agent python[1852650]: [ai-autopsia] ok in 16.6s · 2615+757 token
Sep 29 06:06:48 Trading-Agent python[1852650]: [ai-autopsia] schema: Due cluster netti: (1) strategie fermate su pf_ex_top con scarto piccolo, PF pieno ~1.28-1.44 e molti trade (160-425), concentrate su BANKUSDT/DEXEUSDT/STXUSDT; (2) un gruppo molto numeroso fermato su holdout con scarto esattamente 0.000, PF in-sample buoni (1.4-2.0), diffuso su molte coin. Ricorron
Sep 29 06:06:48 Trading-Agent python[1852650]: [ai-autopsia] consigli: Per il cluster pf_ex_top: alzare la selettivita' delle entrate (filtri piu' stretti, meno trade marginali) per non dipendere dagli outlier; puntare a PF robusto anche escludendo i top. Per il cluster holdout=0.000: verificare se e' un limite del gate/holdout troppo corto prima di iterare, e privileg
Sep 29 06:07:28 Trading-Agent python[1852650]: [ai-hypotheses] ok in 39.8s · 2029+3020 token
Sep 29 06:07:28 Trading-Agent python[1852650]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 29 06:07:28 Trading-Agent python[1852650]: [cervello] sessione oraria: 95 spec note su 637 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] rivalutazione solo urgenti: 34 spec note su 637
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] semi: 2 da coin NON coperte (su 69 gia' coperte)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] 17 semi dai quasi-passaggi del run precedente
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] 4 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 29 06:07:29 Trading-Agent python[1852650]: [discover] 109 candidate (587 con conferme ri-validate + -553 altre, 603 tagliate su 637 note) seed=61990 2022-01-01->2026-09-29
Sep 29 06:07:52 Trading-Agent python[1852650]: [ai-universe] risposta senza JSON valido -> ignorata
Sep 29 06:07:52 Trading-Agent python[1852650]: [discover] 77 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (ZORAUSDT, SKYAIUSDT, HEIUSDT, TSTUSDT, SCRUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT, PNUTUSDT, HOMEUSDT, SOLVUSDT, AVAAIUSDT ...)
Sep 29 06:07:52 Trading-Agent python[1852650]: [discover] maturazione: 125 coin a un passo dalla validazione (mai tagliate) + 52 con una conferma · 0 tagliate dalla coda
Sep 29 06:07:52 Trading-Agent python[1852650]: [discover] shard 0/1: 277/277 coin
Sep 29 06:07:52 Trading-Agent python[1852650]: [parallel] worker ridotti da 8 a 6: 14.2 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 29 06:07:52 Trading-Agent python[1852650]: [discover] 277 coin x 109 spec su 6 worker (core)
Sep 29 06:07:52 Trading-Agent python[1852650]: [paper] 62 verdetti trailing (25 prematuri, 37 protetti) -> nessun candidato in piu' (sotto il 60%)
Sep 29 06:07:52 Trading-Agent python[1852650]: [paper] 174 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 29 06:07:52 Trading-Agent python[1852650]: [paper] scale per strategia dal vissuto: 8 strategie con >= 5 trade (es. gen_2031005e -> 0.75/1/1.25)
Sep 29 06:07:52 Trading-Agent python[1852650]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.71 del tragitto entry->TP su 69 trade
Sep 29 06:07:54 Trading-Agent python[1852745]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:07:54 Trading-Agent python[1852850]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:07:54 Trading-Agent python[1852808]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:07:54 Trading-Agent python[1852787]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:07:55 Trading-Agent python[1852829]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:07:55 Trading-Agent python[1852766]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:09:53 Trading-Agent python[1852829]: [backtest] dati da cache: 166177 candele (BTCUSDT 15m)
Sep 29 06:09:54 Trading-Agent python[1852787]: [backtest] dati da cache: 166177 candele (ETHUSDT 15m)
Sep 29 06:09:55 Trading-Agent python[1852808]: [backtest] dati da cache: 166177 candele (ZECUSDT 15m)
Sep 29 06:09:55 Trading-Agent python[1852745]: [backtest] dati da cache: 166177 candele (SOLUSDT 15m)
Sep 29 06:09:55 Trading-Agent python[1852766]: [backtest] dati da cache: 138135 candele (QNTUSDT 15m)
Sep 29 06:09:56 Trading-Agent python[1852850]: [backtest] dati da cache: 166177 candele (XRPUSDT 15m)
```
