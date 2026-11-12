# Stato della sessione (compito in corso, decisioni, prossimi passi)

Aggiornato a ogni tappa dalla sessione principale (regole dei token in `CLAUDE.md`). Corto: il resto sta nel diario
(`docs/andremo_live.md`) e nei piani.

## Compito in corso (12 novembre 2026, mattina)
- **Bot**: gira il codice della fase 1 del conto vero (commit 83ddb809, riavvio dell'8 novembre 19:02 UTC); `DRY_RUN` vero. Demo di G1
  a 1.000 USDT dall'8 novembre (misura dei minimi a ogni ribilancio nel piano `research/programma7/MIGLIORARE_G1.md`, voce 8). Fase 2
  (codice del conto vero, spento) committata (ff89531), non ancora caricata dal bot.
- **Conto vero**: lista del proprietario e decisioni in `docs/conto_vero.md` (riletta il 12 novembre). Punti aperti prima
  dell'accensione: canale di approvazione della versione (firma o dashboard: la regola di GitHub non basta), Firebase, Binance, le
  decisioni a-k, i problemi 66, 70, 72, 73, pulsante e stato in dashboard, revisione finale.
- **Ricerca**: due binari a ogni giro (migliorare G1, ricerca nuova). Agenti: strategy-scout, strategy-researcher (prima in modalità
  verifica), backtest-auditor, strategy-improver (voci 9-13 del piano di G1), gate2-reconciler e portfolio-allocator il lunedì.
  Prove 149, 150 e 151 chiuse senza candidate (conto 309); riesame: fatte la 28 (miscela F5 + M7 + K2: PASS tecnico, misurata a
  tavolino) e la 113 (resta bocciata); restano la 55 e la 96. In corso: revisione di G1 con backtest-auditor.
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
- Idee mai provate da passare a strategy-scout: differenze di funding fra borse, base dei future trimestrali, dominanza del Bitcoin.
- Lunedì 16 novembre: riepilogo settimanale con la miscela a tavolino, gate2-reconciler, portfolio-allocator.
- Il contesto di questa conversazione è molto lungo: conviene compattarla.
