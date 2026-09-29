# 0342-29set-ai-stato.req

_eseguito: 2026-09-29 06:12 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 5.4s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 29 Sep 06:07 UTC (0h fa)
✅ di origine AI fra quelle che hanno passato il gate: 38 su 637

✅ ombra: 212 decisioni registrate · ultima 29 Sep 05:17 UTC (1h fa)
   il bot aveva un trade aperto nello stesso ciclo in 166 decisioni, in 46 no
   d'accordo col bot 22/166 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×143: avrebbe evitato il trade aperto
     both_flat ×38: entrambi fermi
     agree ×22: stessa scelta del bot
     shadow_only ×8: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 168 trade chiusi): profit factor 0.697 contro 2.035 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 70 trade, 36 vinti, PnL -28.83.
   - Direzione short: 104 trade, 60 vinti, PnL -38.50.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su regime 22 · consistency 17 · holdout 1 · total_return 1207.
✅ quasi-passaggi letti dall'AI: 32 · 29 Sep 06:06 UTC (0h fa)
   schema: Due cluster netti: (1) strategie fermate su pf_ex_top con scarto piccolo, PF pieno ~1.28-1.44 e molti trade (160-425), concentrate su BANKUSDT/DEXEUSDT/STXUSDT; (2) un gruppo molto numeroso fermato su holdout con scarto 
   consigli: Per il cluster pf_ex_top: alzare la selettivita' delle entrate (filtri piu' stretti, meno trade marginali) per non dipendere dagli outlier; puntare a PF robusto anche escludendo i top. Per il cluster holdout=0.000: verif
[paper] 174 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
