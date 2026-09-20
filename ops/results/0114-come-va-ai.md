# 0114-come-va-ai.req

_eseguito: 2026-09-20 13:00 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 4.6s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

❌ proposte: 0 spec con un meccanismo dichiarato su 416 totali
   nessuna spec motivata: o l'AI non ha ancora girato col codice nuovo,
   oppure sta proponendo e le proposte non vengono salvate
   ultimo giro: 20/20 proposte accettate · 20 Sep 12:49 UTC (0h fa)

✅ ombra: 8 decisioni registrate · ultima 20 Sep 11:16 UTC (2h fa)
   d'accordo col bot 0/8 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 18 trade chiusi): profit factor 0.627 contro 1.866 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 9 trade, 3 vinti, PnL -7.83.
   - Direzione short: 9 trade, 2 vinti, PnL -8.05.
   - GATE: su 1312 valutazioni ne passano 0; muoiono soprattutto su pf_ex_top 14 · regime 36 · consistency 18 · total_return 1161.
[paper] 18 trade chiusi -> scala candidata dal vissuto: [0.75, 2.0, 3.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 2.0, 3.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
