# 0604-12ott-analisi-trade-selettore.req

_eseguito: 2026-10-12 17:49 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 169.8s

```
[selettore] 150015 trade da 1280 file (1412413 duplicati fusi, 3217696 gemelle fuse, 0 righe rotte saltate)
[selettore] 2608 coppie coin+strategia; famiglie: reversion 98135, momentum 49893, breakout 1923, altro 64
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 150003 trade usabili (12 scartati: variabili mancanti), 85262 di spec passate e 64741 di bocciate, dal 2023-03-01 al 2026-08-27
  finestra 1 [2025-11-27 -> 2026-02-24] train 60001 | soglia 0.40
     apri tutto: n 30001  pnl +134.1151  dd 1.9156  wr 66.6%  metro +132.1995
     selezione : n 30001  pnl +134.1151  dd 1.9156  wr 66.6%  metro +132.1995  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +132.1995)
     con size  : n 30001  pnl +140.3730  dd 1.7929  metro +138.5801  (informativo: il verdetto e' sulla selezione)
     solo passate : n 19168 | apri tutto pnl +100.9037 metro +100.0805 | selezione n 19168 pnl +100.9037 metro +100.0805
     solo bocciate: n 10833 | apri tutto pnl +33.2113 metro +31.9614 | selezione n 10833 pnl +33.2113 metro +31.9614
  finestra 2 [2026-02-24 -> 2026-05-25] train 90002 | soglia 0.40
     apri tutto: n 30000  pnl +132.2307  dd 1.2224  wr 66.3%  metro +131.0084
     selezione : n 30000  pnl +132.2307  dd 1.2224  wr 66.3%  metro +131.0084  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +131.0084)
     con size  : n 30000  pnl +138.7050  dd 1.2361  metro +137.4689  (informativo: il verdetto e' sulla selezione)
     solo passate : n 19193 | apri tutto pnl +98.3604 metro +97.6145 | selezione n 19193 pnl +98.3604 metro +97.6145
     solo bocciate: n 10807 | apri tutto pnl +33.8703 metro +33.2334 | selezione n 10807 pnl +33.8703 metro +33.2334
  finestra 3 [2026-05-25 -> 2026-08-27] train 120002 | soglia 0.45
     apri tutto: n 30001  pnl +159.8147  dd 0.5881  wr 67.9%  metro +159.2266
     selezione : n 30001  pnl +159.8147  dd 0.5881  wr 67.9%  metro +159.2266  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +159.2266)
     con size  : n 30001  pnl +152.2351  dd 0.5302  metro +151.7049  (informativo: il verdetto e' sulla selezione)
     solo passate : n 19379 | apri tutto pnl +116.7835 metro +116.2500 | selezione n 19379 pnl +116.7835 metro +116.2500
     solo bocciate: n 10622 | apri tutto pnl +43.0312 metro +42.5790 | selezione n 10622 pnl +43.0312 metro +42.5790
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 98123 trade usabili (12 scartati: variabili mancanti), 52965 di spec passate e 45158 di bocciate, dal 2023-03-01 al 2026-08-27
  finestra 1 [2025-12-05 -> 2026-02-28] train 39249 | soglia 0.40
     apri tutto: n 19625  pnl +92.9961  dd 2.7216  wr 67.2%  metro +90.2745
     selezione : n 19624  pnl +93.0115  dd 2.7216  wr 67.2%  metro +90.2899  -> non batte (margine +0.0154, p_perm 0.195, 95° perc. +90.3042)
     con size  : n 19624  pnl +98.2141  dd 2.6080  metro +95.6060  (informativo: il verdetto e' sulla selezione)
     solo passate : n 12220 | apri tutto pnl +67.8468 metro +66.4497 | selezione n 12220 pnl +67.8468 metro +66.4497
     solo bocciate: n 7405 | apri tutto pnl +25.1492 metro +23.8000 | selezione n 7404 pnl +25.1646 metro +23.8154
  finestra 2 [2026-02-28 -> 2026-05-27] train 58874 | soglia 0.45
     apri tutto: n 19624  pnl +79.7335  dd 1.2429  wr 66.2%  metro +78.4907
     selezione : n 19624  pnl +79.7335  dd 1.2429  wr 66.2%  metro +78.4907  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +78.4907)
     con size  : n 19624  pnl +77.5647  dd 1.1245  metro +76.4402  (informativo: il verdetto e' sulla selezione)
     solo passate : n 12273 | apri tutto pnl +57.8215 metro +56.9021 | selezione n 12273 pnl +57.8215 metro +56.9021
     solo bocciate: n 7351 | apri tutto pnl +21.9120 metro +21.3247 | selezione n 7351 pnl +21.9120 metro +21.3247
  finestra 3 [2026-05-27 -> 2026-08-27] train 78498 | soglia 0.50
     apri tutto: n 19625  pnl +107.9796  dd 0.8545  wr 68.9%  metro +107.1251
     selezione : n 19615  pnl +107.7612  dd 0.8545  wr 68.9%  metro +106.9067  -> non batte (margine -0.2184, p_perm 0.975, 95° perc. +107.1880)
     con size  : n 19615  pnl +92.5357  dd 0.6817  metro +91.8540  (informativo: il verdetto e' sulla selezione)
     solo passate : n 12528 | apri tutto pnl +76.5453 metro +75.9866 | selezione n 12519 pnl +76.3662 metro +75.8074
     solo bocciate: n 7097 | apri tutto pnl +31.4343 metro +31.0076 | selezione n 7096 pnl +31.3951 metro +30.9684
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 49893 trade usabili, 30405 di spec passate e 19488 di bocciate, dal 2023-03-01 al 2026-08-27
  finestra 1 [2025-11-10 -> 2026-02-15] train 19957 | soglia 0.50
     apri tutto: n 9979  pnl +45.2878  dd 1.0630  wr 66.2%  metro +44.2248
     selezione : n 9978  pnl +45.3099  dd 1.0630  wr 66.2%  metro +44.2469  -> non batte (margine +0.0221, p_perm 0.190, 95° perc. +44.2656)
     con size  : n 9978  pnl +37.9155  dd 0.9064  metro +37.0091  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6630 | apri tutto pnl +33.9544 metro +32.7917 | selezione n 6629 pnl +33.9766 metro +32.8139
     solo bocciate: n 3349 | apri tutto pnl +11.3334 metro +10.9717 | selezione n 3349 pnl +11.3334 metro +10.9717
  finestra 2 [2026-02-15 -> 2026-05-23] train 29936 | soglia 0.40
     apri tutto: n 9978  pnl +48.4076  dd 0.7869  wr 66.6%  metro +47.6208
     selezione : n 9978  pnl +48.4076  dd 0.7869  wr 66.6%  metro +47.6208  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +47.6208)
     con size  : n 9978  pnl +49.3225  dd 0.8105  metro +48.5120  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6607 | apri tutto pnl +37.9541 metro +37.0957 | selezione n 6607 pnl +37.9541 metro +37.0957
     solo bocciate: n 3371 | apri tutto pnl +10.4535 metro +9.8476 | selezione n 3371 pnl +10.4535 metro +9.8476
  finestra 3 [2026-05-23 -> 2026-08-27] train 39914 | soglia 0.40
     apri tutto: n 9979  pnl +49.3098  dd 1.0069  wr 66.2%  metro +48.3029
     selezione : n 9979  pnl +49.3098  dd 1.0069  wr 66.2%  metro +48.3029  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +48.3029)
     con size  : n 9979  pnl +51.5351  dd 0.9855  metro +50.5496  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6527 | apri tutto pnl +38.2199 metro +37.2117 | selezione n 6527 pnl +38.2199 metro +37.2117
     solo bocciate: n 3452 | apri tutto pnl +11.0899 metro +10.6202 | selezione n 3452 pnl +11.0899 metro +10.6202
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1923 trade usabili, 1828 di spec passate e 95 di bocciate, dal 2024-01-19 al 2026-08-27
  finestra 1 [2025-10-26 -> 2026-01-31] train   769 | soglia 0.60
     apri tutto: n  385  pnl +2.5584  dd 0.3112  wr 67.3%  metro +2.2471
     selezione : n  238  pnl +1.3820  dd 0.3196  wr 68.9%  metro +1.0624  -> non batte (margine -1.1847, p_perm 0.715, 95° perc. +1.8694)
     con size  : n  238  pnl +0.8834  dd 0.2122  metro +0.6712  (informativo: il verdetto e' sulla selezione)
     solo passate : n  358 | apri tutto pnl +2.6590 metro +2.3413 | selezione n  219 pnl +1.3777 metro +1.0511
     solo bocciate: n   27 | apri tutto pnl -0.1006 metro -0.2358 | selezione n   19 pnl +0.0043 metro -0.0417
  finestra 2 [2026-01-31 -> 2026-05-09] train  1154 | soglia 0.55
     apri tutto: n  384  pnl +2.3555  dd 0.2998  wr 63.5%  metro +2.0557
     selezione : n  315  pnl +1.5601  dd 0.3263  wr 63.8%  metro +1.2337  -> non batte (margine -0.8220, p_perm 0.970, 95° perc. +2.1652)
     con size  : n  315  pnl +1.1813  dd 0.2202  metro +0.9611  (informativo: il verdetto e' sulla selezione)
     solo passate : n  362 | apri tutto pnl +2.1896 metro +1.8898 | selezione n  294 pnl +1.4038 metro +0.9872
     solo bocciate: n   22 | apri tutto pnl +0.1659 metro +0.1259 | selezione n   21 pnl +0.1562 metro +0.1163
  finestra 3 [2026-05-10 -> 2026-08-27] train  1538 | soglia 0.45
     apri tutto: n  385  pnl +2.5084  dd 0.4323  wr 63.1%  metro +2.0761
     selezione : n  383  pnl +2.5271  dd 0.4323  wr 63.2%  metro +2.0948  -> non batte (margine +0.0186, p_perm 0.300, 95° perc. +2.1646)
     con size  : n  383  pnl +2.3403  dd 0.3606  metro +1.9797  (informativo: il verdetto e' sulla selezione)
     solo passate : n  359 | apri tutto pnl +2.1193 metro +1.7657 | selezione n  357 pnl +2.1380 metro +1.7844
     solo bocciate: n   26 | apri tutto pnl +0.3891 metro +0.3103 | selezione n   26 pnl +0.3891 metro +0.3103
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[altro] 64 trade usabili, dal 2025-09-07 al 2026-08-25
  finestra 1: train 26 trade < minimo -> campione insufficiente
  finestra 2: train 39 trade < minimo -> campione insufficiente
  finestra 3: train 51 trade < minimo -> campione insufficiente
  VERDETTO: CAMPIONE INSUFFICIENTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 150003, lam 1.0, intercetta +0.711 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.238
    stop_pct   +0.068
    long_x_banda -0.067
    vol_ratio  -0.034
    rsi        -0.033
    dist_ema   -0.025
    bb_pos     +0.021
    stoch_k    +0.019
    atr_pct    +0.018
    market_up  +0.017
    hour_cos   +0.012
    hour_sin   -0.008
    is_long    -0.007
    regime_incerto -0.003
    regime_bull +0.002
    adx        +0.001
    regime_bear -0.000
    long_x_mercato -0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 150015 righe, soglia 0.40, verdetto NON BATTE, stato ombra.
[selettore] fatto in 168.1s
```
