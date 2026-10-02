# 0439-2ott-r1-finestra.req

_eseguito: 2026-10-02 12:48 UTC_

**richiesta:** `replay-gate-esito`
**eseguito:** `.venv/bin/python -m scripts.replay_gate --esito`
**esito:** codice 0 in 1.5s

```
[r1] ultimo lancio: referto scritto 2026-10-02 12:48:06 UTC · processo 2005911 ANCORA IN CORSO
  ultime righe del referto:
  | [r1] 2026-09-03 IOTAUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2190 trade dopo, 159s
  | [backtest] dati da cache: 32113 candele (CCUSDT 15m)
  | [backtest] dati da cache: 59951 candele (PROMUSDT 15m)
  | [r1] 2026-09-03 PROMUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2137 trade dopo, 53s
  | [backtest] dati da cache: 129109 candele (MAGICUSDT 15m)
  | [r1] 2026-09-03 MAGICUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2234 trade dopo, 119s
  | [backtest] dati da cache: 99693 candele (ONGUSDT 15m)
  | [r1] 2026-09-03 ONGUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 1963 trade dopo, 90s
  | [backtest] dati da cache: 46333 candele (LAUSDT 15m)
  | [r1] 2026-09-03 LAUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2076 trade dopo, 38s
  | [backtest] dati da cache: 38287 candele (HEMIUSDT 15m)
  | [r1] 2026-09-03 HEMIUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 1903 trade dopo, 31s
--------------------------------------------------------------------------
[r1] AVANZAMENTO · date complete 1 su 26 · unita' (coin x data) chiuse 358 su 5200 · ok 283 · storia 75
  candidate giudicate 14150 (passate 0) · trade dopo la data: passate 0, bocciate 570092 · piano del 2026-10-01: 50 candidate per data, 200 monete, date 2025-10-02 -> 2026-09-17
  tempo medio misurato per unita' 110s: per le 4842 rimaste STIMA ~37.0 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove coi soli dati fino alla data; poi i trade del motore delle stesse candidate entrati nei 14 giorni dopo, in R netto, con l'uscita scelta dal gate. «Passate» (tutto il gate, holdout compreso) contro «bocciate»: R medio a trade e differenza passate - bocciate; margine = 2 errori standard, il piu' largo fra quello per data e quello trade per trade. Almeno 80 trade delle passate, altrimenti «non si sa». Differenza oltre il margine -> il gate ha un vantaggio vero (il problema e' il mercato o il bot). Differenza + margine sotto 0,10R -> il gate sceglie soprattutto fortuna (la prossima modifica va nel gate). Altrimenti -> non si sa.
  passate: 0 trade · bocciate: 570092 trade, R medio -0.11R · differenza n.d.R · margine n.d. (2 errori standard: per data n.d., trade per trade n.d.; vale il piu' largo)
  LETTURA PARZIALE (1 date complete su 26: non decide ancora): NON SI SA — 0 trade delle passate, ne servono 80.
  per data (* = completa; solo informativo):
    2026-09-17 * coin 161 · passate   0 · trade    0   n.d.R · bocciate trade 311663  -0.08R
    2026-09-03   coin 122 · passate   0 · trade    0   n.d.R · bocciate trade 258429  -0.14R
  bocciate per criterio: total_return 12622, trades 706, recovery 486, regime 214, pf_ex_top 64, consistency 55
  trade fuori dal conto: 1325 ancora aperti a fine dati, 9 senza stop
  limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data): alzano il livello di tutti, pesano poco sul confronto. Non e' il gate di produzione: la vita del registro non c'e'.
```
