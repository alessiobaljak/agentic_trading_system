# 0506-5ott-finestra-esito.req

_eseguito: 2026-10-05 11:56 UTC_

**richiesta:** `replay-gate-esito`
**eseguito:** `.venv/bin/python -m scripts.replay_gate --esito`
**esito:** codice 0 in 1.5s

```
[r1] ultimo lancio: referto scritto 2026-10-05 11:48:45 UTC · processo 2156535 finito
  ultime righe del referto:
  |     2026-09-03 * coin  68 · passate   0 · trade    0   n.d.R · bocciate trade 142204  -0.13R
  |     2026-08-20 * coin  63 · passate   2 · trade    6  -0.43R · bocciate trade 131202  -0.10R · diff -0.34
  |     2026-08-06 * coin  61 · passate   2 · trade   21  -0.35R · bocciate trade 135129  -0.15R · diff -0.20
  |     2026-07-23 * coin  60 · passate   0 · trade    0   n.d.R · bocciate trade  81098  -0.20R
  |     2026-07-09 * coin  58 · passate   0 · trade    0   n.d.R · bocciate trade 111697  -0.22R
  |     2026-06-25 * coin  56 · passate   0 · trade    0   n.d.R · bocciate trade 114309  -0.15R
  |     2026-06-11 * coin  56 · passate   1 · trade    8  +0.07R · bocciate trade 122377  -0.14R · diff +0.20
  |     2026-05-28   coin  19 · passate   1 · trade   10  -0.05R · bocciate trade  44449  -0.11R · diff +0.06
  |   differenza positiva in 2 date su 4 con trade da tutti e due i lati (informativo)
  |   bocciate per criterio: total_return 21720, trades 1653, recovery 1194, regime 662, pf_ex_top 192, consistency 183
  |   trade fuori dal conto: 217 ancora aperti a fine dati, 0 senza stop
  |   limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data
--------------------------------------------------------------------------
[r2] TARATURA DI R1 · candidate del 2026-09-17 giudicate dal gate di OGGI su 72/72 monete · 3600 coppie · PASSATE 0
  REGOLA R2 (3 ott, scritta prima dei numeri): >= 3 passate -> R1 e' piu' severo del gate, si ferma finche' non e' corretto; 0-1 -> lo 0 di R1 e' vero, cambio di piano; 2 -> non si decide
  bocciate per criterio: total_return 3175, recovery 150, trades 146, regime 77, pf_ex_top 31, consistency 19
  ESITO R2: lo 0 di R1 e' vero: le candidate a caso quasi non passano nemmeno nel gate di oggi. Scatta il cambio di piano del 2 ott (lo decide il proprietario)
[g7] IL GATE SUL PREZZO CASUALE (1h) · 100 candidate nuove (seme 20261004) · monete a confronto 72/72 · unita' scritte: ok 144
  REGOLA G7 (4 ott, scritta prima dei numeri): le stesse candidate nuove sulle stesse monete, giudicate dal gate di oggi sulle candele vere e sulle stesse candele rimescolate: quota sul caso >= meta' di quella vera -> il gate passa soprattutto rumore (la prossima modifica va nelle soglie del gate); <= un quinto -> il gate filtra il rumore (il problema del paper e' altrove); altrimenti non si sa; con meno di 10 passate sul vero non si sa
  candele vere: 8 passate su 7200 prove = 0.11% · bocciate per criterio: total_return 4364, regime 897, recovery 842, trades 643, consistency 250
  candele rimescolate: 16 passate su 7200 prove = 0.22% · bocciate per criterio: total_return 4141, recovery 1119, regime 817, trades 643, consistency 254
  rapporto caso/vero: 2.00
  ESITO G7: NON SI SA: sulle candele vere passano solo 8 candidate nuove (ne servono 10 per leggere il rapporto)
[r1] AVANZAMENTO · date complete 8 su 26 · unita' (coin x data) chiuse 597 su 1872 · ok 513 · storia 84
  candidate giudicate 25631 (passate 6) · trade dopo la data: passate 45, bocciate 1022989 · piano del 2026-10-01: 50 candidate per data, 72 monete, date 2025-10-02 -> 2026-09-17
  tempo medio misurato per unita' 79s: per le 1275 rimaste STIMA ~7.0 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove coi soli dati fino alla data; poi i trade del motore delle stesse candidate entrati nei 14 giorni dopo, in R netto, con l'uscita scelta dal gate. «Passate» (tutto il gate, holdout compreso) contro «bocciate»: R medio a trade e differenza passate - bocciate; margine = 2 errori standard, il piu' largo fra quello per data e quello trade per trade. Almeno 80 trade delle passate, altrimenti «non si sa». Differenza oltre il margine -> il gate ha un vantaggio vero (il problema e' il mercato o il bot). Differenza + margine sotto 0,10R -> il gate sceglie soprattutto fortuna (la prossima modifica va nel gate). Altrimenti -> non si sa.
  passate: 45 trade, R medio -0.22R · bocciate: 1022989 trade, R medio -0.14R · differenza -0.08R · margine ±0.31 (2 errori standard: per data 0.20, trade per trade 0.31; vale il piu' largo)
  LETTURA PARZIALE (8 date complete su 26: non decide ancora): NON SI SA — 45 trade delle passate, ne servono 80.
  per data (* = completa; solo informativo):
    2026-09-17 * coin  72 · passate   0 · trade    0   n.d.R · bocciate trade 140524  -0.10R
    2026-09-03 * coin  68 · passate   0 · trade    0   n.d.R · bocciate trade 142204  -0.13R
    2026-08-20 * coin  63 · passate   2 · trade    6  -0.43R · bocciate trade 131202  -0.10R · diff -0.34
    2026-08-06 * coin  61 · passate   2 · trade   21  -0.35R · bocciate trade 135129  -0.15R · diff -0.20
    2026-07-23 * coin  60 · passate   0 · trade    0   n.d.R · bocciate trade  81098  -0.20R
    2026-07-09 * coin  58 · passate   0 · trade    0   n.d.R · bocciate trade 111697  -0.22R
    2026-06-25 * coin  56 · passate   0 · trade    0   n.d.R · bocciate trade 114309  -0.15R
    2026-06-11 * coin  56 · passate   1 · trade    8  +0.07R · bocciate trade 122377  -0.14R · diff +0.20
    2026-05-28   coin  19 · passate   1 · trade   10  -0.05R · bocciate trade  44449  -0.11R · diff +0.06
  differenza positiva in 2 date su 4 con trade da tutti e due i lati (informativo)
  bocciate per criterio: total_return 21720, trades 1653, recovery 1194, regime 662, pf_ex_top 192, consistency 183
  trade fuori dal conto: 217 ancora aperti a fine dati, 0 senza stop
  limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data): alzano il livello di tutti, pesano poco sul confronto. Non e' il gate di produzione: la vita del registro non c'e'.
```
