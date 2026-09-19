# 0101-ai-stato-prima-prova.req

_eseguito: 2026-09-19 18:15 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 10.9s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

❌ proposte: 0 spec con un meccanismo dichiarato su 394 totali
   nessuna spec motivata: o l'AI non ha ancora girato col codice nuovo,
   oppure sta proponendo e le proposte non vengono salvate

✅ ombra: 1 decisioni registrate · ultima 19 Sep 17:01 UTC (1h fa)
   d'accordo col bot 0/1 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 13 trade chiusi): profit factor 0.414 contro 1.853 promesso dal gate.
   - Escursione favorevole mediana 0.74R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 6 trade, 2 vinti, PnL -0.36.
   - Direzione short: 7 trade, 0 vinti, PnL -19.69.
   - GATE: su 1248 valutazioni ne passano 0; muoiono soprattutto su total_return 1105 · pf_ex_top 12 · recovery 73 · regime 36.
[paper] 13 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 3.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.25, 3.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
