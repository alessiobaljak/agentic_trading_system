# 0230-check-25set-ai-stato.req

_eseguito: 2026-09-25 05:13 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 4.6s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 25 Sep 03:31 UTC (2h fa)
✅ di origine AI fra quelle che hanno passato il gate: 10 su 533

✅ ombra: 60 decisioni registrate · ultima 25 Sep 02:47 UTC (2h fa)
   d'accordo col bot 0/60 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 54 trade chiusi): profit factor 0.637 contro 1.887 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 24 trade, 9 vinti, PnL -17.93.
   - Direzione short: 30 trade, 14 vinti, PnL -28.72.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su trades 6 · holdout 1 · regime 22 · total_return 1207.
✅ quasi-passaggi letti dall'AI: 3 · 25 Sep 03:31 UTC (2h fa)
   schema: Le tre quasi-passate sono tutte su timeframe 15m, concentrate su ADAUSDT (2 su 3) ed ETHUSDT, con conteggio trade adeguato (98-178, sopra soglia). Due si fermano su holdout con scarto 0.000 (esattamente al limite, non su
   consigli: Puntare su strategie con PF piu' modesto ma stabilita' cross-periodo, verificando esplicitamente la coerenza in-sample vs holdout invece di massimizzare il PF. Sui setup di fade/mean-reversion (macd_cross+htf_fade) aggiu
[paper] 54 trade chiusi -> scala candidata dal vissuto: [1.0, 1.5, 2.25] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.5, 2.25] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
