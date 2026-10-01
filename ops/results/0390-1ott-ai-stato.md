# 0390-1ott-ai-stato.req

_eseguito: 2026-10-01 06:13 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 6.9s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 01 Oct 05:01 UTC (1h fa)
✅ di origine AI fra quelle che hanno passato il gate: 59 su 730

✅ ombra: 240 decisioni registrate · ultima 30 Sep 15:47 UTC (14h fa)
   il bot aveva un trade aperto nello stesso ciclo in 188 decisioni, in 52 no
   d'accordo col bot 26/188 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×161: avrebbe evitato il trade aperto
     both_flat ×42: entrambi fermi
     agree ×26: stessa scelta del bot
     shadow_only ×10: avrebbe operato, il bot no
     different_pick ×1: altra scelta

✅ prove passate all'AI:
   Prove misurate finora (campioni piccoli: sono indizi, non leggi).
   - PAPER (vissuto, 196 trade chiusi): profit factor 0.698 contro 2.021 promesso dal gate.
   - Escursione favorevole mediana 0.85R contro un primo take-profit a 1.5R: il prezzo si ferma prima di arrivare al primo incasso.
   - Direzione long: 89 trade, 48 vinti, PnL -33.42.
   - Direzione short: 115 trade, 68 vinti, PnL -37.40.
   - GATE: su 1320 valutazioni ne passano 0; muoiono soprattutto su pf_ex_top 3 · regime 22 · trades 6 · total_return 1207.
✅ quasi-passaggi letti dall'AI: 40 · 01 Oct 05:00 UTC (1h fa)
   schema: La maggioranza dei quasi-passaggi si ferma su pf_ex_top (circa 24 su 40), cioe' il PF crolla una volta escluso il blocco di trade migliori: segno di dipendenza da pochi outlier. Dominano coin a bassa capitalizzazione/ill
   consigli: Privilegiare edge distribuito su molti trade piccoli (per superare pf_ex_top) evitando coin micro-cap dove il PF dipende da pochi outlier; preferire setup con conteggio trade piu' alto e PF piu' modesto ma stabile. Diffi
[paper] 204 trade chiusi -> scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle 4 fisse, non le sostituisce: sceglie il gate)
✅ scala candidata dal vissuto: [1.0, 1.25, 1.75] (si aggiunge alle fisse, sceglie il gate)

SPESA AI (misurata: token restituiti dall'API × prezzo configurato 5/25 $ per milione letti/scritti; la fattura vera e' nella console Anthropic)
💶 ieri (30 set, giornata intera ora italiana): 2,80 $ in 57 chiamate
   idee di strategie nuove da far provare al gate (ai-hypotheses): 16 chiamate · 33 mila token letti + 55 mila scritti · 1,54 $ · 55% della spesa di ieri
   lettura delle strategie quasi promosse per dare consigli alla ricerca (ai-autopsia): 16 chiamate · 52 mila token letti + 12 mila scritti · 0,56 $ · 20% della spesa di ieri
   filtro delle monete su cui cercare (ai-universe): 10 chiamate · 18 mila token letti + 15 mila scritti · 0,46 $ · 16% della spesa di ieri
   ombra: cosa farebbe l'AI al posto del bot, solo misura (ai-shadow): 14 chiamate · 12 mila token letti + 7,2 mila scritti · 0,24 $ · 9% della spesa di ieri
   prova di collegamento della chiave (ai-connettivita): 1 chiamata · 8 token letti + 5 scritti · 0,0002 $ · 0% della spesa di ieri
💶 oggi fino alle 08:13 ora italiana: 0,53 $ in 8 chiamate
   ultimi 7 giorni completi: media 2,80 $ al giorno su 1 giorno con dati → circa 84 $ al mese (media × 30) (escluso 29 set: misurato solo in parte)
➖ 1 chiamata fra ieri e oggi per «prova di collegamento della chiave» (ai-connettivita, circa 0,0002 $) ha usato il modello «claude-opus-5» invece di quello della VPS «claude-opus-4-8» (probabile runner GitHub: segreto ANTHROPIC_MODEL): cifra trascurabile, contata col prezzo della VPS
➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: stessa chiave, ma non passano da questo codice) e il controllo della chiave del mattino (~0,0002 $: questo report non scrive nulla)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
