# 0464-3ott-pomeriggio-log-gate.req

_eseguito: 2026-10-03 14:50 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] MUSDT: 1 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] MUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] LAYERUSDT: worker rss 2449 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] USUALUSDT: worker rss 2441 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] GUNUSDT: worker rss 2450 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] REZUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] KERNELUSDT: 1 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] KERNELUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PTBUSDT: 2 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PTBUSDT: worker rss 2450 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] HUSDT: 3 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] HUSDT: worker rss 2449 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] ARKMUSDT: worker rss 2441 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] POPCATUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] BSVUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] AKTUSDT: worker rss 2450 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] KMNOUSDT: worker rss 2347 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] MOODENGUSDT: worker rss 2449 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] HOLOUSDT: 1 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] HOLOUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] BLESSUSDT: worker rss 2450 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] DYMUSDT: worker rss 2347 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] KASUSDT: worker rss 2449 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PORTALUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] API3USDT: worker rss 2441 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] USTCUSDT: worker rss 2450 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] CUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] FUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] ALCHUSDT: worker rss 2347 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PLAYUSDT: 1 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PLAYUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] DEEPUSDT: worker rss 2449 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] AVNTUSDT: 1 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] AVNTUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] XVGUSDT: worker rss 2450 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] SNXUSDT: worker rss 2447 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PIPPINUSDT: 1 coppie passate ✅
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] PIPPINUSDT: worker rss 2347 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] MERLUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] 1000000BOBUSDT: worker rss 2449 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] AXLUSDT: worker rss 2441 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [discover] CARVUSDT: worker rss 2454 MB
Oct 03 10:52:13 Trading-Agent python[2061295]: [selettore] 5013 righe (43 coppie) -> data/selettore/2026-10-03_15m.w*.jsonl
Oct 03 10:52:13 Trading-Agent python[2061295]: [controllo-gruppi] salvate 50 bocciate su 17953 idonee (seme 131536746) · foto conferme: già fatta oggi [15m]
Oct 03 10:52:13 Trading-Agent python[2061295]: [autopsy] 43/19513 passate · muoiono su: total_return 16127 · regime 1124 · recovery 1036 · trades 837 · consistency 214
Oct 03 10:52:13 Trading-Agent python[2061295]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 36
Oct 03 10:52:14 Trading-Agent python[2061295]: [cervello] esplorative: 39 attive (0 nuove), validate poi 2, scartate 300
Oct 03 10:52:14 Trading-Agent python[2061295]: [cervello] intorno: 0 madri riprovate / 0 figlie passate / 0 promosse / 0 senza margine / 0 con madre non valutata / 0 senza conferme retroattive o seconde figlie
Oct 03 10:52:14 Trading-Agent python[2061295]: [cervello] varianti dai referti: 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni: nessuna
Oct 03 10:52:14 Trading-Agent python[2061295]: [cervello] keep del lock scelto dal gate: 0.35 x8 · 0.5 x9 · 0.65 x24 · 0.75 x2
Oct 03 10:52:14 Trading-Agent python[2061295]: [cervello] ipotesi scala_stretta: 0 strategie rigiudicate con la loro scala dal vissuto (0 con almeno 5 trade con mfe e una scala propria)
Oct 03 10:52:14 Trading-Agent python[2061295]: [cervello] declassate: 173 (nuove 0, tornate piene 0) · contatori fermi: giro solo urgenti · validate bocciate nel giro 4 · passate solo con la propria configurazione 1
Oct 03 10:52:14 Trading-Agent python[2061295]: [discover] GIRO FINITO in 2h 41m (19513 valutazioni, 43 passate)
Oct 03 10:52:15 Trading-Agent python[2061295]: [gate-storia] 1888 coppie + riga del giro in data/gate_storia/2026-10.jsonl (114 KiB)
Oct 03 10:52:15 Trading-Agent python[2061295]: [gate-doc] dashboard/gate scritto: finito (solo urgenti, 102 KiB)
Oct 03 10:52:15 Trading-Agent python[2061295]: ============================================================
Oct 03 10:52:15 Trading-Agent python[2061295]: [discover] 19513 valutazioni, 43 coppie nuove passate in QUESTO run.
Oct 03 10:52:15 Trading-Agent python[2061295]: [discover] coppie validate totali nel registro (base+generate): 216
Oct 03 10:52:15 Trading-Agent python[2061295]: ============================================================
Oct 03 10:52:26 Trading-Agent python[2061295]:   - Semafori: sistema verde, paper giallo.
Oct 03 10:52:26 Trading-Agent python[2061295]:   - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,72 vs 2,01 atteso
Oct 03 10:52:26 Trading-Agent python[2061295]:   - Anomalia SENZA_PROMESSA: 123 validate su 216 senza promessa (last_pf)
Oct 03 10:52:26 Trading-Agent python[2061295]:   - Riavvii del bot nelle 24 ore: 0.
Oct 03 10:52:26 Trading-Agent python[2061295]:   - Letture Firestore nelle 24 ore: 7280 (quota gratuita 50.000).
Oct 03 10:52:26 Trading-Agent python[2061295]:   - Spesa AI di ieri (2026-10-02): 1.86 $ in 29 chiamate — ai-hypotheses 1.37 $, ai-autopsia 0.49 $, ai-connettivita 0.00 $
Oct 03 10:52:27 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Oct 03 10:52:27 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Oct 03 10:52:27 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 10h 47min 55.609s CPU time.
Oct 03 12:05:01 Trading-Agent systemd[1]: Starting trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)...
Oct 03 12:05:02 Trading-Agent python[2066971]: [gate] giro delle 12:00 UTC SALTATO: al suo posto lavora R1 (il gate rigiocato nel passato, si' del proprietario del 1 ott). Il prossimo giro e' fra 3 ore; il gate torna a 8 giri al giorno quando R1 finisce (file /root/agentic_trading_system/data/replay_gate/attivo).
Oct 03 12:05:04 Trading-Agent python[2066984]: [gate] giro delle 12:00 UTC SALTATO: al suo posto lavora R1 (il gate rigiocato nel passato, si' del proprietario del 1 ott). Il prossimo giro e' fra 3 ore; il gate torna a 8 giri al giorno quando R1 finisce (file /root/agentic_trading_system/data/replay_gate/attivo).
Oct 03 12:05:07 Trading-Agent python[2066984]:   - Semafori: sistema verde, paper giallo.
Oct 03 12:05:07 Trading-Agent python[2066984]:   - Anomalia FRENO_GLOBALE: freno globale da deriva: PF 0,73 vs 2,01 atteso
Oct 03 12:05:07 Trading-Agent python[2066984]:   - Anomalia SENZA_PROMESSA: 123 validate su 216 senza promessa (last_pf)
Oct 03 12:05:07 Trading-Agent python[2066984]:   - Riavvii del bot nelle 24 ore: 0.
Oct 03 12:05:07 Trading-Agent python[2066984]:   - Letture Firestore nelle 24 ore: 7362 (quota gratuita 50.000).
Oct 03 12:05:07 Trading-Agent python[2066984]:   - Spesa AI di ieri (2026-10-02): 1.86 $ in 29 chiamate — ai-hypotheses 1.37 $, ai-autopsia 0.49 $, ai-connettivita 0.00 $
Oct 03 12:05:07 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Oct 03 12:05:07 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Oct 03 12:05:07 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 7.134s CPU time.
```
