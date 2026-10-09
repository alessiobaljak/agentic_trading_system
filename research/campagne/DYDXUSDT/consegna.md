# DYDXUSDT — consegna della campagna

Protocollo 4.5 (approvato il 2026-10-09 alle 12:06 UTC). Sessione aperta dal coordinamento su delega.
Branch `research/campagna/DYDXUSDT`. Log: `log.jsonl`; idee: `ipotesi.md`; dati: `fase0_dati.md`.

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Il budget è stato usato per intero (30 varianti testate, avanzo 0). Una sola variante è diventata
candidato in Fase 2 (`DYDXUSDT-008`), ha superato tutte le verifiche della Fase 4, e in validazione ha
perso: 83 trade, R medio −0,178, p-value 0,968. Non passa l'asticella (esito provvisorio, lo conferma il
coordinamento al Passo 4). Nessun candidato va al vault.

## Periodi e dati

* Costruzione 2021-09-01 → 2023-04-19 (596 giorni), validazione 2023-04-20 → 2023-12-31. I dati veri
  partono il 2021-09-09/10: i primi 9 giorni della costruzione sono vuoti (dichiarato in Fase 0).
* Nessun mese sotto la liquidità minima; funding a 8 ore per tutto il periodo; due giorni interi senza
  mark price (2022-10-02, 2023-02-24) tolti dall'allineamento.
* Slippage della scheda 0,02% per lato: per il 2022 (volume medio 158 milioni) la fascia giusta sarebbe
  stata 0,05%; i costi della costruzione sono un po' ottimisti.

## Il candidato DYDXUSDT-008 (non validato)

**Regole complete** (`candidati/DYDXUSDT-008/regole.md`): DYDXUSDT, candele da 1 ora, solo long. Alla
chiusura dell'ora, se il rendimento orario di BTCUSDT supera 2 deviazioni standard dei suoi rendimenti
orari delle 168 ore precedenti e DYDX nella stessa ora è salita meno di BTC, long all'apertura dell'ora
dopo; stop a 2 ATR(14) orari dal close; nessun target; uscita dopo 3 ore. Rischio 1% per trade, leva
massima 2, margine isolated (regole del bot).

**Motivo economico dichiarato:** correlazione incrociata ritardata (Lo e MacKinlay, 1990): DYDX recupera
il movimento di BTC con ritardo. **Il test dello scettico della Fase 5 lo smentisce:** senza la condizione
«DYDX è rimasta indietro» la regola rende uguale o meglio (317 trade, R +0,050, `t` contro la (b) 2,77). In
costruzione il segnale era «dopo un'ora molto forte di BTC, DYDX sale nelle 3 ore seguenti», cioè momento
di breve trasmesso da BTC, non recupero del ritardo.

**Metriche, separate per periodo:**

| | Costruzione | Validazione |
|---|---|---|
| Trade | 161 | 83 |
| R medio dopo i costi | +0,060 | −0,178 |
| R medio senza i 3 migliori | +0,016 | −0,243 |
| Profit factor | 1,34 | 0,43 |
| Quota di trade in guadagno | — | 34% |
| Drawdown massimo | (vedi `risultati/DYDXUSDT-008.json`) | 17,6% |
| R medio per anno | 2021 +0,073 (41 trade), 2022 +0,002 (92), 2023 +0,233 (28) | 2023 −0,178 |
| Rendimento sul capitale | — | −15,4% |
| Baseline (a), R medio | −0,044; `t` 2,30 (netta) | −0,053; `t` −1,91 |
| Baseline (b), R medio | −0,038; `t` 2,22, soglia 2,07 (netta) | −0,053; `t` −1,96, soglia 2,14 |
| Percentile fra le simulazioni casuali | 99,0 | — |
| p-value dell'asticella | — | 0,968 |

