# 0463-3ott-pomeriggio-replay-gate-esito.req

_eseguito: 2026-10-03 14:50 UTC_

**richiesta:** `replay-gate-esito`
**eseguito:** `.venv/bin/python -m scripts.replay_gate --esito`
**esito:** codice 0 in 1.4s

```
[r1] ultimo lancio: referto scritto 2026-10-03 08:13:38 UTC · processo 2053452 finito
  ultime righe del referto:
  | [r1] AVANZAMENTO · date complete 2 su 26 · unita' (coin x data) chiuse 144 su 1872 · ok 140 · storia 4
  |   candidate giudicate 7000 (passate 0) · trade dopo la data: passate 0, bocciate 282728 · piano del 2026-10-01: 50 candidate per data, 72 monete, date 2025-10-0
  |   tempo medio misurato per unita' 74s: per le 1728 rimaste STIMA ~8.9 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  |   REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove 
  |   passate: 0 trade · bocciate: 282728 trade, R medio -0.12R · differenza n.d.R · margine n.d. (2 errori standard: per data n.d., trade per trade n.d.; vale il p
  |   LETTURA PARZIALE (2 date complete su 26: non decide ancora): NON SI SA — 0 trade delle passate, ne servono 80.
  |   per data (* = completa; solo informativo):
  |     2026-09-17 * coin  72 · passate   0 · trade    0   n.d.R · bocciate trade 140524  -0.10R
  |     2026-09-03 * coin  68 · passate   0 · trade    0   n.d.R · bocciate trade 142204  -0.13R
  |   bocciate per criterio: total_return 6121, trades 382, recovery 277, regime 150, pf_ex_top 35, consistency 31
  |   trade fuori dal conto: 217 ancora aperti a fine dati, 0 senza stop
  |   limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data
--------------------------------------------------------------------------
[r2] taratura di R1 (le sue 50 candidate del 17 set nel gate di oggi): non ancora fatta, parte all'inizio del prossimo lancio
[r1] AVANZAMENTO · date complete 2 su 26 · unita' (coin x data) chiuse 144 su 1872 · ok 140 · storia 4
  candidate giudicate 7000 (passate 0) · trade dopo la data: passate 0, bocciate 282728 · piano del 2026-10-01: 50 candidate per data, 72 monete, date 2025-10-02 -> 2026-09-17
  tempo medio misurato per unita' 74s: per le 1728 rimaste STIMA ~8.9 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove coi soli dati fino alla data; poi i trade del motore delle stesse candidate entrati nei 14 giorni dopo, in R netto, con l'uscita scelta dal gate. «Passate» (tutto il gate, holdout compreso) contro «bocciate»: R medio a trade e differenza passate - bocciate; margine = 2 errori standard, il piu' largo fra quello per data e quello trade per trade. Almeno 80 trade delle passate, altrimenti «non si sa». Differenza oltre il margine -> il gate ha un vantaggio vero (il problema e' il mercato o il bot). Differenza + margine sotto 0,10R -> il gate sceglie soprattutto fortuna (la prossima modifica va nel gate). Altrimenti -> non si sa.
  passate: 0 trade · bocciate: 282728 trade, R medio -0.12R · differenza n.d.R · margine n.d. (2 errori standard: per data n.d., trade per trade n.d.; vale il piu' largo)
  LETTURA PARZIALE (2 date complete su 26: non decide ancora): NON SI SA — 0 trade delle passate, ne servono 80.
  per data (* = completa; solo informativo):
    2026-09-17 * coin  72 · passate   0 · trade    0   n.d.R · bocciate trade 140524  -0.10R
    2026-09-03 * coin  68 · passate   0 · trade    0   n.d.R · bocciate trade 142204  -0.13R
  bocciate per criterio: total_return 6121, trades 382, recovery 277, regime 150, pf_ex_top 35, consistency 31
  trade fuori dal conto: 217 ancora aperti a fine dati, 0 senza stop
  limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data): alzano il livello di tutti, pesano poco sul confronto. Non e' il gate di produzione: la vita del registro non c'e'.
```
