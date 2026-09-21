# 0124-ai-stato-21set.req

_eseguito: 2026-09-21 06:02 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 11.2s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 21 Sep 03:45 UTC (2h fa)
✅ di origine AI fra quelle che hanno passato il gate: 2 su 428

✅ ombra: 15 decisioni registrate · ultima 21 Sep 02:46 UTC (3h fa)
   d'accordo col bot 0/15 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 21 trade chiusi): profit factor 0.535 contro 1.894 promesso dal gate.
   - Escursione favorevole mediana 0.74R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 10 trade, 3 vinti, PnL -10.03.
   - Direzione short: 11 trade, 2 vinti, PnL -13.20.
   - GATE: su 1312 valutazioni ne passano 1; muoiono soprattutto su total_return 1155 · pf_ex_top 12 · recovery 77 · trades 8.
[paper] 21 trade chiusi -> scala candidata dal vissuto: [0.75, 1.5, 3.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.5, 3.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
