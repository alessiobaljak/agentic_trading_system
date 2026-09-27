# 0307-referto-27set-log-gate.req

_eseguito: 2026-09-27 07:09 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 27 06:51:38 Trading-Agent python[1756002]: [ai-hypotheses] ok in 47.3s · 1961+3428 token
Sep 27 06:51:38 Trading-Agent python[1756002]: [discover] 20 ipotesi AI (motivate) + 80 casuali
Sep 27 06:51:38 Trading-Agent python[1756002]: [discover] 2 varianti dai referti del paper (B8): gen_fa304106 -> gen_9998083f (solo_long) · gen_fca11c08 -> gen_6efd0bda (conferma_trend)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] rivalutazione solo urgenti: 31 spec note su 572
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] semi: 2 da coin NON coperte (su 68 gia' coperte)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] 3 semi dai quasi-passaggi del run precedente
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_18c839a0, gen_a12226f7)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] GEMELLE gia' validate su QUSDT: 2 coppie con la stessa logica (gen_0ada82e9, gen_7f8adcde)
Sep 27 06:51:39 Trading-Agent python[1756002]: [discover] 96 candidate (522 con conferme ri-validate + -491 altre, 541 tagliate su 572 note) seed=91837 2022-01-01->2026-09-27
Sep 27 06:52:04 Trading-Agent python[1756002]: [ai-universe] risposta senza JSON valido -> ignorata
Sep 27 06:52:04 Trading-Agent python[1756002]: [discover] 80 coin riaggiunte: hanno una coppia in maturazione ma sono uscite dal top-200 per volume (DEXEUSDT, BICOUSDT, ORCAUSDT, GPSUSDT, SKYAIUSDT, TSTUSDT, JASMYUSDT, SCRUSDT, HEMIUSDT, ARCUSDT, SAHARAUSDT, AIOUSDT ...)
Sep 27 06:52:04 Trading-Agent python[1756002]: [discover] maturazione: 137 coin a un passo dalla validazione (mai tagliate) + 35 con una conferma · 0 tagliate dalla coda
Sep 27 06:52:04 Trading-Agent python[1756002]: [discover] shard 0/1: 280/280 coin
Sep 27 06:52:04 Trading-Agent python[1756002]: [parallel] worker ridotti da 8 a 6: 14.4 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Sep 27 06:52:04 Trading-Agent python[1756002]: [discover] 280 coin x 96 spec su 6 worker (core)
Sep 27 06:52:04 Trading-Agent python[1756002]: [paper] 30 verdetti trailing (11 prematuri, 19 protetti) -> keep candidato dal vissuto: 0.75 (si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate)
Sep 27 06:52:04 Trading-Agent python[1756002]: [paper] 111 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Sep 27 06:52:04 Trading-Agent python[1756002]: [paper] scale per strategia dal vissuto: 5 strategie con >= 5 trade (es. gen_2031005e -> 0.5/1/1.25)
Sep 27 06:52:07 Trading-Agent python[1756109]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:52:07 Trading-Agent python[1756172]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:52:07 Trading-Agent python[1756193]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:52:07 Trading-Agent python[1756130]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:52:07 Trading-Agent python[1756151]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:52:07 Trading-Agent python[1756214]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:54:01 Trading-Agent python[1756109]: [backtest] dati da cache: 165985 candele (ETHUSDT 15m)
Sep 27 06:54:02 Trading-Agent python[1756172]: [backtest] dati da cache: 165985 candele (BTCUSDT 15m)
Sep 27 06:54:03 Trading-Agent python[1756130]: [backtest] dati da cache: 165985 candele (ZECUSDT 15m)
Sep 27 06:54:04 Trading-Agent python[1756214]: [backtest] dati da cache: 165985 candele (SOLUSDT 15m)
Sep 27 06:54:04 Trading-Agent python[1756151]: [backtest] dati da cache: 137943 candele (QNTUSDT 15m)
Sep 27 06:54:05 Trading-Agent python[1756193]: [backtest] dati da cache: 165985 candele (XRPUSDT 15m)
Sep 27 06:56:21 Trading-Agent python[1756151]: [backtest] dati da cache: 165985 candele (NEARUSDT 15m)
Sep 27 06:56:38 Trading-Agent python[1756109]: [backtest] dati da cache: 74157 candele (RAREUSDT 15m)
Sep 27 06:56:41 Trading-Agent python[1756130]: [backtest] dati da cache: 111313 candele (WLDUSDT 15m)
Sep 27 06:56:42 Trading-Agent python[1756172]: [backtest] dati da cache: 119169 candele (SUIUSDT 15m)
Sep 27 06:56:42 Trading-Agent python[1756214]: [backtest] dati da cache: 87023 candele (ENAUSDT 15m)
Sep 27 06:56:45 Trading-Agent python[1756193]: [backtest] dati da cache: 37411 candele (QUSDT 15m)
Sep 27 06:57:38 Trading-Agent python[1756193]: [backtest] dati da cache: 86151 candele (TAOUSDT 15m)
Sep 27 06:58:03 Trading-Agent python[1756109]: [backtest] dati da cache: 46423 candele (HYPEUSDT 15m)
Sep 27 06:58:41 Trading-Agent python[1756214]: [backtest] dati da cache: 165985 candele (DOGEUSDT 15m)
Sep 27 06:58:57 Trading-Agent python[1756130]: [backtest] dati da cache: 165985 candele (UNIUSDT 15m)
Sep 27 06:59:01 Trading-Agent python[1756109]: [backtest] dati da cache: 165985 candele (FILUSDT 15m)
Sep 27 06:59:15 Trading-Agent python[1756172]: [backtest] dati da cache: 165985 candele (LINKUSDT 15m)
Sep 27 06:59:17 Trading-Agent python[1756193]: [backtest] dati da cache: 118975 candele (1000PEPEUSDT 15m)
Sep 27 06:59:48 Trading-Agent python[1756151]: [backtest] dati da cache: 165985 candele (DASHUSDT 15m)
Sep 27 07:01:28 Trading-Agent python[1756193]: [backtest] dati da cache: 165985 candele (AVAXUSDT 15m)
Sep 27 07:01:45 Trading-Agent python[1756214]: [backtest] dati da cache: 165985 candele (LTCUSDT 15m)
Sep 27 07:02:22 Trading-Agent python[1756130]: [backtest] dati da cache: 61011 candele (PHAUSDT 15m)
Sep 27 07:02:23 Trading-Agent python[1756172]: [backtest] dati da cache: 165985 candele (ADAUSDT 15m)
Sep 27 07:02:25 Trading-Agent python[1756109]: [backtest] dati da cache: 165985 candele (BNBUSDT 15m)
Sep 27 07:03:26 Trading-Agent python[1756151]: [backtest] dati da cache: 94029 candele (ONDOUSDT 15m)
Sep 27 07:03:42 Trading-Agent python[1756130]: [backtest] dati da cache: 123109 candele (ARBUSDT 15m)
Sep 27 07:04:49 Trading-Agent python[1756193]: [backtest] dati da cache: 42499 candele (PUMPUSDT 15m)
Sep 27 07:05:05 Trading-Agent python[1756214]: [backtest] dati da cache: 38363 candele (XPLUSDT 15m)
Sep 27 07:05:11 Trading-Agent python[1756151]: [backtest] dati da cache: 34415 candele (2ZUSDT 15m)
Sep 27 07:05:12 Trading-Agent python[1756151]: [backtest] dati da cache: 53514 candele (MUBARAKUSDT 15m)
Sep 27 07:05:22 Trading-Agent python[1756172]: [backtest] dati da cache: 165985 candele (AAVEUSDT 15m)
Sep 27 07:05:40 Trading-Agent python[1756109]: [backtest] dati da cache: 10888 candele (BTWUSDT 15m)
Sep 27 07:05:44 Trading-Agent python[1756109]: [backtest] dati da cache: 165985 candele (BCHUSDT 15m)
Sep 27 07:05:44 Trading-Agent python[1756193]: [backtest] dati da cache: 53230 candele (BRUSDT 15m)
Sep 27 07:05:53 Trading-Agent python[1756130]: [backtest] dati da cache: 59085 candele (TRUMPUSDT 15m)
Sep 27 07:05:54 Trading-Agent python[1756214]: [backtest] dati da cache: 19059 candele (龙虾USDT 15m)
Sep 27 07:05:54 Trading-Agent python[1756214]: [backtest] dati da cache: 2362 candele (MARSCOINUSDT 15m)
Sep 27 07:05:57 Trading-Agent python[1756214]: [backtest] dati da cache: 165985 candele (DOTUSDT 15m)
Sep 27 07:06:15 Trading-Agent python[1756151]: [backtest] dati da cache: 27606 candele (USUSDT 15m)
Sep 27 07:06:17 Trading-Agent python[1756151]: [backtest] dati da cache: 105831 candele (ARKUSDT 15m)
Sep 27 07:06:39 Trading-Agent python[1756193]: [backtest] dati da cache: 47199 candele (SOONUSDT 15m)
Sep 27 07:07:02 Trading-Agent python[1756130]: [backtest] dati da cache: 166081 candele (RUNEUSDT 15m)
Sep 27 07:07:34 Trading-Agent python[1756193]: [backtest] dati da cache: 129399 candele (FETUSDT 15m)
Sep 27 07:08:08 Trading-Agent python[1756151]: [backtest] dati da cache: 34991 candele (AKEUSDT 15m)
Sep 27 07:08:11 Trading-Agent python[1756151]: [backtest] dati da cache: 86359 candele (SAGAUSDT 15m)
Sep 27 07:08:48 Trading-Agent python[1756172]: [backtest] dati da cache: 165985 candele (XLMUSDT 15m)
Sep 27 07:09:04 Trading-Agent python[1756109]: [backtest] dati da cache: 62144 candele (PENGUUSDT 15m)
Sep 27 07:09:05 Trading-Agent python[1756214]: [backtest] dati da cache: 93640 candele (LSKUSDT 15m)
```
