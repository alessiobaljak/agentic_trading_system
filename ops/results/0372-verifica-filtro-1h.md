# 0372-verifica-filtro-1h.req

_eseguito: 2026-09-30 09:31 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 30 09:12:29 Trading-Agent python[1907894]: - PAPER (vissuto, 183 trade chiusi): profit factor 0.702 contro 2.023 promesso dal gate.
Sep 30 09:12:29 Trading-Agent python[1907894]: - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 30 09:12:29 Trading-Agent python[1907894]: - Direzione long: 81 trade, 43 vinti, PnL -30.31.
Sep 30 09:12:29 Trading-Agent python[1907894]: - Direzione short: 109 trade, 64 vinti, PnL -37.43.
Sep 30 09:12:29 Trading-Agent python[1907894]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su total_return 1207 · pf_ex_top 3 · trades 6 · holdout 1.
Sep 30 09:12:46 Trading-Agent python[1907894]: [ai-autopsia] ok in 17.1s · 3239+736 token
Sep 30 09:12:46 Trading-Agent python[1907894]: [ai-autopsia] schema: I quasi-passaggi si concentrano su poche coin (BANK, DEXE, UB, ADA, ETH, TRUMP) e ruotano quasi tutti attorno a bb_break e volume_surge combinati con filtri di trend (trend_strength/adx) o relative_strength, su TF 15m. I due criteri che fermano queste candidate sono pf_ex_top (PF fuori dal target un
Sep 30 09:12:46 Trading-Agent python[1907894]: [ai-autopsia] consigli: Preferite strategie con edge distribuito su piu' trade (per superare pf_ex_top) e testate la robustezza al holdout separando in-sample da out-of-sample: molte candidate con PF>1.8 falliscono sul holdout, quindi diffidate del PF in-sample alto. Diversificate oltre bb_break/volume_surge e oltre le poc
Sep 30 09:13:35 Trading-Agent python[1907894]: [ai-hypotheses] ok in 48.1s · 2018+3564 token
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 30 09:13:35 Trading-Agent python[1907894]: [cervello] sessione oraria: 101 spec note su 676 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] rivalutazione solo urgenti: 27 spec note su 676
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] semi: 6 da coin NON coperte (su 70 gia' coperte)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] 22 semi dai quasi-passaggi del run precedente
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] 2 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 30 09:13:35 Trading-Agent python[1907894]: [discover] 109 candidate (626 con conferme ri-validate + -599 altre, 649 tagliate su 676 note) seed=59547 2022-01-01->2026-09-30
Sep 30 09:13:54 Trading-Agent python[1907894]: [ai-universe] ok in 18.3s · 2174+1793 token
Sep 30 09:13:54 Trading-Agent python[1907894]: [ai-universe] escluse 55/200 coin dal ciclo di validazione
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso 龙虾USDT: listing meme locale, illiquida non rappresentativa
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso 牛来USDT: meme locale, illiquida
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso 币安人生USDT: meme locale, illiquida
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso BTWUSDT: listing recente illiquido, storia troppo corta
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso MARSCOINUSDT: meme illiquido, storia inaffidabile
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso USUSDT: listing recente, storia insufficiente
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso PONSUSDT: listing recente, storia troppo corta
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso AKEUSDT: illiquida, storia insufficiente
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso QUSDT: ticker illiquido, storia insufficiente
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover]   escluso LYNUSDT: listing recente illiquido
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover] 93 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (ZORAUSDT, ZKUSDT, XPLUSDT, DEXEUSDT, ORCAUSDT, SKYAIUSDT, HEIUSDT, HEMIUSDT, FORMUSDT, BULLAUSDT, ARCUSDT, SAHARAUSDT ...)
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover] maturazione: 130 coin a un passo dalla validazione (mai tagliate) + 50 con una conferma · 0 tagliate dalla coda
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover] shard 0/1: 238/238 coin
Sep 30 09:13:54 Trading-Agent python[1907894]: [parallel] worker ridotti da 8 a 6: 14.5 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 30 09:13:54 Trading-Agent python[1907894]: [discover] 238 coin x 109 spec su 6 worker (core)
Sep 30 09:13:55 Trading-Agent python[1907894]: [paper] 71 verdetti trailing (30 prematuri, 41 protetti) -> nessun candidato in piu' (sotto il 60%)
Sep 30 09:13:55 Trading-Agent python[1907894]: [paper] 190 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 30 09:13:55 Trading-Agent python[1907894]: [paper] scale per strategia dal vissuto: 10 strategie con >= 5 trade (es. gen_2031005e -> 0.75/1/1.25)
Sep 30 09:13:55 Trading-Agent python[1907894]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.72 del tragitto entry->TP su 80 trade
Sep 30 09:13:57 Trading-Agent python[1908069]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:13:57 Trading-Agent python[1908006]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:13:57 Trading-Agent python[1908090]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:13:57 Trading-Agent python[1908027]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:13:58 Trading-Agent python[1908111]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:13:58 Trading-Agent python[1908048]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:16:11 Trading-Agent python[1908069]: [backtest] dati da cache: 166369 candele (ETHUSDT 15m)
Sep 30 09:16:11 Trading-Agent python[1908048]: [backtest] dati da cache: 166369 candele (BTCUSDT 15m)
Sep 30 09:16:11 Trading-Agent python[1908090]: [backtest] dati da cache: 166369 candele (SOLUSDT 15m)
Sep 30 09:16:12 Trading-Agent python[1908027]: [backtest] dati da cache: 166369 candele (ZECUSDT 15m)
Sep 30 09:16:12 Trading-Agent python[1908006]: [backtest] dati da cache: 138327 candele (QNTUSDT 15m)
Sep 30 09:16:15 Trading-Agent python[1908111]: [backtest] dati da cache: 166369 candele (XRPUSDT 15m)
Sep 30 09:20:11 Trading-Agent python[1908006]: [backtest] dati da cache: 166369 candele (NEARUSDT 15m)
Sep 30 09:20:47 Trading-Agent python[1908048]: [backtest] dati da cache: 46807 candele (HYPEUSDT 15m)
Sep 30 09:20:49 Trading-Agent python[1908069]: [backtest] dati da cache: 42883 candele (PUMPUSDT 15m)
Sep 30 09:20:54 Trading-Agent python[1908090]: [backtest] dati da cache: 166369 candele (DOGEUSDT 15m)
Sep 30 09:21:14 Trading-Agent python[1908027]: [backtest] dati da cache: 119553 candele (SUIUSDT 15m)
Sep 30 09:21:16 Trading-Agent python[1908111]: [backtest] dati da cache: 166369 candele (AAVEUSDT 15m)
Sep 30 09:22:12 Trading-Agent python[1908048]: [backtest] dati da cache: 166369 candele (AVAXUSDT 15m)
Sep 30 09:22:16 Trading-Agent python[1908069]: [backtest] dati da cache: 111697 candele (WLDUSDT 15m)
Sep 30 09:24:49 Trading-Agent python[1908027]: [backtest] dati da cache: 166369 candele (HBARUSDT 15m)
Sep 30 09:25:31 Trading-Agent python[1908006]: [backtest] dati da cache: 166369 candele (UNIUSDT 15m)
Sep 30 09:25:35 Trading-Agent python[1908069]: [backtest] dati da cache: 166369 candele (LINKUSDT 15m)
Sep 30 09:26:10 Trading-Agent python[1908111]: [backtest] dati da cache: 87407 candele (ENAUSDT 15m)
Sep 30 09:26:16 Trading-Agent python[1908090]: [backtest] dati da cache: 166369 candele (BNBUSDT 15m)
Sep 30 09:27:29 Trading-Agent python[1908048]: [backtest] dati da cache: 26907 candele (LITUSDT 15m)
Sep 30 09:27:30 Trading-Agent python[1908048]: [backtest] dati da cache: 96719 candele (MOVRUSDT 15m)
Sep 30 09:28:56 Trading-Agent python[1908111]: [backtest] dati da cache: 119359 candele (1000PEPEUSDT 15m)
Sep 30 09:30:10 Trading-Agent python[1908027]: [backtest] dati da cache: 86535 candele (TAOUSDT 15m)
Sep 30 09:30:42 Trading-Agent python[1908048]: [backtest] dati da cache: 166369 candele (ADAUSDT 15m)
Sep 30 09:30:48 Trading-Agent python[1908006]: [backtest] dati da cache: 94413 candele (ONDOUSDT 15m)
Sep 30 09:30:53 Trading-Agent python[1908069]: [backtest] dati da cache: 66179 candele (GRASSUSDT 15m)
Sep 30 09:31:39 Trading-Agent python[1908090]: [backtest] dati da cache: 166369 candele (XLMUSDT 15m)
```
