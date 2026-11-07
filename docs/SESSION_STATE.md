# Stato della sessione (compito in corso, decisioni, prossimi passi)

Aggiornato a ogni tappa dalla sessione principale (regole dei token in `CLAUDE.md`). Corto: il resto sta nel diario
(`docs/andremo_live.md`) e nei piani.

## Compito in corso (7 novembre 2026, pomeriggio)
- Subagent (`.claude/agents/`): i quattro creati e adattati al sistema di oggi; collaudo fatto (`docs/collaudo_agenti.md`: auditor
  FAIL con i tre errori voluti, segreti bloccati, revisore REQUEST CHANGES). Primo avvio del revisore degli ordini fatto
  (`reviews/reports/2026-11-07-primo-avvio.md`): niente di bloccante per il demo, 9 problemi Alti da chiudere prima del conto vero
  (backlog P26).
- Gli agenti si possono chiamare per nome solo dalle sessioni avviate dopo il 7 novembre (Claude Code li carica all'avvio); in questa
  sessione si usano con un agente generico che segue il loro file.
- Demo: alla mezzanotte dell'8 novembre chiude la fase da 280 USDT e riparte da zero a 1.000 (controllo al giro delle 00:17).
- Correzioni dei 9 problemi Alti del percorso degli ordini e dei problemi nuovi 25-33: approvate dal revisore (commit 013f9426,
  `reviews/reports/2026-11-07-correzione-32.md`); allarmi del demo visibili in dashboard e nel rapporto. **Riavvio del bot: aspetta
  l'ok del proprietario.** Bassi rimasti (36-38) e Medi del primo avvio nel backlog, prima del codice del conto vero.

## Decisioni del proprietario di questi giorni
- 5 nov: si migliora G1, un'idea nuova solo con un perché forte. 6 nov: 250 euro, eventi spenti sul demo. 7 nov: demo a 1.000 dalla
  mezzanotte; i subagent servono a strutturare il sistema («procedi con i tuoi suggerimenti e la gestione migliore dei token»); il
  passaggio di gate lo approva lui.

## Decisioni aperte per il proprietario
- Commissioni e scarto di prezzo da usare nelle prove (auditor); minimo di anni e operazioni per giudicare una prova.
- Leva di G1, limiti di G1 dentro `hard_limits.py`, divieto della parità col backtest fuori dal paper (revisore; backlog P26).
- Regole di Firebase davvero pubblicate; chiavi di Binance senza prelievo e limitate all'indirizzo della macchina.
- Compromessi dei token (modelli più leggeri per ricercatore e confronto, frequenza dei giri): proposti, non applicati.

## Prossimi passi
- Lunedì 9 novembre: riepilogo settimanale e primo avvio di gate2-reconciler su G1 (paper e demo).
- Prima dei soldi veri: audit di G1 con backtest-auditor sulla configurazione finale.
