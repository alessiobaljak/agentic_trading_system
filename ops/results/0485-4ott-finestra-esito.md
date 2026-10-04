# 0485-4ott-finestra-esito.req

_eseguito: 2026-10-04 11:53 UTC_

**richiesta:** `replay-gate-esito`
**eseguito:** `.venv/bin/python -m scripts.replay_gate --esito`
**esito:** codice 0 in 1.5s

```
[r1] ultimo lancio: referto scritto 2026-10-04 11:53:29 UTC · processo 2107931 ANCORA IN CORSO
  ultime righe del referto:
  | [backtest] dati da cache: 43837 candele (BULLAUSDT 15m)
  | [r1] 2026-08-20 BULLAUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 1805 trade dopo, 40s
  | [backtest] dati da cache: 54187 candele (BMTUSDT 15m)
  | [r1] 2026-08-20 BMTUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2089 trade dopo, 49s
  | [backtest] dati da cache: 43255 candele (CROSSUSDT 15m)
  | [r1] 2026-08-20 CROSSUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2114 trade dopo, 36s
  | [backtest] dati da cache: 71283 candele (CATIUSDT 15m)
  | [r1] 2026-08-20 CATIUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 1862 trade dopo, 67s
  | [backtest] dati da cache: 48447 candele (CVCUSDT 15m)
  | [r1] 2026-08-20 CVCUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 2092 trade dopo, 43s
  | [backtest] dati da cache: 62258 candele (DEXEUSDT 15m)
  | [r1] 2026-08-20 DEXEUSDT: 50 candidate, 0 passate (0 trade dopo), bocciate 1992 trade dopo, 57s
--------------------------------------------------------------------------
[r2] TARATURA DI R1 · candidate del 2026-09-17 giudicate dal gate di OGGI su 72/72 monete · 3600 coppie · PASSATE 0
  REGOLA R2 (3 ott, scritta prima dei numeri): >= 3 passate -> R1 e' piu' severo del gate, si ferma finche' non e' corretto; 0-1 -> lo 0 di R1 e' vero, cambio di piano; 2 -> non si decide
  bocciate per criterio: total_return 3175, recovery 150, trades 146, regime 77, pf_ex_top 31, consistency 19
  ESITO R2: lo 0 di R1 e' vero: le candidate a caso quasi non passano nemmeno nel gate di oggi. Scatta il cambio di piano del 2 ott (lo decide il proprietario)
[g7] IL GATE SUL PREZZO CASUALE (1h) · 100 candidate nuove (seme 20261004) · monete a confronto 0/72
  REGOLA G7 (4 ott, scritta prima dei numeri): le stesse candidate nuove sulle stesse monete, giudicate dal gate di oggi sulle candele vere e sulle stesse candele rimescolate: quota sul caso >= meta' di quella vera -> il gate passa soprattutto rumore (la prossima modifica va nelle soglie del gate); <= un quinto -> il gate filtra il rumore (il problema del paper e' altrove); altrimenti non si sa; con meno di 10 passate sul vero non si sa
  candele vere: 0 passate su 0 prove = n.d.
  candele rimescolate: 0 passate su 0 prove = n.d.
  rapporto caso/vero: n.d.
  ESITO G7: in corso (PARZIALE)
[r1] AVANZAMENTO · date complete 2 su 26 · unita' (coin x data) chiuse 190 su 1872 · ok 181 · storia 9
  candidate giudicate 9050 (passate 1) · trade dopo la data: passate 2, bocciate 367936 · piano del 2026-10-01: 50 candidate per data, 72 monete, date 2025-10-02 -> 2026-09-17
  tempo medio misurato per unita' 78s: per le 1682 rimaste STIMA ~9.1 ore con 4 worker (un tetto: le unita' senza storia costano meno)
  REGOLA R1 (scritta prima dei numeri, docs/andremo_live.md): a ogni data il gate (soglie di oggi, niente AI, niente vita del registro) giudica candidate nuove coi soli dati fino alla data; poi i trade del motore delle stesse candidate entrati nei 14 giorni dopo, in R netto, con l'uscita scelta dal gate. «Passate» (tutto il gate, holdout compreso) contro «bocciate»: R medio a trade e differenza passate - bocciate; margine = 2 errori standard, il piu' largo fra quello per data e quello trade per trade. Almeno 80 trade delle passate, altrimenti «non si sa». Differenza oltre il margine -> il gate ha un vantaggio vero (il problema e' il mercato o il bot). Differenza + margine sotto 0,10R -> il gate sceglie soprattutto fortuna (la prossima modifica va nel gate). Altrimenti -> non si sa.
  passate: 2 trade, R medio +0.89R · bocciate: 367936 trade, R medio -0.11R · differenza +1.00R · margine ±0.89 (2 errori standard: per data 0.02, trade per trade 0.89; vale il piu' largo)
  LETTURA PARZIALE (2 date complete su 26: non decide ancora): NON SI SA — 2 trade delle passate, ne servono 80.
  per data (* = completa; solo informativo):
    2026-09-17 * coin  72 · passate   0 · trade    0   n.d.R · bocciate trade 140524  -0.10R
    2026-09-03 * coin  68 · passate   0 · trade    0   n.d.R · bocciate trade 142204  -0.13R
    2026-08-20   coin  41 · passate   1 · trade    2  +0.89R · bocciate trade  85208  -0.08R · diff +0.98
  differenza positiva in 1 date su 1 con trade da tutti e due i lati (informativo)
  bocciate per criterio: total_return 7920, trades 442, recovery 374, regime 203, pf_ex_top 57, consistency 49
  trade fuori dal conto: 217 ancora aperti a fine dati, 0 senza stop
  limiti dichiarati: monete di oggi (le sopravvissute), motore senza scivolamento, niente AI, funding medio della coin dagli ultimi ~11 mesi (anche dopo la data): alzano il livello di tutti, pesano poco sul confronto. Non e' il gate di produzione: la vita del registro non c'e'.
```
