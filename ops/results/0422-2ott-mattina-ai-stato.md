# 0422-2ott-mattina-ai-stato.req

_eseguito: 2026-10-02 06:04 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 6.2s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 02 Oct 03:48 UTC (2h fa)
✅ di origine AI fra quelle che hanno passato il gate: 70 su 813

✅ ombra: 240 decisioni registrate · ultima 30 Sep 15:47 UTC (38h fa)
   il bot aveva un trade aperto nello stesso ciclo in 188 decisioni, in 52 no
   d'accordo col bot 26/188 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×161: avrebbe evitato il trade aperto
     both_flat ×42: entrambi fermi
     agree ×26: stessa scelta del bot
     shadow_only ×10: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 216 trade chiusi): profit factor 0.694 contro 2.032 promesso dal gate.
   - Escursione favorevole mediana 0.84R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 98 trade, 51 vinti, PnL -40.83.
   - Direzione short: 126 trade, 73 vinti, PnL -36.39.
   - GATE (giro precedente a 15m, finito il 02/10 05:50 UTC): su 27104 valutazioni coin x strategia ne passano 37; muoiono soprattutto su recovery 1318 · holdout 65 · trades 1957 · total_return 22124.
✅ quasi-passaggi letti dall'AI: 40 · 02 Oct 03:47 UTC (2h fa)
   schema: La stragrande maggioranza si ferma su pf_ex_top (o la sua versione holdout): il PF regge solo grazie ai pochi trade migliori, e tolti quelli scende a ~1.0 o sotto. Dominano mean-reversion su 15m (rsi_extreme, bb_touch, s
   consigli: Punta a edge distribuito e non dipendente dagli outlier: preferisci setup con PF che regge anche togliendo i top trade (margine su molti trade piuttosto che pochi colpi grossi). Evita conteggi holdout sotto ~20-30 trade 
[paper] 224 trade chiusi -> scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [0.75, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
💶 ieri (1 ott, giornata intera ora italiana): 2,07 $ in 31 chiamate
   idee di strategie nuove da far provare al gate (ai-hypotheses): 16 chiamate · 32 mila token letti + 55 mila scritti · 1,53 $ · 74% della spesa di ieri
   lettura delle strategie quasi promosse per dare consigli alla ricerca (ai-autopsia): 15 chiamate · 53 mila token letti + 11 mila scritti · 0,55 $ · 26% della spesa di ieri
💶 oggi fino alle 08:04 ora italiana: 0,53 $ in 8 chiamate
   ultimi 7 giorni completi: media 2,44 $ al giorno su 2 giorni con dati → circa 73 $ al mese (media × 30) (escluso 29 set: misurato solo in parte)
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
