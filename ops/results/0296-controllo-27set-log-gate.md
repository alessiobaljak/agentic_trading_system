# 0296-controllo-27set-log-gate.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 27 06:08:43 Trading-Agent python[1753392]: [backtest] dati da cache: 12161 candele (SYRUPUSDT 1h)
Sep 27 06:08:49 Trading-Agent python[1753371]: [backtest] dati da cache: 15374 candele (DEXEUSDT 1h)
Sep 27 06:08:56 Trading-Agent python[1753392]: [backtest] dati da cache: 17750 candele (NEIROUSDT 1h)
Sep 27 06:09:06 Trading-Agent python[1753371]: [backtest] dati da cache: 26245 candele (BICOUSDT 1h)
Sep 27 06:09:15 Trading-Agent python[1753392]: [backtest] dati da cache: 19023 candele (RENDERUSDT 1h)
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] BTCUSDT: worker rss 524 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] ETHUSDT: worker rss 530 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] SOLUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] ADAUSDT: 1 coppie passate ✅
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] ADAUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] BCHUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] JTOUSDT: 1 coppie passate ✅
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] JTOUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] STXUSDT: 1 coppie passate ✅
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] STXUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] DOTUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] ORCAUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] HUMAUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] TRUMPUSDT: 2 coppie passate ✅
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] TRUMPUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] VETUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] GPSUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] SPXUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] SYRUPUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] DEXEUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] NEIROUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] BICOUSDT: worker rss 656 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [discover] RENDERUSDT: worker rss 616 MB
Sep 27 06:09:32 Trading-Agent python[1753282]: [selettore] 1266 righe (5 coppie) -> data/selettore/2026-09-27_1h.w*.jsonl
Sep 27 06:09:32 Trading-Agent python[1753282]: [autopsy] 5/1577 passate · muoiono su: total_return 976 · recovery 232 · trades 145 · regime 107 · consistency 65
Sep 27 06:09:32 Trading-Agent python[1753282]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 21
Sep 27 06:09:33 Trading-Agent python[1753282]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Sep 27 06:09:33 Trading-Agent python[1753282]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Sep 27 06:09:33 Trading-Agent python[1753282]: [cervello] keep del lock scelto dal gate: 0.75 x5 (dal paper 0.75 x5)
Sep 27 06:09:33 Trading-Agent python[1753282]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Sep 27 06:09:33 Trading-Agent python[1753282]: [cervello] declassate: 0 (nuove 0, tornate piene 0) · validate bocciate nel giro 0 · passate solo con la propria configurazione 0
Sep 27 06:09:33 Trading-Agent python[1753282]: [discover] GIRO FINITO in 0h 6m (1577 valutazioni, 5 passate)
Sep 27 06:09:33 Trading-Agent python[1753282]: ============================================================
Sep 27 06:09:33 Trading-Agent python[1753282]: [discover] 1577 valutazioni, 5 coppie nuove passate in QUESTO run.
Sep 27 06:09:33 Trading-Agent python[1753282]: [discover] coppie validate totali nel registro (base+generate): 212
Sep 27 06:09:33 Trading-Agent python[1753282]: ============================================================
Sep 27 06:09:34 Trading-Agent python[1753247]: [optimize] passata extra finita in 6 min (codice 0)
Sep 27 06:09:35 Trading-Agent python[1753524]: [firebase] connesso (Firestore + RTDB)
Sep 27 06:09:37 Trading-Agent python[1753524]: [discover] prove del paper passate all'AI:
Sep 27 06:09:37 Trading-Agent python[1753524]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 27 06:09:37 Trading-Agent python[1753524]: - PAPER (vissuto, 110 trade chiusi): profit factor 0.616 contro 2.098 promesso dal gate.
Sep 27 06:09:37 Trading-Agent python[1753524]: - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 27 06:09:37 Trading-Agent python[1753524]: - Direzione long: 45 trade, 20 vinti, PnL -22.79.
Sep 27 06:09:37 Trading-Agent python[1753524]: - Direzione short: 66 trade, 33 vinti, PnL -51.00.
Sep 27 06:09:37 Trading-Agent python[1753524]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su regime 22 · holdout 1 · trades 6 · total_return 1207.
Sep 27 06:09:52 Trading-Agent python[1753524]: [ai-autopsia] ok in 15.1s · 1495+794 token
Sep 27 06:09:52 Trading-Agent python[1753524]: [ai-autopsia] schema: I quasi-passaggi si dividono in due cluster: 13 fermati su pf_ex_top (PF 1.26-1.45, spesso 250-520 trade) e 8 fermati su holdout con scarto 0.000 ma PF alto (1.38-2.04, tipicamente <220 trade). Ricorrono le coin ADA, STX, TRUMP, NEIRO, SYRUP, DEXE, ETH; timeframe unico 15m. Le feature visibili sono
Sep 27 06:09:52 Trading-Agent python[1753524]: [ai-autopsia] consigli: Per il cluster pf_ex_top puntate su edge piu' distribuito: piu' trade e meno dipendenza da singoli movimenti (filtri che riducano la varianza del profitto per trade, non che la aumentino). Per il cluster holdout verificate cosa misura esattamente lo scarto 0.000 (probabile soglia di trade/copertura
Sep 27 06:10:38 Trading-Agent python[1753524]: [ai-hypotheses] ok in 46.2s · 2036+3360 token
Sep 27 06:10:38 Trading-Agent python[1753524]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 27 06:10:38 Trading-Agent python[1753524]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 27 06:10:38 Trading-Agent python[1753524]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 27 06:10:38 Trading-Agent python[1753524]: [discover] rivalutazione solo urgenti: 31 spec note su 570
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] semi: 2 da coin NON coperte (su 68 gia' coperte)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] 3 semi dai quasi-passaggi del run precedente
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 27 06:10:39 Trading-Agent python[1753524]: [discover] 96 candidate (520 con conferme ri-validate + -489 altre, 539 tagliate su 570 note) seed=89375 2022-01-01->2026-09-27
Sep 27 06:11:00 Trading-Agent python[1753524]: [ai-universe] risposta senza JSON valido -> ignorata
Sep 27 06:11:00 Trading-Agent python[1753524]: [discover] 80 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (DEXEUSDT, BICOUSDT, ORCAUSDT, GPSUSDT, SKYAIUSDT, TSTUSDT, JASMYUSDT, SCRUSDT, HEMIUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT ...)
Sep 27 06:11:00 Trading-Agent python[1753524]: [discover] maturazione: 137 coin a un passo dalla validazione (mai tagliate) + 35 con una conferma · 0 tagliate dalla coda
Sep 27 06:11:00 Trading-Agent python[1753524]: [discover] shard 0/1: 280/280 coin
Sep 27 06:11:00 Trading-Agent python[1753524]: [parallel] worker ridotti da 8 a 2: 6.3 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 27 06:11:00 Trading-Agent python[1753524]: [discover] 280 coin x 96 spec su 2 worker (core)
Sep 27 06:11:00 Trading-Agent python[1753524]: [paper] 30 verdetti trailing (11 prematuri, 19 protetti) -> keep candidato dal vissuto: 0.75 (si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate)
Sep 27 06:11:00 Trading-Agent python[1753524]: [paper] 111 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 27 06:11:00 Trading-Agent python[1753524]: [paper] scale per strategia dal vissuto: 5 strategie con >= 5 trade (es. gen_2031005e -> 0.5/1/1.25)
Sep 27 06:11:03 Trading-Agent python[1753636]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:11:03 Trading-Agent python[1753615]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
```
