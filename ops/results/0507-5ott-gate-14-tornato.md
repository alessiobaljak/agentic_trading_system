# 0507-5ott-gate-14-tornato.req

_eseguito: 2026-10-05 12:10 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 05 11:28:12 Trading-Agent python[2151419]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Oct 05 11:28:12 Trading-Agent python[2151419]: [cervello] keep del lock scelto dal gate: 0.35 x12 · 0.5 x14 · 0.65 x36 · 0.75 x1 (dal paper per strategia x0)
Oct 05 11:28:12 Trading-Agent python[2151419]: [cervello] ipotesi scala_stretta: 1 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Oct 05 11:28:12 Trading-Agent python[2151419]: [cervello] declassate: 173 (nuove 0, tornate piene 0) · contatori fermi: giro solo urgenti · validate bocciate nel giro 13 · passate solo con la propria configurazione 1
Oct 05 11:28:12 Trading-Agent python[2151419]: [discover] GIRO FINITO in 2h 10m (24800 valutazioni, 63 passate)
Oct 05 11:28:12 Trading-Agent python[2151419]: [gate-storia] 2054 coppie + riga del giro in data/gate_storia/2026-10.jsonl (126 KiB)
Oct 05 11:28:14 Trading-Agent python[2151419]: [gate-doc] dashboard/gate scritto: finito (solo urgenti, 111 KiB)
Oct 05 11:28:14 Trading-Agent python[2151419]: ============================================================
Oct 05 11:28:14 Trading-Agent python[2151419]: [discover] 24800 valutazioni, 63 coppie nuove passate in QUESTO run.
Oct 05 11:28:14 Trading-Agent python[2151419]: [discover] coppie validate totali nel registro (base+generate): 235
Oct 05 11:28:14 Trading-Agent python[2151419]: ============================================================
Oct 05 11:28:17 Trading-Agent python[2151419]:   - Semafori: sistema verde, paper giallo.
Oct 05 11:28:17 Trading-Agent python[2151419]:   - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,73 vs 2,00 atteso
Oct 05 11:28:17 Trading-Agent python[2151419]:   - Anomalia SENZA_PROMESSA: 121 validate su 235 senza promessa (last_pf)
Oct 05 11:28:17 Trading-Agent python[2151419]:   - Riavvii del bot nelle 24 ore: 0.
Oct 05 11:28:17 Trading-Agent python[2151419]:   - Letture Firestore nelle 24 ore: 7730 (quota gratuita 50.000).
Oct 05 11:28:17 Trading-Agent python[2151419]:   - Spesa AI di ieri (2026-10-04): 0.10 $ in 1 chiamate — ai-learning 0.10 $
Oct 05 11:28:18 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Oct 05 11:28:18 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Oct 05 11:28:18 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 13h 47min 6.865s CPU time.
Oct 05 12:05:21 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Oct 05 12:05:23 Trading-Agent python[2158963]: [firebase] connesso (Firestore + RTDB)
Oct 05 12:05:24 Trading-Agent python[2158963]: [optimize] universo: top 200 per volume -> 200 coin
Oct 05 12:05:24 Trading-Agent python[2158963]: [optimize] shard 0/1: 200/200 coin
Oct 05 12:05:24 Trading-Agent python[2158963]: [optimize] strategie BASE saltate (OPTIMIZER_SKIP_BASE): 0 validate su 1312 valutazioni nella storia del registro — il calcolo va alla discovery. Faccio solo la manutenzione del registro.
Oct 05 12:05:25 Trading-Agent python[2158963]: [optimize] registro: 235 validate · copertura 38.5%
Oct 05 12:05:26 Trading-Agent python[2158963]: [optimize] passata extra: discovery a 1h su 30 coin (auto30: 5 fisse + 25 con coppie a 1h + 0 con validate + 0 top volume) (max 40 min) · ~12 min stimati: 2 min per 5 coin misurati il 26 set
Oct 05 12:05:26 Trading-Agent python[2158963]: [optimize] passata extra: coin BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT,BCHUSDT,AVAAIUSDT,BANKUSDT,BICOUSDT,BULLAUSDT,CVCUSDT,DEXEUSDT,DOTUSDT,GPSUSDT,HEIUSDT,HEMIUSDT,HUMAUSDT,IDUSDT,JTOUSDT,MUBARAKUSDT,ORCAUSDT,QUSDT,SAHARAUSDT,SKYAIUSDT,SPXUSDT,STXUSDT,SYRUPUSDT,TAUSDT,TRUMPUSDT,UBUSDT,USELESSUSDT
Oct 05 12:05:28 Trading-Agent python[2159011]: [firebase] connesso (Firestore + RTDB)
Oct 05 12:05:29 Trading-Agent python[2159011]: [discover] prove del paper passate all'AI:
Oct 05 12:05:29 Trading-Agent python[2159011]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Oct 05 12:05:29 Trading-Agent python[2159011]: - PAPER (vissuto, 283 trade chiusi): profit factor 0.733 contro 2.002 promesso dal gate.
Oct 05 12:05:29 Trading-Agent python[2159011]: - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Oct 05 12:05:29 Trading-Agent python[2159011]: - Direzione long: 137 trade, 76 vinti, PnL -36.92.
Oct 05 12:05:29 Trading-Agent python[2159011]: - Direzione short: 158 trade, 92 vinti, PnL -39.76.
Oct 05 12:05:29 Trading-Agent python[2159011]: - GATE (giro precedente a 1h, finito il 05/10 09:18 UTC): su 11760 valutazioni coin x strategia ne passano 277; muoiono soprattutto su recovery 1897 · total_return 6772 · regime 1518 · trades 315.
Oct 05 12:05:29 Trading-Agent python[2159011]: [discover] idee AI e autopsia SPENTE (AI_HYPOTHESES_ENABLED=false, 2 ott 2026)
Oct 05 12:05:30 Trading-Agent python[2159011]: [cervello] sessione oraria: 128 spec note su 1043 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] varianti dai referti SPENTE (DISCOVERY_VARIANTI_REFERTI=false, 2 ott 2026)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] rivalutazione completa: 985 spec note su 1043
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] semi: 2 da coin NON coperte (su 77 gia' coperte)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] 30 semi dai quasi-passaggi del run precedente
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] 4 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su IDUSDT: 3 coppie con la stessa logica (gen_6bc43e03, gen_c5430258, gen_dd9238bf)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_c61d9322, gen_4cadc09b)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] 397 candidate (985 con conferme ri-validate + 0 altre, 58 tagliate su 1043 note) seed=1927 2022-01-01->2026-10-05
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] universo RISTRETTO a 30 coin (--symbols)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] filtro AI dell'universo saltato: elenco scelto apposta (--symbols), 30 coin tenute tutte
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] shard 0/1: 30/30 coin
Oct 05 12:05:30 Trading-Agent python[2159011]: [parallel] worker ridotti da 8 a 6: 14.4 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Oct 05 12:05:30 Trading-Agent python[2159011]: [discover] 30 coin x 397 spec su 6 worker (core)
Oct 05 12:05:31 Trading-Agent python[2159011]: [paper] 115 verdetti trailing (55 prematuri, 60 protetti) -> nessun candidato in piu' (sotto il 60%)
Oct 05 12:05:31 Trading-Agent python[2159011]: [paper] 295 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Oct 05 12:05:31 Trading-Agent python[2159011]: [paper] scale per strategia dal vissuto: 15 strategie con >= 5 trade (es. gen_18c839a0 -> 1/1.5/2.25)
Oct 05 12:05:31 Trading-Agent python[2159011]: [paper] keep per strategia dal vissuto: 1 strategie con >= 5 verdetti trailing (es. gen_e59ad90b -> 0.75, protetti 3/5) · tragitto lasciato sul tavolo medio 0.72 del tragitto entry->TP su 129 trade
Oct 05 12:05:32 Trading-Agent python[2159124]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:32 Trading-Agent python[2159145]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:32 Trading-Agent python[2159061]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:32 Trading-Agent python[2159103]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:32 Trading-Agent python[2159082]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:32 Trading-Agent python[2159166]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:57 Trading-Agent python[2159166]: [backtest] dati da cache: 41713 candele (BTCUSDT 1h)
Oct 05 12:05:57 Trading-Agent python[2159082]: [backtest] dati da cache: 41713 candele (SOLUSDT 1h)
Oct 05 12:05:57 Trading-Agent python[2159061]: [backtest] dati da cache: 41713 candele (ETHUSDT 1h)
Oct 05 12:05:58 Trading-Agent python[2159124]: [backtest] dati da cache: 41713 candele (ADAUSDT 1h)
Oct 05 12:05:58 Trading-Agent python[2159145]: [backtest] dati da cache: 14988 candele (AVAAIUSDT 1h)
Oct 05 12:05:58 Trading-Agent python[2159103]: [backtest] dati da cache: 41713 candele (BCHUSDT 1h)
Oct 05 12:07:20 Trading-Agent python[2159145]: [backtest] dati da cache: 12823 candele (BANKUSDT 1h)
Oct 05 12:09:15 Trading-Agent python[2159145]: [backtest] dati da cache: 26437 candele (BICOUSDT 1h)
Oct 05 12:09:39 Trading-Agent python[2159103]: [backtest] dati da cache: 10960 candele (BULLAUSDT 1h)
Oct 05 12:09:40 Trading-Agent python[2159082]: [backtest] dati da cache: 12137 candele (CVCUSDT 1h)
Oct 05 12:09:42 Trading-Agent python[2159166]: [backtest] dati da cache: 15566 candele (DEXEUSDT 1h)
Oct 05 12:10:17 Trading-Agent python[2159061]: [backtest] dati da cache: 41689 candele (DOTUSDT 1h)
```
