# 0283-giro-completo-log-gate-4.req

_eseguito: 2026-09-26 13:10 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 26 12:58:08 Trading-Agent python[1719019]: [discover] ADAUSDT: worker rss 527 MB
Sep 26 12:58:08 Trading-Agent python[1719019]: [discover] BCHUSDT: worker rss 525 MB
Sep 26 12:58:08 Trading-Agent python[1719019]: [selettore] 302 righe (1 coppie) -> data/selettore/2026-09-26_1h.w*.jsonl
Sep 26 12:58:08 Trading-Agent python[1719019]: [autopsy] 1/460 passate · muoiono su: total_return 312 · recovery 72 · regime 31 · trades 24 · consistency 8
Sep 26 12:58:08 Trading-Agent python[1719019]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 8
Sep 26 12:58:09 Trading-Agent python[1719019]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Sep 26 12:58:09 Trading-Agent python[1719019]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 26 12:58:09 Trading-Agent python[1719019]: [cervello] keep del lock scelto dal gate: 0.75 x1 (dal paper 0.75 x1)
Sep 26 12:58:09 Trading-Agent python[1719019]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 26 12:58:09 Trading-Agent python[1719019]: [discover] GIRO FINITO in 0h 2m (460 valutazioni, 1 passate)
Sep 26 12:58:09 Trading-Agent python[1719019]: ============================================================
Sep 26 12:58:09 Trading-Agent python[1719019]: [discover] 460 valutazioni, 1 coppie nuove passate in QUESTO run.
Sep 26 12:58:09 Trading-Agent python[1719019]: [discover] coppie validate totali nel registro (base+generate): 182
Sep 26 12:58:09 Trading-Agent python[1719019]: ============================================================
Sep 26 12:58:17 Trading-Agent python[1718986]: [optimize] passata extra finita in 3 min (codice 0)
Sep 26 12:58:19 Trading-Agent python[1719264]: [firebase] connesso (Firestore + RTDB)
Sep 26 12:58:20 Trading-Agent python[1719264]: [discover] prove del paper passate all'AI:
Sep 26 12:58:20 Trading-Agent python[1719264]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 26 12:58:20 Trading-Agent python[1719264]: - PAPER (vissuto, 90 trade chiusi): profit factor 0.588 contro 2.089 promesso dal gate.
Sep 26 12:58:20 Trading-Agent python[1719264]: - Escursione favorevole mediana 0.82R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 26 12:58:20 Trading-Agent python[1719264]: - Direzione long: 32 trade, 13 vinti, PnL -22.69.
Sep 26 12:58:20 Trading-Agent python[1719264]: - Direzione short: 58 trade, 28 vinti, PnL -49.48.
Sep 26 12:58:20 Trading-Agent python[1719264]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su total_return 1207 · trades 6 · recovery 64 · regime 22.
Sep 26 12:58:34 Trading-Agent python[1719264]: [ai-autopsia] ok in 13.4s · 849+685 token
Sep 26 12:58:34 Trading-Agent python[1719264]: [ai-autopsia] schema: Quasi-passaggi concentrati su ADAUSDT ed ETHUSDT (con qualche BCHUSDT) su 15m, spesso basati su combinazioni trend/momentum (macd_cross, relative_strength, trend_strength con adx>=20, atr 1.5-2.0). Il pattern piu' ricorrente e' la fermata su holdout con scarto 0.000 (4 su 8), mentre a livello global
Sep 26 12:58:34 Trading-Agent python[1719264]: [ai-autopsia] consigli: Prioritizzare robustezza cross-regime e sul holdout piuttosto che spingere il PF in-sample: puntare a strategie con piu' trade (per superare total_return e consistency) mantenendo PF moderato ma stabile. Testare le famiglie trend+ATR gia' promettenti su ADA/ETH ma verificando esplicitamente la tenut
Sep 26 12:59:17 Trading-Agent python[1719264]: [ai-hypotheses] ok in 43.1s · 1969+3242 token
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] 2 varianti dai referti del paper (B8): gen_ba3a671f -> gen_54d1beed (solo_short) · gen_fa304106 -> gen_9998083f (solo_long)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] rivalutazione solo urgenti: 7 spec note su 554
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] semi: 2 da coin NON coperte (su 62 gia' coperte)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] 2 semi dai quasi-passaggi del run precedente
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] GEMELLE gia' validate su DOTUSDT: 2 coppie con la stessa logica (gen_22b2cade, gen_5af56024)
Sep 26 12:59:17 Trading-Agent python[1719264]: [discover] 71 candidate (504 con conferme ri-validate + -497 altre, 547 tagliate su 554 note) seed=27499 2022-01-01->2026-09-26
Sep 26 12:59:42 Trading-Agent python[1719264]: [ai-universe] risposta senza JSON valido -> ignorata
Sep 26 12:59:42 Trading-Agent python[1719264]: [discover] 77 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (DEXEUSDT, BICOUSDT, ORCAUSDT, GPSUSDT, SKYAIUSDT, HEIUSDT, TSTUSDT, SCRUSDT, HEMIUSDT, BULLAUSDT, ARCUSDT, SAHARAUSDT ...)
Sep 26 12:59:42 Trading-Agent python[1719264]: [discover] maturazione: 127 coin a un passo dalla validazione (mai tagliate) + 46 con una conferma · 0 tagliate dalla coda
Sep 26 12:59:42 Trading-Agent python[1719264]: [discover] shard 0/1: 277/277 coin
Sep 26 12:59:42 Trading-Agent python[1719264]: [parallel] worker ridotti da 8 a 6: 14.5 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 26 12:59:42 Trading-Agent python[1719264]: [discover] 277 coin x 71 spec su 6 worker (core)
Sep 26 12:59:42 Trading-Agent python[1719264]: [paper] 25 verdetti trailing (9 prematuri, 16 protetti) -> keep candidato dal vissuto: 0.75 (si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate)
Sep 26 12:59:42 Trading-Agent python[1719264]: [paper] 90 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 26 12:59:42 Trading-Agent python[1719264]: [paper] scale per strategia dal vissuto: 5 strategie con >= 5 trade (es. gen_2031005e -> 0.5/1/1.25)
Sep 26 12:59:45 Trading-Agent python[1719418]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 12:59:45 Trading-Agent python[1719376]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 12:59:45 Trading-Agent python[1719397]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 12:59:45 Trading-Agent python[1719439]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 12:59:45 Trading-Agent python[1719355]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 12:59:45 Trading-Agent python[1719334]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 13:01:51 Trading-Agent python[1719376]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 13:01:52 Trading-Agent python[1719355]: [backtest] dati da cache: 165985 candele (ETHUSDT 15m)
Sep 26 13:01:53 Trading-Agent python[1719439]: [backtest] dati da cache: 165985 candele (SOLUSDT 15m)
Sep 26 13:01:54 Trading-Agent python[1719418]: [backtest] dati da cache: 165985 candele (ZECUSDT 15m)
Sep 26 13:01:54 Trading-Agent python[1719334]: [backtest] dati da cache: 165985 candele (XRPUSDT 15m)
Sep 26 13:01:56 Trading-Agent python[1719397]: [backtest] dati da cache: 165985 candele (NEARUSDT 15m)
Sep 26 13:04:19 Trading-Agent python[1719376]: [backtest] dati da cache: 87023 candele (ENAUSDT 15m)
Sep 26 13:04:20 Trading-Agent python[1719439]: [backtest] dati da cache: 60819 candele (PHAUSDT 15m)
Sep 26 13:04:20 Trading-Agent python[1719355]: [backtest] dati da cache: 119169 candele (SUIUSDT 15m)
Sep 26 13:04:23 Trading-Agent python[1719397]: [backtest] dati da cache: 46423 candele (HYPEUSDT 15m)
Sep 26 13:04:26 Trading-Agent python[1719418]: [backtest] dati da cache: 165985 candele (DOGEUSDT 15m)
Sep 26 13:04:26 Trading-Agent python[1719334]: [backtest] dati da cache: 165985 candele (UNIUSDT 15m)
Sep 26 13:05:16 Trading-Agent python[1719397]: [backtest] dati da cache: 111313 candele (WLDUSDT 15m)
Sep 26 13:05:32 Trading-Agent python[1719439]: [backtest] dati da cache: 165985 candele (LTCUSDT 15m)
Sep 26 13:06:11 Trading-Agent python[1719376]: [backtest] dati da cache: 165985 candele (LINKUSDT 15m)
Sep 26 13:06:44 Trading-Agent python[1719355]: [backtest] dati da cache: 73965 candele (RAREUSDT 15m)
Sep 26 13:07:26 Trading-Agent python[1719397]: [backtest] dati da cache: 86151 candele (TAOUSDT 15m)
Sep 26 13:07:37 Trading-Agent python[1719418]: [backtest] dati da cache: 10888 candele (BTWUSDT 15m)
Sep 26 13:07:39 Trading-Agent python[1719334]: [backtest] dati da cache: 94029 candele (ONDOUSDT 15m)
Sep 26 13:07:41 Trading-Agent python[1719418]: [backtest] dati da cache: 165985 candele (ADAUSDT 15m)
Sep 26 13:08:09 Trading-Agent python[1719355]: [backtest] dati da cache: 118975 candele (1000PEPEUSDT 15m)
Sep 26 13:08:46 Trading-Agent python[1719439]: [backtest] dati da cache: 38363 candele (XPLUSDT 15m)
Sep 26 13:09:02 Trading-Agent python[1719376]: [backtest] dati da cache: 165985 candele (BNBUSDT 15m)
Sep 26 13:09:07 Trading-Agent python[1719397]: [backtest] dati da cache: 165985 candele (AVAXUSDT 15m)
Sep 26 13:09:32 Trading-Agent python[1719439]: [backtest] dati da cache: 165985 candele (AAVEUSDT 15m)
Sep 26 13:09:34 Trading-Agent python[1719334]: [backtest] dati da cache: 53038 candele (BRUSDT 15m)
```
