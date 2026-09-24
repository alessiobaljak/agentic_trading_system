# 0186-ai-stato-24set.req

_eseguito: 2026-09-24 06:36 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 5.0s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 22 Sep 18:14 UTC (36h fa)
✅ di origine AI fra quelle che hanno passato il gate: 8 su 522

✅ ombra: 44 decisioni registrate · ultima 24 Sep 00:16 UTC (6h fa)
   d'accordo col bot 0/44 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 44 trade chiusi): profit factor 0.601 contro 1.885 promesso dal gate.
   - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 18 trade, 6 vinti, PnL -16.28.
   - Direzione short: 26 trade, 10 vinti, PnL -32.87.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su consistency 17 · holdout 1 · total_return 1207 · regime 22.
✅ quasi-passaggi letti dall'AI: 4 · 23 Sep 21:12 UTC (9h fa)
   schema: I quattro quasi-passaggi sono tutti su timeframe 15m e si fermano esattamente sullo stesso criterio — l'holdout — con scarto 0.000, cioè falliscono il test out-of-sample finale pur avendo PF in-sample buoni (1.59–2.48). 
   consigli: Prima di generare altro, verificare come viene calcolato lo scarto sull'holdout e se l'holdout contiene abbastanza barre/trade: uno scarto 0.000 ripetuto è sospetto di gate binario o finestra vuota. Poi puntare su logich
[paper] 44 trade chiusi -> scala candidata dal vissuto: [0.75, 1.5, 2.25] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.5, 2.25] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
