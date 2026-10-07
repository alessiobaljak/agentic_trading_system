# 0525-7ott-mattina-ai-stato.req

_eseguito: 2026-10-07 06:05 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 6.8s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 02 Oct 18:18 UTC (4 giorni fa)
✅ di origine AI fra quelle che hanno passato il gate: 77 su 1172

✅ ombra: 240 decisioni registrate · ultima 30 Sep 15:47 UTC (7 giorni fa)
   il bot aveva un trade aperto nello stesso ciclo in 188 decisioni, in 52 no
   d'accordo col bot 26/188 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×161: avrebbe evitato il trade aperto
     both_flat ×42: entrambi fermi
     agree ×26: stessa scelta del bot
     shadow_only ×10: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 332 trade chiusi): profit factor 0.726 contro 2.024 promesso dal gate.
   - Escursione favorevole mediana 0.82R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 171 trade, 92 vinti, PnL -50.30.
   - Direzione short: 174 trade, 101 vinti, PnL -37.73.
   - GATE (giro precedente a 15m, finito il 07/10 04:51 UTC): su 45069 valutazioni coin x strategia ne passano 496; muoiono soprattutto su pf_ex_top 361 · total_return 34168 · trades 1189 · regime 3685.
✅ quasi-passaggi letti dall'AI: 27 · 02 Oct 18:17 UTC (4 giorni fa)
   schema: La stragrande maggioranza dei quasi-passaggi si ferma su pf_ex_top (PF ricalcolato togliendo i trade migliori) con scarti piccoli, su timeframe 15m. Dominano famiglie di feature mean-reversion/estremi (rsi_extreme, stoch
   consigli: Puntare su edge piu' distribuito: filtrare o aumentare la frequenza dei trade cosi' che il PF non dipenda dai pochi vincitori (il collo di bottiglia e' pf_ex_top, non il PF nominale). Evitare di riproporre lo stesso temp
[paper] 345 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
➖ ieri (6 ott): nessuna chiamata registrata (contatore appena nato, AI ferma o Firebase non raggiungibile)
➖ oggi fino alle 08:05 ora italiana: nessuna chiamata registrata
   ultimi 7 giorni completi: media 2,25 $ al giorno su 3 giorni con dati → circa 67 $ al mese (media × 30) (escluso 4 ott: misurato solo in parte)
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
