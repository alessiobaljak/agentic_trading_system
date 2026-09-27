# 0293-controllo-27set-ai-stato.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 4.8s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 27 Sep 06:10 UTC (0h fa)
✅ di origine AI fra quelle che hanno passato il gate: 22 su 570

✅ ombra: 144 decisioni registrate · ultima 27 Sep 06:02 UTC (0h fa)
   il bot aveva un trade aperto nello stesso ciclo in 123 decisioni, in 21 no
   d'accordo col bot 10/123 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×112: avrebbe evitato il trade aperto
     both_flat ×18: entrambi fermi
     agree ×10: stessa scelta del bot
     shadow_only ×3: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 110 trade chiusi): profit factor 0.616 contro 2.098 promesso dal gate.
   - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 45 trade, 20 vinti, PnL -22.79.
   - Direzione short: 66 trade, 33 vinti, PnL -51.00.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su trades 6 · recovery 64 · pf_ex_top 3 · regime 22.
✅ quasi-passaggi letti dall'AI: 21 · 27 Sep 06:09 UTC (0h fa)
   schema: I quasi-passaggi si dividono in due cluster: 13 fermati su pf_ex_top (PF 1.26-1.45, spesso 250-520 trade) e 8 fermati su holdout con scarto 0.000 ma PF alto (1.38-2.04, tipicamente <220 trade). Ricorrono le coin ADA, STX
   consigli: Per il cluster pf_ex_top puntate su edge piu' distribuito: piu' trade e meno dipendenza da singoli movimenti (filtri che riducano la varianza del profitto per trade, non che la aumentino). Per il cluster holdout verifica
[paper] 111 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
