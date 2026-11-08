# Stato della sessione (compito in corso, decisioni, prossimi passi)

Aggiornato a ogni tappa dalla sessione principale (regole dei token in `CLAUDE.md`). Corto: il resto sta nel diario
(`docs/andremo_live.md`) e nei piani.

## Compito in corso (8 novembre 2026, mattina)
- Subagent (`.claude/agents/`): i quattro creati e adattati al sistema di oggi; collaudo fatto (`docs/collaudo_agenti.md`: auditor
  FAIL con i tre errori voluti, segreti bloccati, revisore REQUEST CHANGES). Primo avvio del revisore degli ordini fatto
  (`reviews/reports/2026-11-07-primo-avvio.md`): niente di bloccante per il demo, 9 problemi Alti da chiudere prima del conto vero
  (backlog P26).
- Gli agenti si possono chiamare per nome solo dalle sessioni avviate dopo il 7 novembre (Claude Code li carica all'avvio); in questa
  sessione si usano con un agente generico che segue il loro file.
- Demo: partito da zero a 1.000 l'8 novembre alle 00:18 UTC (52 posizioni chiuse, 0 errori; 48 ordini di G1; sotto il minimo 2
  variazioni invece di 50). La misura vera dei minimi a 1.000 è il ribilancio del 9 novembre.
- Correzioni dei 9 problemi Alti del percorso degli ordini e dei problemi nuovi 25-33: approvate dal revisore (commit 013f9426,
  `reviews/reports/2026-11-07-correzione-32.md`); allarmi del demo visibili in dashboard e nel rapporto. **Riavviato il 7 novembre alle
  18:54 UTC** con l'ok del proprietario (commit 78bb70e3). Bassi rimasti (36-38) e Medi del primo avvio nel backlog, prima del codice del conto vero.

- 8 nov: contenitore nuovo (disco sano, cartella dei dati vuota). La prova in avanti del programma 5 scaricava solo da ottobre 2026:
  ora scarica dal giugno 2025 (inizio del periodo su cui sceglie le candidate); i numeri del mattino non sono stati committati
  (M-002 600 trade invece di 1.916). Da rifare con lo scarico intero, poi il paper delle candidate del programma 6.
- 8 nov: due agenti nuovi (strategy-improver, portfolio-allocator), la regola «nessuna strategia del paper o del demo si perde» con il
  suo test, le idee 136 (la 1:1:1) e 137 (il riesame delle bocciate di poco) in coda.

## Decisioni del proprietario di questi giorni
- 5 nov: si migliora G1, un'idea nuova solo con un perché forte. 6 nov: 250 euro, eventi spenti sul demo. 7 nov: demo a 1.000 dalla
  mezzanotte; i subagent servono a strutturare il sistema («procedi con i tuoi suggerimenti e la gestione migliore dei token»); il
  passaggio di gate lo approva lui.

## Decisioni aperte per il proprietario
- Commissioni e scarto di prezzo da usare nelle prove (auditor); minimo di anni e operazioni per giudicare una prova.
- Leva di G1, limiti di G1 dentro `hard_limits.py`, divieto della parità col backtest fuori dal paper (revisore; backlog P26).
- Regole di Firebase davvero pubblicate; chiavi di Binance senza prelievo e limitate all'indirizzo della macchina.
- Token: ricercatore e confronto settimanale sul modello medio dall'8 novembre (i due revisori restano sul più potente). Giri meno
  frequenti: proposti, aspettano il proprietario (la decisione del 5 novembre dice «ogni giro delle 4 ore migliora G1»).

## Prossimi passi
- Lunedì 9 novembre: riepilogo settimanale, primo avvio di gate2-reconciler su G1 (paper e demo) e di portfolio-allocator (proposta
  delle regole di scelta, da far approvare).
- Prima dei soldi veri: audit di G1 con backtest-auditor sulla configurazione finale.
