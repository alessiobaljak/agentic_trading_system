# 0113-ai-stato-motivi.req

_eseguito: 2026-09-20 08:21 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 4.1s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

❌ proposte: 0 spec con un meccanismo dichiarato su 408 totali
   nessuna spec motivata: o l'AI non ha ancora girato col codice nuovo,
   oppure sta proponendo e le proposte non vengono salvate
   ultimo giro: 1/20 proposte accettate · 20 Sep 06:41 UTC (2h fa)
     scartate ×4: rr=1.3 fuori dalla fascia 1.5-3
     scartate ×1: rsi_momentum: manca il parametro mid
     scartate ×4: rr=1.2 fuori dalla fascia 1.5-3
     scartate ×3: rr=1 fuori dalla fascia 1.5-3
     scartate ×1: nessuna feature direzionale
     scartate ×3: rr=0.9 fuori dalla fascia 1.5-3

✅ ombra: 6 decisioni registrate · ultima 20 Sep 03:01 UTC (5h fa)
   d'accordo col bot 0/6 volte (serve piu' campione per dire se conviene ascoltarla)

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 16 trade chiusi): profit factor 0.416 contro 1.865 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 8 trade, 3 vinti, PnL -4.30.
   - Direzione short: 8 trade, 1 vinti, PnL -18.52.
   - GATE: su 1312 valutazioni ne passano 0; muoiono soprattutto su consistency 20 · trades 6 · win_rate 1 · regime 40.
[paper] 16 trade chiusi -> scala candidata dal vissuto: [0.75, 1.5, 3.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.5, 3.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
