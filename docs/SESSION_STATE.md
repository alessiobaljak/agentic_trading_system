# Stato della sessione (compito in corso, decisioni, prossimi passi)

Aggiornato a ogni tappa dalla sessione principale (regole dei token in `CLAUDE.md`). Corto: il resto sta nel diario
(`docs/andremo_live.md`) e nei piani.

## Compito in corso (13 novembre 2026, 09:00 UTC)
- **Bot**: gira il codice della fase 1 del conto vero (commit 83ddb809, riavvio dell'8 novembre 19:02 UTC); `DRY_RUN` vero. Demo di G1
  a 1.000 USDT dall'8 novembre (misura dei minimi a ogni ribilancio nel piano `research/programma7/MIGLIORARE_G1.md`, voce 8). Fase 2
  (codice del conto vero, spento) committata (ff89531), non ancora caricata dal bot.
- **Conto vero**: lista del proprietario e decisioni in `docs/conto_vero.md` (riletta il 12 novembre). Punti aperti prima
  dell'accensione: canale di approvazione della versione (firma o dashboard: la regola di GitHub non basta), Firebase, Binance, le
  decisioni a-k, i problemi 66, 70, 72, 73, pulsante e stato in dashboard, revisione finale.
- **Ricerca**: due binari a ogni giro (migliorare G1, ricerca nuova). Agenti: strategy-scout, strategy-researcher (prima in modalità
  verifica), backtest-auditor, strategy-improver (voci 9-13 del piano di G1), gate2-reconciler e portfolio-allocator il lunedì.
  Prove 149-151 chiuse senza candidate; prova 152 (concentrazione di G1) chiusa: il tetto del 20% non passa l'esame scritto solo per
  8 ordini saltati in più su circa 123.000, decisione al proprietario (conto 312). Revisione di G1: PASS tecnico con 4 Alti
  (`audits/reports/2026-11-12-G1_CONTO_VERO.md`). Riesame: fatte la 28 e la 113; in corso la 96 (backtest-auditor); resta la 55.
  Prove 153 (libro degli ordini) e 154 (dimensione media dello scambio) chiuse senza candidate (conto 316); riesami finiti (28 PASS
  tecnico, 113, 96 e 55 restano bocciate). Pulsante di approvazione, estratto dal demo e funding dei paper committati, in attesa del
  riavvio (ok del proprietario). 13 novembre: lo scout non trova idee forti (idee 138-140 nella coda con il perché no); voce 9 di G1
  misurata (scarto del demo = minimi + monete mancanti; costo nel funding); trappola del funding di novembre nel pannello annotata in
  `research/INDEX.md` (per i confronti con paper e demo si usa `applica_stima`).
  Pomeriggio: voce 11 di G1 misurata (il demo è sopra il paper solo per il primo giorno; a regime il paper sopravvaluta di 0,045
  punti al giorno); prova 155 (G1 frenata dall'indice di paura delle opzioni) non passa, conto 318; le spese di G1 della prova 120
  erano un po' sovrastimate (ordini senza candele a 1 ora).
- **Dashboard**: «Plancia» (aree Crypto e Azioni, menu a sinistra richiudibile); la scheda Azioni la riempie la sessione «trading
  stock». Aree del repository separate (`AREE.md`, blocco `.claude/hooks/aree.py`).

## Decisioni del proprietario di questi giorni
- 8 nov: nessuna strategia del paper o del demo si perde; lo 0,90 non è un muro. 9 nov: Sharpe corretto minimo 0,80; sotto i 500 USDT
  una strategia sola. 11 nov: la ricerca nuova non si ferma; aree separate; Sharpe corretto per famiglie di prove simili; la miscela
  F5 + M7 + K2 si misura a tavolino.

## Decisioni aperte per il proprietario
- Conto vero: `docs/conto_vero.md`, punti 1-5 (Firebase per primo).
- Confronto settimanale: le soglie di `gate2/THRESHOLDS.md` non vanno approvate così (due sono già superate solo per le monete che il
  demo di Binance non ha): prima decidere come trattare le monete mancanti.
- Allocatore: la miscela sopra i 500 USDT e la regola della sostituzione (`allocazione/REGOLE.md`).

## Prossimi passi
- Da costruire nella ricerca: una funzione unica per l'esame (famiglie), un controllo dei dati a inizio giro (giorni a metà, candele
  mancanti, file vecchi), le voci rimaste del backlog P32.
- Idee passate a strategy-scout il 12 novembre: differenze di funding fra borse, base dei future trimestrali, dominanza del Bitcoin.
- Decisione aperta: la variante di G1 con il tetto del 20% per moneta (prova 152) al revisore e poi nel paper accanto a G1?
- Lunedì 16 novembre: riepilogo settimanale con la miscela a tavolino, gate2-reconciler (funding di novembre: usare la stima, non il
  pannello; dire del salto del funding dei paper dopo il riavvio), portfolio-allocator.
- Il contesto di questa conversazione è molto lungo: conviene compattarla.
