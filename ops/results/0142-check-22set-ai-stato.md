# 0142-check-22set-ai-stato.req

_eseguito: 2026-09-22 06:02 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 7.8s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 22 Sep 02:53 UTC (3h fa)
✅ di origine AI fra quelle che hanno passato il gate: 3 su 437

✅ ombra: 31 decisioni registrate · ultima 22 Sep 06:01 UTC (0h fa)
   d'accordo col bot 0/31 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 35 trade chiusi): profit factor 0.687 contro 1.878 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 14 trade, 6 vinti, PnL +4.75.
   - Direzione short: 21 trade, 7 vinti, PnL -33.40.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su pf_ex_top 3 · holdout 1 · consistency 17 · trades 6.
✅ quasi-passaggi letti dall'AI: 40 · 22 Sep 02:52 UTC (3h fa)
   schema: La stragrande maggioranza si ferma su pf_ex_top (profit factor escluso il top trade) con scarti minimi (-0.000 a -0.009), mentre solo pochi cadono su recovery o total_return. Dominano feature mean-reversion/estremi (rsi_
   consigli: Proponete strategie il cui PF regga anche escludendo il top trade: puntate su distribuzione più uniforme dei profitti (più trade, meno dipendenza da outlier) e aggiungete un filtro ADX/regime reale invece di adx>=0.0. Pr
[paper] 35 trade chiusi -> scala candidata dal vissuto: [1.0, 1.5, 3.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.5, 3.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
