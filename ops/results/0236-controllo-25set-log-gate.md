# 0236-controllo-25set-log-gate.req

_eseguito: 2026-09-25 06:10 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] CROSSUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] PORTALUSDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] EPICUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] RSRUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] REZUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] THEUSDT: 1 coppie passate ✅
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] THEUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] SOPHUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] PUNDIXUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] GRIFFAINUSDT: worker rss 2283 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] TAUSDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] WALUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] OPENUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] PARTIUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] XPINUSDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] NEOUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] BMTUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] MTLUSDT: worker rss 2283 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] API3USDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] MAVIAUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] UBUSDT: 2 coppie passate ✅
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] UBUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] REDUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] WUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] ASTRUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] AXLUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] IDUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] IDOLUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] BERAUSDT: worker rss 2283 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] AINUSDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] BRETTUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] HIVEUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] DRIFTUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] BABYUSDT: worker rss 2283 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] ACHUSDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] MUSDT: 1 coppie passate ✅
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] MUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] USUALUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] GUNUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] USTCUSDT: worker rss 2283 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] CUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] FUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] JSTUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] ALCHUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] POPCATUSDT: worker rss 2278 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] RUNEUSDT: worker rss 2287 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] CARVUSDT: worker rss 2276 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] AGTUSDT: worker rss 2282 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] AKTUSDT: worker rss 2281 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [discover] HOLOUSDT: worker rss 2283 MB
Sep 25 04:40:12 Trading-Agent python[1658691]: [selettore] 1558 righe (18 coppie) -> data/selettore/2026-09-25_15m.w*.jsonl
Sep 25 04:40:12 Trading-Agent python[1658691]: [autopsy] 18/16330 passate · muoiono su: total_return 14382 · recovery 808 · regime 512 · trades 285 · pf_ex_top 163
Sep 25 04:40:12 Trading-Agent python[1658691]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 36
Sep 25 04:40:13 Trading-Agent python[1658691]: [discover] GIRO FINITO in 1h 9m (16330 valutazioni, 18 passate)
Sep 25 04:40:13 Trading-Agent python[1658691]: ============================================================
Sep 25 04:40:13 Trading-Agent python[1658691]: [discover] 16330 valutazioni, 18 coppie nuove passate in QUESTO run.
Sep 25 04:40:13 Trading-Agent python[1658691]: [discover] coppie validate totali nel registro (base+generate): 160
Sep 25 04:40:13 Trading-Agent python[1658691]: ============================================================
Sep 25 04:40:14 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Sep 25 04:40:14 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Sep 25 04:40:14 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 6h 44min 31.834s CPU time.
Sep 25 06:09:41 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Sep 25 06:09:43 Trading-Agent python[1664534]: [firebase] connesso (Firestore + RTDB)
Sep 25 06:09:44 Trading-Agent python[1664534]: [optimize] universo: top 200 per volume -> 200 coin
Sep 25 06:09:44 Trading-Agent python[1664534]: [optimize] shard 0/1: 200/200 coin
Sep 25 06:09:44 Trading-Agent python[1664534]: [optimize] strategie BASE saltate (OPTIMIZER_SKIP_BASE): 0 validate su 1312 valutazioni nella storia del registro — il calcolo va alla discovery. Faccio solo la manutenzione del registro.
Sep 25 06:09:45 Trading-Agent python[1664534]: [registry] BASE STANTIE: rimosse 16 coppie di coin uscite dall'universo da oltre 6 giorni. Senza questo il registro cresce senza limite e soffoca le generate.
Sep 25 06:09:45 Trading-Agent python[1664534]: [optimize] registro: 160 validate · copertura 26.0%
Sep 25 06:09:45 Trading-Agent python[1664534]: [optimize] passata extra: discovery a 1h su BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT,BCHUSDT (max 40 min)
Sep 25 06:09:47 Trading-Agent python[1664560]: [firebase] connesso (Firestore + RTDB)
Sep 25 06:09:47 Trading-Agent python[1664560]: [discover] prove del paper passate all'AI:
Sep 25 06:09:47 Trading-Agent python[1664560]: Prove misurate finora (campioni piccoli: sono indizi, non leggi).
Sep 25 06:09:47 Trading-Agent python[1664560]: - PAPER (vissuto, 55 trade chiusi): profit factor 0.62 contro 1.887 promesso dal gate.
Sep 25 06:09:47 Trading-Agent python[1664560]: - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
Sep 25 06:09:47 Trading-Agent python[1664560]: - Direzione long: 24 trade, 9 vinti, PnL -17.93.
Sep 25 06:09:47 Trading-Agent python[1664560]: - Direzione short: 31 trade, 14 vinti, PnL -32.19.
Sep 25 06:09:47 Trading-Agent python[1664560]: - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su trades 6 · total_return 1207 · pf_ex_top 3 · holdout 1.
Sep 25 06:10:04 Trading-Agent python[1664560]: [ai-autopsia] ok in 16.6s · 3284+803 token
Sep 25 06:10:04 Trading-Agent python[1664560]: [ai-autopsia] schema: Quasi tutti i quasi-passaggi sono strategie mean-reversion su timeframe 15m che combinano oscillatori (rsi_extreme, stoch_extreme) con filtri di sessione (hour 8-16) o trend_strength/adx; le coin sono in gran parte alt a bassa/media capitalizzazione (VELVET, CROSS, AIN, DEXE, SCR) piu' qualche major
Sep 25 06:10:04 Trading-Agent python[1664560]: [ai-autopsia] consigli: Puntare su setup con piu' trade (mirare a >100-150 anche in holdout) per stabilizzare le metriche vicine a soglia, e verificare che il PF non dipenda da pochi outlier riducendo il peso dei trade estremi (position sizing/limiti). Per il template rsi_extreme+stoch_extreme+session, provare a estenderlo
```
