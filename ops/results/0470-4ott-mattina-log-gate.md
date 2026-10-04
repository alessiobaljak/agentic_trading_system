# 0470-4ott-mattina-log-gate.req

_eseguito: 2026-10-04 06:05 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 04 05:38:40 Trading-Agent python[2093503]: [selettore] 1864 righe (25 coppie) -> data/selettore/2026-10-04_15m.w*.jsonl
Oct 04 05:38:41 Trading-Agent python[2093503]: [controllo-gruppi] salvate 50 bocciate su 18728 idonee (seme 166552515) · foto conferme: già fatta oggi [15m]
Oct 04 05:38:41 Trading-Agent python[2093503]: [autopsy] 25/20667 passate · muoiono su: total_return 16684 · trades 1330 · regime 1098 · recovery 1078 · consistency 255
Oct 04 05:38:41 Trading-Agent python[2093503]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 32
Oct 04 05:38:42 Trading-Agent python[2093503]: [cervello] esplorative: 48 attive (12 nuove), validate poi 3, scartate 327
Oct 04 05:38:42 Trading-Agent python[2093503]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Oct 04 05:38:42 Trading-Agent python[2093503]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Oct 04 05:38:42 Trading-Agent python[2093503]: [cervello] keep del lock scelto dal gate: 0.35 x5 · 0.5 x4 · 0.65 x16
Oct 04 05:38:42 Trading-Agent python[2093503]: [cervello] ipotesi scala_stretta: 1 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Oct 04 05:38:42 Trading-Agent python[2093503]: [cervello] declassate: 169 (nuove 0, tornate piene 0) · contatori fermi: giro solo urgenti · validate bocciate nel giro 2 · passate solo con la propria configurazione 0
Oct 04 05:38:42 Trading-Agent python[2093503]: [discover] GIRO FINITO in 2h 45m (20667 valutazioni, 25 passate)
Oct 04 05:38:42 Trading-Agent python[2093503]: [gate-storia] 1947 coppie + riga del giro in data/gate_storia/2026-10.jsonl (119 KiB)
Oct 04 05:38:43 Trading-Agent python[2093503]: [gate-doc] dashboard/gate scritto: finito (solo urgenti, 105 KiB)
Oct 04 05:38:43 Trading-Agent python[2093503]: ============================================================
Oct 04 05:38:43 Trading-Agent python[2093503]: [discover] 20667 valutazioni, 25 coppie nuove passate in QUESTO run.
Oct 04 05:38:43 Trading-Agent python[2093503]: [discover] coppie validate totali nel registro (base+generate): 223
Oct 04 05:38:43 Trading-Agent python[2093503]: ============================================================
Oct 04 05:38:54 Trading-Agent python[2093503]:   - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,76 vs 2,00 atteso
Oct 04 05:38:54 Trading-Agent python[2093503]:   - Anomalia GATE_SFORA: il giro del gate e' durato 3 h 09 (piu' di 3 h)
Oct 04 05:38:54 Trading-Agent python[2093503]:   - Anomalia SENZA_PROMESSA: 122 validate su 223 senza promessa (last_pf)
Oct 04 05:38:54 Trading-Agent python[2093503]:   - Riavvii del bot nelle 24 ore: 0.
Oct 04 05:38:54 Trading-Agent python[2093503]:   - Letture Firestore nelle 24 ore: 7774 (quota gratuita 50.000).
Oct 04 05:38:54 Trading-Agent python[2093503]:   - Spesa AI di ieri (2026-10-03): nessun dato.
Oct 04 05:38:54 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Oct 04 05:38:54 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Oct 04 05:38:54 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 11h 15min 33.276s CPU time.
Oct 04 06:04:25 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Oct 04 06:04:27 Trading-Agent python[2097542]: [firebase] connesso (Firestore + RTDB)
Oct 04 06:04:28 Trading-Agent python[2097542]: [optimize] universo: top 200 per volume -> 200 coin
Oct 04 06:04:28 Trading-Agent python[2097542]: [optimize] shard 0/1: 200/200 coin
Oct 04 06:04:28 Trading-Agent python[2097542]: [optimize] strategie BASE saltate (OPTIMIZER_SKIP_BASE): 0 validate su 1312 valutazioni nella storia del registro — il calcolo va alla discovery. Faccio solo la manutenzione del registro.
Oct 04 06:04:29 Trading-Agent python[2097542]: [optimize] registro: 223 validate · copertura 38.0%
Oct 04 06:04:30 Trading-Agent python[2097542]: [optimize] passata extra: discovery a 1h su 30 coin (auto30: 5 fisse + 25 con coppie a 1h + 0 con validate + 0 top volume) (max 40 min) · ~12 min stimati: 2 min per 5 coin misurati il 26 set
Oct 04 06:04:30 Trading-Agent python[2097542]: [optimize] passata extra: coin BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT,BCHUSDT,AVAAIUSDT,BANKUSDT,BICOUSDT,BULLAUSDT,CVCUSDT,DEXEUSDT,DOTUSDT,GPSUSDT,HEIUSDT,HEMIUSDT,HUMAUSDT,IDUSDT,JTOUSDT,MUBARAKUSDT,ORCAUSDT,QUSDT,SAHARAUSDT,SKYAIUSDT,SPXUSDT,STXUSDT,SYRUPUSDT,TAUSDT,TRUMPUSDT,UBUSDT,USELESSUSDT
Oct 04 06:04:32 Trading-Agent python[2097575]: [firebase] connesso (Firestore + RTDB)
Oct 04 06:04:33 Trading-Agent python[2097575]: [discover] prove del paper passate all'AI:
Oct 04 06:04:33 Trading-Agent python[2097575]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Oct 04 06:04:33 Trading-Agent python[2097575]: - PAPER (vissuto, 254 trade chiusi): profit factor 0.759 contro 2.005 promesso dal gate.
Oct 04 06:04:33 Trading-Agent python[2097575]: - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Oct 04 06:04:33 Trading-Agent python[2097575]: - Direzione long: 125 trade, 68 vinti, PnL -35.19.
Oct 04 06:04:33 Trading-Agent python[2097575]: - Direzione short: 139 trade, 83 vinti, PnL -27.39.
Oct 04 06:04:33 Trading-Agent python[2097575]: - GATE (giro precedente a 1h, finito il 04/10 03:53 UTC): su 9840 valutazioni coin x strategia ne passano 218; muoiono soprattutto su total_return 5629 · consistency 466 · pf_ex_top 237 · recovery 1590.
Oct 04 06:04:33 Trading-Agent python[2097575]: [discover] idee AI e autopsia SPENTE (AI_HYPOTHESES_ENABLED=false, 2 ott 2026)
Oct 04 06:04:34 Trading-Agent python[2097575]: [cervello] sessione oraria: 122 spec note su 956 usano `session` (fino al 27 set valutata con l'orologio del giro, non della candela, e sceglieva il lato: dal 27 set filtro per i due lati, passaggi azzerati)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] varianti dai referti SPENTE (DISCOVERY_VARIANTI_REFERTI=false, 2 ott 2026)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] candidate casuali limitate a 40 (DISCOVERY_RANDOM_MAX=40): le altre fonti sono ragionate
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] rivalutazione completa: 900 spec note su 956
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] semi: 3 da coin NON coperte (su 76 gia' coperte)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] 30 semi dai quasi-passaggi del run precedente
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] 1 candidate scartate perche' gemelle di una spec gia' nota (stessa logica, id diverso)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su IDUSDT: 3 coppie con la stessa logica (gen_6bc43e03, gen_c5430258, gen_dd9238bf)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su USELESSUSDT: 2 coppie con la stessa logica (gen_194e2514, gen_1bb04e1a)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_c61d9322, gen_4cadc09b)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su SKYAIUSDT: 2 coppie con la stessa logica (gen_6cf80ae6, gen_c202787e)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su MUBARAKUSDT: 2 coppie con la stessa logica (gen_ff3e4154, gen_e933160c)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su TRUMPUSDT: 2 coppie con la stessa logica (gen_108c996b, gen_f156ca1b)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] GEMELLE gia' validate su HEMIUSDT: 2 coppie con la stessa logica (gen_6bc43e03, gen_c5430258)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] 334 candidate (900 con conferme ri-validate + 0 altre, 56 tagliate su 956 note) seed=93871 2022-01-01->2026-10-04
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] universo RISTRETTO a 30 coin (--symbols)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] filtro AI dell'universo saltato: elenco scelto apposta (--symbols), 30 coin tenute tutte
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] shard 0/1: 30/30 coin
Oct 04 06:04:34 Trading-Agent python[2097575]: [parallel] worker ridotti da 8 a 6: 14.4 GB disponibili, ~2 GB per worker (alza BACKTEST_MEM_PER_WORKER_GB se la stima e' pessimistica)
Oct 04 06:04:34 Trading-Agent python[2097575]: [discover] 30 coin x 334 spec su 6 worker (core)
Oct 04 06:04:35 Trading-Agent python[2097575]: [paper] 104 verdetti trailing (49 prematuri, 55 protetti) -> nessun candidato in piu' (sotto il 60%)
Oct 04 06:04:35 Trading-Agent python[2097575]: [paper] 264 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
Oct 04 06:04:35 Trading-Agent python[2097575]: [paper] scale per strategia dal vissuto: 13 strategie con >= 5 trade (es. gen_18c839a0 -> 1/1.5/2.25)
Oct 04 06:04:35 Trading-Agent python[2097575]: [paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing · tragitto lasciato sul tavolo medio 0.72 del tragitto entry->TP su 117 trade
Oct 04 06:04:36 Trading-Agent python[2097685]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:04:36 Trading-Agent python[2097727]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:04:36 Trading-Agent python[2097643]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:04:36 Trading-Agent python[2097706]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:04:36 Trading-Agent python[2097622]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:04:36 Trading-Agent python[2097664]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:05:00 Trading-Agent python[2097664]: [backtest] dati da cache: 41665 candele (BTCUSDT 1h)
Oct 04 06:05:00 Trading-Agent python[2097727]: [backtest] dati da cache: 41665 candele (ETHUSDT 1h)
Oct 04 06:05:00 Trading-Agent python[2097685]: [backtest] dati da cache: 41665 candele (SOLUSDT 1h)
Oct 04 06:05:01 Trading-Agent python[2097643]: [backtest] dati da cache: 41665 candele (ADAUSDT 1h)
Oct 04 06:05:01 Trading-Agent python[2097622]: [backtest] dati da cache: 41665 candele (BCHUSDT 1h)
Oct 04 06:05:01 Trading-Agent python[2097706]: [backtest] dati da cache: 14988 candele (AVAAIUSDT 1h)
```
