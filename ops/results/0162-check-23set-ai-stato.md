# 0162-check-23set-ai-stato.req

_eseguito: 2026-09-23 06:02 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 4.4s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-5
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 22 Sep 18:14 UTC (12h fa)
✅ di origine AI fra quelle che hanno passato il gate: 8 su 480

✅ ombra: 35 decisioni registrate · ultima 23 Sep 05:01 UTC (1h fa)
   d'accordo col bot 0/35 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 37 trade chiusi): profit factor 0.691 contro 1.942 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 14 trade, 6 vinti, PnL +4.75.
   - Direzione short: 23 trade, 8 vinti, PnL -35.84.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su recovery 64 · consistency 17 · total_return 1207 · pf_ex_top 3.
✅ quasi-passaggi letti dall'AI: 40 · 22 Sep 18:14 UTC (12h fa)
   schema: La stragrande maggioranza (32/40) si ferma su pf_ex_top con scarti minimi (da -0.000 a -0.009): sono mean-reversion basate su rsi_extreme e/o bb_touch spesso combinate con vwap_momentum/vwap_reversion, quasi tutte con ad
   consigli: Puntare a robustezza della distribuzione dei profitti piu' che al PF grezzo: preferire setup il cui edge non dipenda dai top winner (per superare pf_ex_top) aggiungendo un filtro trend reale (adx>0) e stop/target piu' si
[paper] 37 trade chiusi -> scala candidata dal vissuto: [1.0, 1.75, 3.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.75, 3.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
