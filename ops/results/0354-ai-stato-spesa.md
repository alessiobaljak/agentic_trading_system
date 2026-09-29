# 0354-ai-stato-spesa.req

_eseguito: 2026-09-29 08:13 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 6.4s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 29 Sep 06:07 UTC (2h fa)
✅ di origine AI fra quelle che hanno passato il gate: 39 su 641

✅ ombra: 214 decisioni registrate · ultima 29 Sep 06:47 UTC (1h fa)
   il bot aveva un trade aperto nello stesso ciclo in 167 decisioni, in 47 no
   d'accordo col bot 23/167 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×143: avrebbe evitato il trade aperto
     both_flat ×39: entrambi fermi
     agree ×23: stessa scelta del bot
     shadow_only ×8: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 169 trade chiusi): profit factor 0.699 contro 2.031 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 71 trade, 37 vinti, PnL -28.33.
   - Direzione short: 104 trade, 60 vinti, PnL -38.50.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su recovery 64 · trades 6 · pf_ex_top 3 · holdout 1.
✅ quasi-passaggi letti dall'AI: 32 · 29 Sep 06:06 UTC (2h fa)
   schema: Due cluster netti: (1) strategie fermate su pf_ex_top con scarto piccolo, PF pieno ~1.28-1.44 e molti trade (160-425), concentrate su BANKUSDT/DEXEUSDT/STXUSDT; (2) un gruppo molto numeroso fermato su holdout con scarto 
   consigli: Per il cluster pf_ex_top: alzare la selettivita' delle entrate (filtri piu' stretti, meno trade marginali) per non dipendere dagli outlier; puntare a PF robusto anche escludendo i top. Per il cluster holdout=0.000: verif
[paper] 175 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
➖ ieri (28 set): nessuna chiamata registrata (contatore appena nato, AI ferma o Firebase non raggiungibile)
➖ oggi fino alle 10:13 ora italiana: nessuna chiamata registrata
   media: nessun giorno completo misurato ancora; fino ad allora vale la stima D6 del backlog (~2,75 $ al giorno, stimata dai log il 29 set)
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
