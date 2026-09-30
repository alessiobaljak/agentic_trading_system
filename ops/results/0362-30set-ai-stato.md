# 0362-30set-ai-stato.req

_eseguito: 2026-09-30 06:12 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 5.5s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 30 Sep 06:09 UTC (0h fa)
✅ di origine AI fra quelle che hanno passato il gate: 48 su 667

✅ ombra: 229 decisioni registrate · ultima 30 Sep 06:02 UTC (0h fa)
   il bot aveva un trade aperto nello stesso ciclo in 179 decisioni, in 50 no
   d'accordo col bot 25/179 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×153: avrebbe evitato il trade aperto
     both_flat ×40: entrambi fermi
     agree ×25: stessa scelta del bot
     shadow_only ×10: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 182 trade chiusi): profit factor 0.698 contro 2.024 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 80 trade, 42 vinti, PnL -31.22.
   - Direzione short: 109 trade, 64 vinti, PnL -37.43.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su holdout 1 · consistency 17 · pf_ex_top 3 · trades 6.
✅ quasi-passaggi letti dall'AI: 40 · 30 Sep 06:09 UTC (0h fa)
   schema: Dominano strategie mean-reversion su oscillatori estremi (stoch_momentum + rsi_extreme, spesso con bb_touch) su timeframe 15m, quasi tutte con adx>=0.0 (nessun filtro di trend) e atr elevato (2.0-2.5). Il criterio che fe
   consigli: Per superare pf_ex_top puntate su edge piu' distribuito, non dipendente da pochi outlier: riducete l'atr (usate 1.0-1.5, gia' presente in alcuni setup vwap/htf_fade che si fermano su altro) e valutate filtri direzionali/
[paper] 189 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
💶 ieri (29 set, giornata NON intera: prima chiamata contata alle 10): 1,88 $ in 43 chiamate
   idee di strategie nuove da far provare al gate (ai-hypotheses): 10 chiamate · 20 mila token letti + 34 mila scritti · 0,95 $ · 50% della spesa di ieri
   filtro delle monete su cui cercare (ai-universe): 10 chiamate · 14 mila token letti + 13 mila scritti · 0,38 $ · 20% della spesa di ieri
   lettura delle strategie quasi promosse per dare consigli alla ricerca (ai-autopsia): 10 chiamate · 31 mila token letti + 7,6 mila scritti · 0,34 $ · 18% della spesa di ieri
   ombra: cosa farebbe l'AI al posto del bot, solo misura (ai-shadow): 12 chiamate · 10 mila token letti + 6,2 mila scritti · 0,21 $ · 11% della spesa di ieri
   prova di collegamento della chiave (ai-connettivita): 1 chiamata · 8 token letti + 5 scritti · 0,0002 $ · 0% della spesa di ieri
💶 oggi fino alle 08:12 ora italiana: 0,87 $ in 18 chiamate
   media: nessun giorno completo misurato ancora (escluso 29 set: misurato solo in parte); fino ad allora vale la stima D6 del backlog (~2,75 $ al giorno, stimata dai log il 29 set)
⚠️ risposte tagliate a meta' (il modello ha finito lo spazio di risposta concesso, max_tokens):
   filtro delle monete su cui cercare (ai-universe): ieri 4 su 10 → pagate e buttate: aspettavano dati strutturati
➖ 1 chiamata fra ieri e oggi per «prova di collegamento della chiave» (ai-connettivita, circa 0,0002 $) ha usato il modello «claude-opus-5» invece di quello della VPS «claude-opus-4-8» (probabile runner GitHub: segreto ANTHROPIC_MODEL): cifra trascurabile, contata col prezzo della VPS
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
