# 0396-1ott-selettore.req

_eseguito: 2026-10-01 06:18 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 53.2s

```
[selettore] 99688 trade da 479 file (320233 duplicati fusi, 382203 gemelle fuse, 0 righe rotte saltate)
[selettore] 1441 coppie coin+strategia; famiglie: reversion 68273, momentum 30085, breakout 1330
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 99688 trade usabili, 44508 di spec passate e 55180 di bocciate, dal 2023-02-27 al 2026-08-16
  finestra 1 [2025-11-07 -> 2026-02-10] train 39875 | soglia 0.50
     apri tutto: n 19938  pnl +85.2823  dd 1.8309  wr 66.1%  metro +83.4514
     selezione : n 19933  pnl +85.1718  dd 1.8309  wr 66.1%  metro +83.3410  -> non batte (margine -0.1104, p_perm 0.970, 95° perc. +83.5233)
     con size  : n 19933  pnl +70.8375  dd 1.3804  metro +69.4571  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9892 | apri tutto pnl +49.1162 metro +48.4220 | selezione n 9889 pnl +49.0512 metro +48.3570
     solo bocciate: n 10046 | apri tutto pnl +36.1661 metro +35.0070 | selezione n 10044 pnl +36.1206 metro +34.9615
  finestra 2 [2026-02-10 -> 2026-05-13] train 59813 | soglia 0.45
     apri tutto: n 19937  pnl +88.1139  dd 0.9571  wr 66.2%  metro +87.1568
     selezione : n 19937  pnl +88.1139  dd 0.9571  wr 66.2%  metro +87.1568  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +87.1568)
     con size  : n 19937  pnl +82.8108  dd 0.7995  metro +82.0113  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9908 | apri tutto pnl +53.0547 metro +52.4491 | selezione n 9908 pnl +53.0547 metro +52.4491
     solo bocciate: n 10029 | apri tutto pnl +35.0592 metro +34.3832 | selezione n 10029 pnl +35.0592 metro +34.3832
  finestra 3 [2026-05-13 -> 2026-08-16] train 79750 | soglia 0.40
     apri tutto: n 19938  pnl +98.9038  dd 0.7900  wr 66.7%  metro +98.1138
     selezione : n 19938  pnl +98.9038  dd 0.7900  wr 66.7%  metro +98.1138  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +98.1138)
     con size  : n 19938  pnl +102.7698  dd 0.8326  metro +101.9372  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10146 | apri tutto pnl +58.8713 metro +58.3611 | selezione n 10146 pnl +58.8713 metro +58.3611
     solo bocciate: n 9792 | apri tutto pnl +40.0325 metro +39.5861 | selezione n 9792 pnl +40.0325 metro +39.5861
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 68273 trade usabili, 31223 di spec passate e 37050 di bocciate, dal 2023-02-27 al 2026-08-16
  finestra 1 [2025-11-12 -> 2026-02-11] train 27309 | soglia 0.40
     apri tutto: n 13655  pnl +57.9328  dd 2.1975  wr 66.5%  metro +55.7353
     selezione : n 13655  pnl +57.9328  dd 2.1975  wr 66.5%  metro +55.7353  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +55.7353)
     con size  : n 13655  pnl +60.9113  dd 2.1461  metro +58.7652  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7134 | apri tutto pnl +34.4249 metro +33.4571 | selezione n 7134 pnl +34.4249 metro +33.4571
     solo bocciate: n 6521 | apri tutto pnl +23.5079 metro +22.0018 | selezione n 6521 pnl +23.5079 metro +22.0018
  finestra 2 [2026-02-11 -> 2026-05-14] train 40964 | soglia 0.50
     apri tutto: n 13654  pnl +54.9124  dd 0.9764  wr 66.2%  metro +53.9359
     selezione : n 13636  pnl +55.0080  dd 0.9764  wr 66.3%  metro +54.0316  -> BATTE (margine +0.0957, p_perm 0.035, 95° perc. +54.0211)
     con size  : n 13636  pnl +47.4870  dd 0.7924  metro +46.6945  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7358 | apri tutto pnl +36.4558 metro +35.8671 | selezione n 7351 pnl +36.5038 metro +35.9151
     solo bocciate: n 6296 | apri tutto pnl +18.4566 metro +17.8249 | selezione n 6285 pnl +18.5042 metro +17.8726
  finestra 3 [2026-05-14 -> 2026-08-16] train 54618 | soglia 0.50
     apri tutto: n 13655  pnl +66.5918  dd 0.7181  wr 67.8%  metro +65.8737
     selezione : n 13643  pnl +66.5780  dd 0.7181  wr 67.8%  metro +65.8598  -> non batte (margine -0.0138, p_perm 0.320, 95° perc. +65.9519)
     con size  : n 13643  pnl +56.4534  dd 0.5299  metro +55.9236  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7632 | apri tutto pnl +41.6158 metro +41.1217 | selezione n 7624 pnl +41.6741 metro +41.1800
     solo bocciate: n 6023 | apri tutto pnl +24.9760 metro +24.4371 | selezione n 6019 pnl +24.9039 metro +24.3650
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 30085 trade usabili, 12497 di spec passate e 17588 di bocciate, dal 2023-03-01 al 2026-08-16
  finestra 1 [2025-10-24 -> 2026-02-05] train 12034 | soglia 0.40
     apri tutto: n 6017  pnl +26.7984  dd 0.7010  wr 65.0%  metro +26.0974
     selezione : n 6017  pnl +26.7984  dd 0.7010  wr 65.0%  metro +26.0974  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +26.0974)
     con size  : n 6017  pnl +27.2029  dd 0.7016  metro +26.5013  (informativo: il verdetto e' sulla selezione)
     solo passate : n 2614 | apri tutto pnl +14.0849 metro +13.6229 | selezione n 2614 pnl +14.0849 metro +13.6229
     solo bocciate: n 3403 | apri tutto pnl +12.7134 metro +12.1923 | selezione n 3403 pnl +12.7134 metro +12.1923
  finestra 2 [2026-02-05 -> 2026-05-11] train 18051 | soglia 0.40
     apri tutto: n 6017  pnl +30.5594  dd 0.5735  wr 65.9%  metro +29.9859
     selezione : n 6017  pnl +30.5594  dd 0.5735  wr 65.9%  metro +29.9859  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +29.9859)
     con size  : n 6017  pnl +31.1146  dd 0.5903  metro +30.5242  (informativo: il verdetto e' sulla selezione)
     solo passate : n 2384 | apri tutto pnl +15.2205 metro +14.8558 | selezione n 2384 pnl +15.2205 metro +14.8558
     solo bocciate: n 3633 | apri tutto pnl +15.3389 metro +14.6951 | selezione n 3633 pnl +15.3389 metro +14.6951
  finestra 3 [2026-05-11 -> 2026-08-16] train 24068 | soglia 0.40
     apri tutto: n 6017  pnl +31.1974  dd 0.4669  wr 64.5%  metro +30.7305
     selezione : n 6017  pnl +31.1974  dd 0.4669  wr 64.5%  metro +30.7305  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +30.7305)
     con size  : n 6017  pnl +32.0619  dd 0.4744  metro +31.5875  (informativo: il verdetto e' sulla selezione)
     solo passate : n 2380 | apri tutto pnl +16.0159 metro +15.4713 | selezione n 2380 pnl +16.0159 metro +15.4713
     solo bocciate: n 3637 | apri tutto pnl +15.1815 metro +14.5296 | selezione n 3637 pnl +15.1815 metro +14.5296
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1330 trade usabili, 788 di spec passate e 542 di bocciate, dal 2024-01-23 al 2026-08-15
  finestra 1 [2025-12-15 -> 2026-03-06] train   532 | soglia 0.55
     apri tutto: n  266  pnl +1.2816  dd 0.2210  wr 62.4%  metro +1.0606
     selezione : n  202  pnl +0.7713  dd 0.1740  wr 63.9%  metro +0.5974  -> non batte (margine -0.4632, p_perm 0.790, 95° perc. +1.1232)
     con size  : n  202  pnl +0.4787  dd 0.1334  metro +0.3454  (informativo: il verdetto e' sulla selezione)
     solo passate : n  122 | apri tutto pnl +0.9522 metro +0.7148 | selezione n   88 pnl +0.3503 metro +0.1596
     solo bocciate: n  144 | apri tutto pnl +0.3295 metro +0.1425 | selezione n  114 pnl +0.4210 metro +0.3345
  finestra 2 [2026-03-06 -> 2026-05-24] train   798 | soglia 0.45
     apri tutto: n  266  pnl +2.2791  dd 0.3006  wr 69.2%  metro +1.9785
     selezione : n  249  pnl +2.0589  dd 0.2420  wr 69.9%  metro +1.8168  -> non batte (margine -0.1617, p_perm 0.520, 95° perc. +2.0357)
     con size  : n  249  pnl +1.7507  dd 0.1881  metro +1.5626  (informativo: il verdetto e' sulla selezione)
     solo passate : n  139 | apri tutto pnl +1.5902 metro +1.4228 | selezione n  126 pnl +1.3811 metro +1.2259
     solo bocciate: n  127 | apri tutto pnl +0.6889 metro +0.5158 | selezione n  123 pnl +0.6778 metro +0.5360
  finestra 3 [2026-05-24 -> 2026-08-15] train  1064 | soglia 0.45
     apri tutto: n  266  pnl +1.2248  dd 0.2438  wr 57.9%  metro +0.9811
     selezione : n  261  pnl +0.9777  dd 0.2466  wr 57.5%  metro +0.7311  -> non batte (margine -0.2500, p_perm 0.965, 95° perc. +1.0807)
     con size  : n  261  pnl +0.9292  dd 0.2246  metro +0.7046  (informativo: il verdetto e' sulla selezione)
     solo passate : n  126 | apri tutto pnl +0.8048 metro +0.5929 | selezione n  125 pnl +0.6726 metro +0.4607
     solo bocciate: n  140 | apri tutto pnl +0.4200 metro +0.1248 | selezione n  136 pnl +0.3051 metro +0.0099
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 99688, lam 1.0, intercetta +0.683 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.189
    stop_pct   +0.063
    long_x_banda -0.052
    bb_pos     +0.050
    dist_ema   -0.033
    vol_ratio  -0.029
    is_long    -0.024
    rsi        -0.023
    atr_pct    +0.017
    hour_sin   -0.015
    regime_bull -0.014
    stoch_k    -0.013
    market_up  +0.010
    hour_cos   +0.009
    regime_incerto -0.007
    regime_bear -0.004
    adx        +0.003
    long_x_mercato -0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 99688 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 51.7s
```
