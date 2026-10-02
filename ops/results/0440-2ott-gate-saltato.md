# 0440-2ott-gate-saltato.req

_eseguito: 2026-10-02 12:48 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] USUALUSDT: worker rss 2449 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] GUNUSDT: worker rss 2443 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] KERNELUSDT: 1 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] KERNELUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] PTBUSDT: worker rss 2445 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] HUSDT: worker rss 2448 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] ARKMUSDT: worker rss 2449 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] POPCATUSDT: worker rss 2445 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] BSVUSDT: 1 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] BSVUSDT: worker rss 2443 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] TAKEUSDT: 1 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] TAKEUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] AKTUSDT: 1 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] AKTUSDT: worker rss 2448 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] MOODENGUSDT: worker rss 2451 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] HOLOUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] BLESSUSDT: 1 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] BLESSUSDT: worker rss 2445 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] PORTALUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] BICOUSDT: worker rss 2448 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] WUSDT: worker rss 2449 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] CUSDT: worker rss 2445 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] FUSDT: worker rss 2443 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] JSTUSDT: worker rss 2451 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] ALCHUSDT: worker rss 2445 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] PLAYUSDT: worker rss 2443 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] DYMUSDT: 2 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] DYMUSDT: worker rss 2451 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] SPKUSDT: 1 coppie passate ✅
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] SPKUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] DEEPUSDT: worker rss 2449 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] AVNTUSDT: worker rss 2448 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] XVGUSDT: worker rss 2443 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] SNXUSDT: worker rss 2445 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] PIPPINUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] MERLUSDT: worker rss 2448 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] EGLDUSDT: worker rss 2449 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] API3USDT: worker rss 2451 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] AXLUSDT: worker rss 2448 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] USTCUSDT: worker rss 2450 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [discover] CARVUSDT: worker rss 2443 MB
Oct 02 11:12:58 Trading-Agent python[2011477]: [selettore] 3529 righe (38 coppie) -> data/selettore/2026-10-02_15m.w*.jsonl
Oct 02 11:12:58 Trading-Agent python[2011477]: [controllo-gruppi] salvate 50 bocciate su 20203 idonee (seme 1044048553) · foto conferme: già fatta oggi [15m]
Oct 02 11:12:58 Trading-Agent python[2011477]: [autopsy] 38/22448 passate · muoiono su: total_return 18748 · recovery 1234 · regime 1093 · trades 863 · consistency 249
Oct 02 11:12:58 Trading-Agent python[2011477]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 27
Oct 02 11:12:59 Trading-Agent python[2011477]: [discover] 4 varianti passate solo con i dati di oggi (o seconde figlie): scartate, non entrano nel registro
Oct 02 11:13:00 Trading-Agent python[2011477]: [cervello] esplorative: 31 attive (1 nuove), validate poi 0, scartate 261
Oct 02 11:13:00 Trading-Agent python[2011477]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Oct 02 11:13:00 Trading-Agent python[2011477]: [cervello] varianti dai referti: 3 create / 4 passate / 0 con conferme retroattive / 0 promosse / 4 scartate / sostituzioni: nessuna
Oct 02 11:13:00 Trading-Agent python[2011477]: [cervello] keep del lock scelto dal gate: 0.35 x2 · 0.5 x4 · 0.65 x28
Oct 02 11:13:00 Trading-Agent python[2011477]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Oct 02 11:13:00 Trading-Agent python[2011477]: [cervello] declassate: 163 (nuove 0, tornate piene 0) · contatori fermi: giro solo urgenti · validate bocciate nel giro 9 · passate solo con la propria configurazione 0
Oct 02 11:13:00 Trading-Agent python[2011477]: [discover] GIRO FINITO in 2h 2m (22448 valutazioni, 34 passate)
Oct 02 11:13:00 Trading-Agent python[2011477]: [gate-storia] 1793 coppie + riga del giro in data/gate_storia/2026-10.jsonl (108 KiB)
Oct 02 11:13:01 Trading-Agent python[2011477]: [gate-doc] dashboard/gate scritto: finito (solo urgenti, 99 KiB)
Oct 02 11:13:01 Trading-Agent python[2011477]: ============================================================
Oct 02 11:13:01 Trading-Agent python[2011477]: [discover] 22448 valutazioni, 34 coppie nuove passate in QUESTO run.
Oct 02 11:13:01 Trading-Agent python[2011477]: [discover] coppie validate totali nel registro (base+generate): 212
Oct 02 11:13:01 Trading-Agent python[2011477]: ============================================================
Oct 02 11:13:05 Trading-Agent python[2011477]:   - Semafori: sistema verde, paper giallo.
Oct 02 11:13:05 Trading-Agent python[2011477]:   - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,71 vs 2,02 atteso
Oct 02 11:13:05 Trading-Agent python[2011477]:   - Anomalia SENZA_PROMESSA: 123 validate su 212 senza promessa (last_pf)
Oct 02 11:13:05 Trading-Agent python[2011477]:   - Riavvii del bot nelle 24 ore: 2.
Oct 02 11:13:05 Trading-Agent python[2011477]:   - Letture Firestore nelle 24 ore: 1479 (quota gratuita 50.000).
Oct 02 11:13:05 Trading-Agent python[2011477]:   - Spesa AI di ieri (2026-10-01): 2.07 $ in 31 chiamate — ai-hypotheses 1.53 $, ai-autopsia 0.55 $
Oct 02 11:13:05 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Oct 02 11:13:05 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Oct 02 11:13:05 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 12h 46min 15.367s CPU time.
Oct 02 12:09:30 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Oct 02 12:09:31 Trading-Agent python[2016637]: [gate] giro delle 12:00 UTC SALTATO: al suo posto lavora R1 (il gate rigiocato nel passato, si' del proprietario del 1 ott). Il prossimo giro e' fra 3 ore; il gate torna a 8 giri al giorno quando R1 finisce (file /root/agentic_trading_system/data/replay_gate/attivo).
Oct 02 12:09:32 Trading-Agent python[2016646]: [gate] giro delle 12:00 UTC SALTATO: al suo posto lavora R1 (il gate rigiocato nel passato, si' del proprietario del 1 ott). Il prossimo giro e' fra 3 ore; il gate torna a 8 giri al giorno quando R1 finisce (file /root/agentic_trading_system/data/replay_gate/attivo).
Oct 02 12:09:35 Trading-Agent python[2016646]:   - Semafori: sistema verde, paper giallo.
Oct 02 12:09:35 Trading-Agent python[2016646]:   - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,71 vs 2,03 atteso
Oct 02 12:09:35 Trading-Agent python[2016646]:   - Anomalia SENZA_PROMESSA: 123 validate su 212 senza promessa (last_pf)
Oct 02 12:09:35 Trading-Agent python[2016646]:   - Riavvii del bot nelle 24 ore: 2.
Oct 02 12:09:35 Trading-Agent python[2016646]:   - Letture Firestore nelle 24 ore: 1734 (quota gratuita 50.000).
Oct 02 12:09:35 Trading-Agent python[2016646]:   - Spesa AI di ieri (2026-10-01): 2.07 $ in 31 chiamate — ai-hypotheses 1.53 $, ai-autopsia 0.55 $
Oct 02 12:09:35 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Oct 02 12:09:35 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Oct 02 12:09:35 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 5.215s CPU time.
```
