# 0260-controllo-26set-ai-stato.req

_eseguito: 2026-09-26 06:05 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 5.4s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 26 Sep 06:04 UTC (0h fa)
✅ di origine AI fra quelle che hanno passato il gate: 15 su 549

✅ ombra: 100 decisioni registrate · ultima 26 Sep 06:02 UTC (0h fa)
   il bot aveva un trade aperto nello stesso ciclo in 100 decisioni, in 0 no
   d'accordo col bot 7/100 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×92: avrebbe evitato il trade aperto
     agree ×7: stessa scelta del bot
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 84 trade chiusi): profit factor 0.615 contro 2.091 promesso dal gate.
   - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 30 trade, 13 vinti, PnL -18.78.
   - Direzione short: 54 trade, 26 vinti, PnL -44.95.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su consistency 17 · total_return 1207 · trades 6 · regime 22.
✅ quasi-passaggi letti dall'AI: 3 · 26 Sep 06:03 UTC (0h fa)
   schema: Tutti e tre sono su 15m con PF discreti (1.30-1.74) e volumi di trade sani (124-223), su ADAUSDT (2 su 3) ed ETHUSDT. Usano filtri di trend/momentum multi-timeframe (macd_cross+htf_fade, relative_strength+trend_strength 
   consigli: Puntate su logiche trend-following multi-TF gia' viste (adx>=20, relative_strength) ma aggiungete controllo esplicito del drawdown/dimensionamento per superare recovery, e testate su piu' segmenti temporali per non morir
[paper] 84 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.25, 2.0] (si aggiunge alle fisse, sceglie il gate)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
