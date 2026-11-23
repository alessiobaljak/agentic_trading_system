# 0770-23nov-chiave-del-modello.req

_eseguito: 2026-11-23 07:55 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 9.4s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 02 Oct 18:18 UTC (52 giorni fa)
✅ di origine AI fra quelle che hanno passato il gate: 79 su 1675

✅ ombra: 240 decisioni registrate · ultima 30 Sep 15:47 UTC (54 giorni fa)
   il bot aveva un trade aperto nello stesso ciclo in 188 decisioni, in 52 no
   d'accordo col bot 26/188 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×161: avrebbe evitato il trade aperto
     both_flat ×42: entrambi fermi
     agree ×26: stessa scelta del bot
     shadow_only ×10: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - Direzione long: 456 trade, 248 vinti, PnL -100.57.
   - Direzione short: 328 trade, 185 vinti, PnL -82.18.
✅ quasi-passaggi letti dall'AI: 27 · 02 Oct 18:17 UTC (52 giorni fa)
   schema: La stragrande maggioranza dei quasi-passaggi si ferma su pf_ex_top (PF ricalcolato togliendo i trade migliori) con scarti piccoli, su timeframe 15m. Dominano famiglie di feature mean-reversion/estremi (rsi_extreme, stoch
   consigli: Puntare su edge piu' distribuito: filtrare o aumentare la frequenza dei trade cosi' che il PF non dipenda dai pochi vincitori (il collo di bottiglia e' pf_ex_top, non il PF nominale). Evitare di riproporre lo stesso temp
[paper] 784 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
💶 ieri (22 nov, giornata NON intera: prima chiamata contata alle 09): 0,011 $ in 1 chiamata
   riassunto settimanale della domenica (ai-learning): 1 chiamata · 252 token letti + 400 scritti · 0,011 $ · 100% della spesa di ieri
➖ oggi fino alle 08:55 ora italiana: nessuna chiamata registrata
   media: nessun giorno completo misurato ancora (escluso 22 nov: misurato solo in parte); fino ad allora vale la stima D6 del backlog (~2,75 $ al giorno, stimata dai log il 29 set)
⚠️ risposte tagliate a meta' (il modello ha finito lo spazio di risposta concesso, max_tokens):
   riassunto settimanale della domenica (ai-learning): ieri 1 su 1 → testo salvato ma monco
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
