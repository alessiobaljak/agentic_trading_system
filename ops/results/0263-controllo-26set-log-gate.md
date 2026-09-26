# 0263-controllo-26set-log-gate.req

_eseguito: 2026-09-26 06:05 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 26 06:02:34 Trading-Agent python[1708792]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 26 06:02:34 Trading-Agent python[1708792]: [discover] GEMELLE gia' validate su DOTUSDT: 2 coppie con la stessa logica (gen_22b2cade, gen_5af56024)
Sep 26 06:02:34 Trading-Agent python[1708792]: [discover] 69 candidate (499 con conferme ri-validate + 0 altre, 50 tagliate su 549 note) seed=2489 2022-01-01->2026-09-26
Sep 26 06:02:34 Trading-Agent python[1708792]: [discover] universo RISTRETTO a 5 coin (--symbols)
Sep 26 06:02:36 Trading-Agent python[1708792]: [ai-universe] ok in 1.3s · 484+10 token
Sep 26 06:02:36 Trading-Agent python[1708792]: [discover] shard 0/1: 5/5 coin
Sep 26 06:02:36 Trading-Agent python[1708792]: [parallel] worker ridotti da 8 a 6: 14.4 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 26 06:02:36 Trading-Agent python[1708792]: [discover] 5 coin x 69 spec su 6 worker (core)
Sep 26 06:02:36 Trading-Agent python[1708792]: [paper] 24 verdetti trailing (9 prematuri, 15 protetti) -> keep candidato dal vissuto: 0.75 (si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate)
Sep 26 06:02:36 Trading-Agent python[1708792]: [paper] 84 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 26 06:02:36 Trading-Agent python[1708792]: [paper] scale per strategia dal vissuto: 4 strategie con >= 5 trade (es. gen_2031005e -> 0.5/1/1.25)
Sep 26 06:02:36 Trading-Agent python[1708886]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:36 Trading-Agent python[1708865]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:37 Trading-Agent python[1708928]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:37 Trading-Agent python[1708949]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:37 Trading-Agent python[1708907]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:37 Trading-Agent python[1708970]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:59 Trading-Agent python[1708907]: [backtest] dati da cache: 41473 candele (BTCUSDT 1h)
Sep 26 06:02:59 Trading-Agent python[1708970]: [backtest] dati da cache: 41473 candele (ETHUSDT 1h)
Sep 26 06:02:59 Trading-Agent python[1708949]: [backtest] dati da cache: 41473 candele (SOLUSDT 1h)
Sep 26 06:03:00 Trading-Agent python[1708886]: [backtest] dati da cache: 41473 candele (ADAUSDT 1h)
Sep 26 06:03:00 Trading-Agent python[1708928]: [backtest] dati da cache: 41473 candele (BCHUSDT 1h)
Sep 26 06:03:37 Trading-Agent python[1708792]: [discover] BTCUSDT: worker rss 522 MB
Sep 26 06:03:37 Trading-Agent python[1708792]: [discover] ETHUSDT: worker rss 523 MB
Sep 26 06:03:37 Trading-Agent python[1708792]: [discover] SOLUSDT: worker rss 522 MB
Sep 26 06:03:37 Trading-Agent python[1708792]: [discover] ADAUSDT: 1 coppie passate ✅
Sep 26 06:03:37 Trading-Agent python[1708792]: [discover] ADAUSDT: worker rss 528 MB
Sep 26 06:03:37 Trading-Agent python[1708792]: [discover] BCHUSDT: worker rss 522 MB
Sep 26 06:03:37 Trading-Agent python[1708792]: [selettore] 302 righe (1 coppie) -> data/selettore/2026-09-26_1h.w*.jsonl
Sep 26 06:03:37 Trading-Agent python[1708792]: [autopsy] 1/345 passate · muoiono su: total_return 215 · recovery 71 · regime 24 · trades 18 · consistency 10
Sep 26 06:03:37 Trading-Agent python[1708792]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 3
Sep 26 06:03:38 Trading-Agent python[1708792]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Sep 26 06:03:38 Trading-Agent python[1708792]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 26 06:03:38 Trading-Agent python[1708792]: [cervello] keep del lock scelto dal gate: 0.75 x1 (dal paper 0.75 x1)
Sep 26 06:03:38 Trading-Agent python[1708792]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 26 06:03:38 Trading-Agent python[1708792]: [discover] GIRO FINITO in 0h 2m (345 valutazioni, 1 passate)
Sep 26 06:03:38 Trading-Agent python[1708792]: ============================================================
Sep 26 06:03:38 Trading-Agent python[1708792]: [discover] 345 valutazioni, 1 coppie nuove passate in QUESTO run.
Sep 26 06:03:38 Trading-Agent python[1708792]: [discover] coppie validate totali nel registro (base+generate): 182
Sep 26 06:03:38 Trading-Agent python[1708792]: ============================================================
Sep 26 06:03:38 Trading-Agent python[1708751]: [optimize] passata extra finita in 2 min (codice 0)
Sep 26 06:03:40 Trading-Agent python[1709111]: [firebase] connesso (Firestore + RTDB)
Sep 26 06:03:41 Trading-Agent python[1709111]: [discover] prove del paper passate all'AI:
Sep 26 06:03:41 Trading-Agent python[1709111]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 26 06:03:41 Trading-Agent python[1709111]: - PAPER (vissuto, 84 trade chiusi): profit factor 0.615 contro 2.091 promesso dal gate.
Sep 26 06:03:41 Trading-Agent python[1709111]: - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 26 06:03:41 Trading-Agent python[1709111]: - Direzione long: 30 trade, 13 vinti, PnL -18.78.
Sep 26 06:03:41 Trading-Agent python[1709111]: - Direzione short: 54 trade, 26 vinti, PnL -44.95.
Sep 26 06:03:41 Trading-Agent python[1709111]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su total_return 1207 · recovery 64 · consistency 17 · pf_ex_top 3.
Sep 26 06:03:56 Trading-Agent python[1709111]: [ai-autopsia] ok in 14.5s · 628+709 token
Sep 26 06:03:56 Trading-Agent python[1709111]: [ai-autopsia] schema: Tutti e tre sono su 15m con PF discreti (1.30-1.74) e volumi di trade sani (124-223), su ADAUSDT (2 su 3) ed ETHUSDT. Usano filtri di trend/momentum multi-timeframe (macd_cross+htf_fade, relative_strength+trend_strength con adx>=20). Le fermate sono su recovery (scarto minimo -0.029) e holdout (scar
Sep 26 06:03:56 Trading-Agent python[1709111]: [ai-autopsia] consigli: Puntate su logiche trend-following multi-TF gia' viste (adx>=20, relative_strength) ma aggiungete controllo esplicito del drawdown/dimensionamento per superare recovery, e testate su piu' segmenti temporali per non morire sull'holdout. Diversificate oltre ADA/ETH e verificate la stabilita' rispetto
Sep 26 06:04:43 Trading-Agent python[1709111]: [ai-hypotheses] ok in 47.0s · 1988+3444 token
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] 2 varianti dai referti del paper (B8): gen_ba3a671f -> gen_54d1beed (solo_short) · gen_fa304106 -> gen_9998083f (solo_long)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] rivalutazione solo urgenti: 7 spec note su 549
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] semi: 2 da coin NON coperte (su 62 gia' coperte)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] 2 semi dai quasi-passaggi del run precedente
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] GEMELLE gia' validate su DOTUSDT: 2 coppie con la stessa logica (gen_22b2cade, gen_5af56024)
Sep 26 06:04:43 Trading-Agent python[1709111]: [discover] 71 candidate (499 con conferme ri-validate + -492 altre, 542 tagliate su 549 note) seed=2619 2022-01-01->2026-09-26
Sep 26 06:05:07 Trading-Agent python[1709111]: [ai-universe] risposta senza JSON valido -> ignorata
Sep 26 06:05:07 Trading-Agent python[1709111]: [discover] 74 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (DEXEUSDT, BICOUSDT, ORCAUSDT, GPSUSDT, SKYAIUSDT, HEIUSDT, SCRUSDT, HEMIUSDT, BULLAUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT ...)
Sep 26 06:05:07 Trading-Agent python[1709111]: [discover] maturazione: 127 coin a un passo dalla validazione (mai tagliate) + 44 con una conferma · 0 tagliate dalla coda
Sep 26 06:05:07 Trading-Agent python[1709111]: [discover] shard 0/1: 274/274 coin
Sep 26 06:05:07 Trading-Agent python[1709111]: [parallel] worker ridotti da 8 a 6: 14.5 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 26 06:05:07 Trading-Agent python[1709111]: [discover] 274 coin x 71 spec su 6 worker (core)
Sep 26 06:05:07 Trading-Agent python[1709111]: [paper] 24 verdetti trailing (9 prematuri, 15 protetti) -> keep candidato dal vissuto: 0.75 (si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate)
Sep 26 06:05:07 Trading-Agent python[1709111]: [paper] 84 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 26 06:05:07 Trading-Agent python[1709111]: [paper] scale per strategia dal vissuto: 4 strategie con >= 5 trade (es. gen_2031005e -> 0.5/1/1.25)
Sep 26 06:05:10 Trading-Agent python[1709217]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 06:05:10 Trading-Agent python[1709175]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 06:05:10 Trading-Agent python[1709196]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 06:05:10 Trading-Agent python[1709280]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 06:05:10 Trading-Agent python[1709259]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 26 06:05:10 Trading-Agent python[1709238]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
```