**Verifiche della Fase 4 (tutte superate in costruzione):** robustezza 12 casi su 12 con `t` positivo e 9
netti (ma i casi che toccano la condizione, soglia su BTC 1,6 e 2,4, danno `t` 1,83 e 2,06, non netti);
timeframe adiacenti 30m (`t` 1,12) e 2h (`t` 1,69); stabilità sopra la (b) in 3 anni su 3 (il 2022, con 92
trade, a zero); senza i 3 migliori +0,016; ritardo di una barra `t` 1,56 (nessun crollo); regola intra-barra
opposta identica (nessun target); costi doppi R +0,024 e `t` 2,23 (netta); 0 violazioni della liquidazione,
0 trade ridotti per il tetto di leva.

**Rischi noti:** un solo candidato su 30 varianti, con `t` poco sopra la soglia (con la prova a placebo,
circa 12% di probabilità di almeno una «netta» su 30 varianti senza vantaggio); motivo economico smentito
dal test dello scettico; guadagno concentrato nel 2021 e nei primi mesi del 2023.

**Asticella:** m = 1 candidato validato; p = 0,968 > 0,10: **non passa** (provvisorio, Passo 4).

**Eseguibilità dal bot:** timeframe 1h scaricato dal bot; serve la condizione su BTC (strategia in codice
più l'aggiunta «coppia del protocollo»); stop oltre il 6% nel 17% dei trade di costruzione. Irrilevante:
non va al vault.

## Varianti e budget

* 30 varianti testate: 21 di idee nuove (13 idee, 21 famiglie), 9 ritocchi (5 nella famiglia 013 di cui uno
  scarto, 5 nella famiglia 014). Avanzo 0.
* 9 scarti per meno di 70 trade (S001-S008 di idee nuove, S009 di un ritocco): non hanno consumato budget.
* Controllo positivo degli strumenti (lookahead dichiarato): superato (`t` 46,9 senza ritardo, 2,48 con
  ritardo).
* Varianti diventate candidati in Fase 2: 1 da idee nuove (008), 0 da ritocchi.
* Varianti nette contro la (a) e la (b) con R medio non positivo: 0.

Riepilogo delle idee: `lezioni_moneta.md`.

## Criterio del vault (non applicato: nessun candidato)

Sarebbe stato: profit factor ≥ 1,10, almeno 30 trade, rendimento totale positivo, R medio sopra il 90°
percentile delle entrate casuali con la stessa uscita.

## Paper, vault e trasferimento

Nessun candidato: niente paper, niente vault, niente trasferimento per questa moneta. Previsione per
le stesse idee nel vault: nessuna delle 30 varianti mostrava un vantaggio che reggesse la validazione; mi
aspetto lo stesso.

## Misure di processo

Dal log (`codice/misure.py`), orologio della macchina.

* Prima voce 2026-10-09 17:26:08 UTC, ultima 18:40:10 UTC: **74 minuti**, nessuna pausa registrata. Il
  lavoro prima della prima voce (lettura del protocollo e degli strumenti, circa 3 minuti dall'apertura del
  branch alle 17:23) e la scrittura di `ipotesi.md` (fra le 17:30 e le 17:38, prima di ogni test) non
  stanno fra due voci di idea, quindi i minuti per idea qui sotto misurano solo i test.
* Minuti dalla registrazione della prima variante all'ultimo risultato, per idea: I-01 0,0; I-02 0,6;
  I-03 0,5; I-04 0,8; I-05 0,4; I-06 0,0; I-07 0,0; I-08 4,1; I-09 0,4; I-10 8,0 (con 4 ritocchi);
  I-11 9,6 (con 5 ritocchi); I-12 1,7.
* Spiegazioni concorrenti scritte in `ipotesi.md`: 11 per ognuna delle 12 idee (I-01..I-12); le varianti
  aggiunte di I-02, I-05, I-06 usano quelle della loro idea.
* Varianti diventate candidati in Fase 2: idee nuove 1, ritocchi 0.
* Varianti nette contro (a) e (b) con R medio dopo i costi non positivo: 0.
* Rifiuti del guardiano: 6, tutti per la forma dei comandi (note N002, N003 e questa consegna: anche un
  messaggio di commit passato con `-m` invece che con `-F`), nessuno per un percorso vietato voluto.
