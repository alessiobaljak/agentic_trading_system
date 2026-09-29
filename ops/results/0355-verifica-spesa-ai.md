# 0355-verifica-spesa-ai.req

_eseguito: 2026-09-29 09:28 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 5.8s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 29 Sep 09:09 UTC (0h fa)
✅ di origine AI fra quelle che hanno passato il gate: 39 su 642

✅ ombra: 215 decisioni registrate · ultima 29 Sep 08:19 UTC (1h fa)
   il bot aveva un trade aperto nello stesso ciclo in 168 decisioni, in 47 no
   d'accordo col bot 23/168 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×144: avrebbe evitato il trade aperto
     both_flat ×39: entrambi fermi
     agree ×23: stessa scelta del bot
     shadow_only ×8: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 169 trade chiusi): profit factor 0.699 contro 2.029 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 71 trade, 37 vinti, PnL -28.33.
   - Direzione short: 104 trade, 60 vinti, PnL -38.50.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su pf_ex_top 3 · consistency 17 · trades 6 · regime 22.
✅ quasi-passaggi letti dall'AI: 30 · 29 Sep 09:09 UTC (0h fa)
   schema: La stragrande maggioranza (25 su 30) si ferma su 'holdout' con scarto 0.000, cioe' falliscono l'ultima finestra out-of-sample nonostante PF in-sample buoni (1.4-2.6). C'e' forte concentrazione su poche coin (BANKUSDT ~10
   consigli: Concentrarsi su coin con storia lunga e liquidita' alta e chiedere piu' trade nell'holdout stesso (non solo in-sample), scartando i PF gonfiati da campioni piccoli. Evitare di ottimizzare su BANKUSDT e simili e privilegi
[paper] 175 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
➖ ieri (28 set): nessuna chiamata registrata (contatore appena nato, AI ferma o Firebase non raggiungibile)
💶 oggi fino alle 11:28 ora italiana: 0,35 $ in 8 chiamate
   media: nessun giorno completo misurato ancora; fino ad allora vale la stima D6 del backlog (~2,75 $ al giorno, stimata dai log il 29 set)
⚠️ risposte tagliate a meta' (il modello ha finito lo spazio di risposta concesso, max_tokens):
   filtro delle monete su cui cercare (ai-universe): oggi 1 su 2 → pagate e buttate: aspettavano dati strutturati
➖ 1 chiamata fra ieri e oggi per «prova di collegamento della chiave» (ai-connettivita, circa 0,0002 $) ha usato il modello «claude-opus-5» invece di quello della VPS «claude-opus-4-8» (probabile runner GitHub: segreto ANTHROPIC_MODEL): cifra trascurabile, contata col prezzo della VPS
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
