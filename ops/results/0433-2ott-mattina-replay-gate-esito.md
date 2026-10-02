# 0433-2ott-mattina-replay-gate-esito.req

_eseguito: 2026-10-02 06:17 UTC_

**richiesta:** `replay-gate-esito`
**eseguito:** `.venv/bin/python -m scripts.replay_gate --esito`
**esito:** codice 0 in 1.3s

```
[r1] ultimo lancio: referto scritto 2026-10-01 20:52:15 UTC · processo 1979850 finito
  ultime righe del referto:
  | 
  | [r1] AVANZAMENTO · date complete 0 su 26 · unita' (coin x data) chiuse 85 su 5200 · ok 67 · storia 18
  |   candidate giudicate 3350 (passate 0) · trade dopo la data: passate 0, bocciate 123759 · piano del 2026-10-01: 50 candidate per data, 200 monete, date 2025-10-
  |   tempo medio misurato per unita' 129s: per le 5115 rimaste STIMA ~45.8 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  |   REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove 
  |   passate: 0 trade · bocciate: 123759 trade, R medio -0.07R · differenza n.d.R · margine n.d. (2 errori standard: per data n.d., trade per trade n.d.; vale il p
  |   LETTURA PARZIALE (0 date complete su 26: non decide ancora): NON SI SA — 0 trade delle passate, ne servono 80.
  |   per data (* = completa; solo informativo):
  |     2026-09-17   coin  67 · passate   0 · trade    0   n.d.R · bocciate trade 123759  -0.07R
  |   bocciate per criterio: total_return 3008, trades 131, recovery 121, regime 54, pf_ex_top 25, consistency 11
  |   trade fuori dal conto: 876 ancora aperti a fine dati, 0 senza stop
  |   limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data
--------------------------------------------------------------------------
[r1] AVANZAMENTO · date complete 0 su 26 · unita' (coin x data) chiuse 85 su 5200 · ok 67 · storia 18
  candidate giudicate 3350 (passate 0) · trade dopo la data: passate 0, bocciate 123759 · piano del 2026-10-01: 50 candidate per data, 200 monete, date 2025-10-02 -> 2026-09-17
  tempo medio misurato per unita' 129s: per le 5115 rimaste STIMA ~45.8 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove coi soli dati fino alla data; poi i trade del motore delle stesse candidate entrati nei 14 giorni dopo, in R netto, con l'uscita scelta dal gate. «Passate» (tutto il gate, holdout compreso) contro «bocciate»: R medio a trade e differenza passate - bocciate; margine = 2 errori standard, il piu' largo fra quello per data e quello trade per trade. Almeno 80 trade delle passate, altrimenti «non si sa». Differenza oltre il margine -> il gate ha un vantaggio vero (il problema e' il mercato o il bot). Differenza + margine sotto 0,10R -> il gate sceglie soprattutto fortuna (la prossima modifica va nel gate). Altrimenti -> non si sa.
  passate: 0 trade · bocciate: 123759 trade, R medio -0.07R · differenza n.d.R · margine n.d. (2 errori standard: per data n.d., trade per trade n.d.; vale il piu' largo)
  LETTURA PARZIALE (0 date complete su 26: non decide ancora): NON SI SA — 0 trade delle passate, ne servono 80.
  per data (* = completa; solo informativo):
    2026-09-17   coin  67 · passate   0 · trade    0   n.d.R · bocciate trade 123759  -0.07R
  bocciate per criterio: total_return 3008, trades 131, recovery 121, regime 54, pf_ex_top 25, consistency 11
  trade fuori dal conto: 876 ancora aperti a fine dati, 0 senza stop
  limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data): alzano il livello di tutti, pesano poco sul confronto. Non e' il gate di produzione: la vita del registro non c'e'.
```
