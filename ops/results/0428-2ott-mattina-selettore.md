# 0428-2ott-mattina-selettore.req

_eseguito: 2026-10-02 06:10 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 62.1s

```
[selettore] 109280 trade da 576 file (418047 duplicati fusi, 496882 gemelle fuse, 0 righe rotte saltate)
[selettore] 1601 coppie coin+strategia; famiglie: reversion 73477, momentum 33971, breakout 1832
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 109280 trade usabili, 51657 di spec passate e 57623 di bocciate, dal 2023-02-27 al 2026-08-17
  finestra 1 [2025-11-10 -> 2026-02-11] train 43712 | soglia 0.50
     apri tutto: n 21856  pnl +93.7051  dd 1.6971  wr 66.6%  metro +92.0080
     selezione : n 21853  pnl +93.6815  dd 1.6971  wr 66.6%  metro +91.9844  -> non batte (margine -0.0236, p_perm 0.655, 95° perc. +92.0645)
     con size  : n 21853  pnl +79.3141  dd 1.3050  metro +78.0091  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11518 | apri tutto pnl +55.9251 metro +55.2499 | selezione n 11517 pnl +55.9362 metro +55.2611
     solo bocciate: n 10338 | apri tutto pnl +37.7800 metro +36.5029 | selezione n 10336 pnl +37.7452 metro +36.4681
  finestra 2 [2026-02-11 -> 2026-05-15] train 65568 | soglia 0.40
     apri tutto: n 21856  pnl +99.0489  dd 0.9116  wr 66.9%  metro +98.1373
     selezione : n 21856  pnl +99.0489  dd 0.9116  wr 66.9%  metro +98.1373  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +98.1373)
     con size  : n 21856  pnl +103.6807  dd 0.8592  metro +102.8215  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11643 | apri tutto pnl +62.9582 metro +62.3878 | selezione n 11643 pnl +62.9582 metro +62.3878
     solo bocciate: n 10213 | apri tutto pnl +36.0907 metro +35.3451 | selezione n 10213 pnl +36.0907 metro +35.3451
  finestra 3 [2026-05-15 -> 2026-08-17] train 87424 | soglia 0.50
     apri tutto: n 21856  pnl +106.6926  dd 0.8530  wr 67.3%  metro +105.8396
     selezione : n 21851  pnl +106.6799  dd 0.8530  wr 67.3%  metro +105.8269  -> non batte (margine -0.0127, p_perm 0.420, 95° perc. +105.9179)
     con size  : n 21851  pnl +91.0971  dd 0.7149  metro +90.3822  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11894 | apri tutto pnl +68.0713 metro +67.3716 | selezione n 11892 pnl +68.0681 metro +67.3684
     solo bocciate: n 9962 | apri tutto pnl +38.6213 metro +38.1142 | selezione n 9959 pnl +38.6118 metro +38.1047
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 73477 trade usabili, 34709 di spec passate e 38768 di bocciate, dal 2023-02-27 al 2026-08-17
  finestra 1 [2025-11-14 -> 2026-02-13] train 29391 | soglia 0.45
     apri tutto: n 14695  pnl +62.9689  dd 2.1413  wr 67.1%  metro +60.8276
     selezione : n 14695  pnl +62.9689  dd 2.1413  wr 67.1%  metro +60.8276  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +60.8276)
     con size  : n 14695  pnl +60.7610  dd 1.9049  metro +58.8561  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7978 | apri tutto pnl +38.2651 metro +37.6159 | selezione n 7978 pnl +38.2651 metro +37.6159
     solo bocciate: n 6717 | apri tutto pnl +24.7038 metro +23.0244 | selezione n 6717 pnl +24.7038 metro +23.0244
  finestra 2 [2026-02-13 -> 2026-05-15] train 44086 | soglia 0.50
     apri tutto: n 14696  pnl +59.6136  dd 1.0606  wr 66.8%  metro +58.5530
     selezione : n 14680  pnl +59.7321  dd 1.0606  wr 66.8%  metro +58.6715  -> BATTE (margine +0.1185, p_perm 0.050, 95° perc. +58.6714)
     con size  : n 14680  pnl +52.1139  dd 0.8936  metro +51.2203  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8191 | apri tutto pnl +39.9375 metro +39.3570 | selezione n 8184 pnl +39.9659 metro +39.3854
     solo bocciate: n 6505 | apri tutto pnl +19.6761 metro +18.9679 | selezione n 6496 pnl +19.7663 metro +19.0581
  finestra 3 [2026-05-15 -> 2026-08-17] train 58782 | soglia 0.50
     apri tutto: n 14695  pnl +70.7545  dd 0.7979  wr 68.4%  metro +69.9566
     selezione : n 14676  pnl +70.4815  dd 0.7979  wr 68.4%  metro +69.6836  -> non batte (margine -0.2730, p_perm 0.970, 95° perc. +70.0363)
     con size  : n 14676  pnl +60.6621  dd 0.6480  metro +60.0140  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8508 | apri tutto pnl +46.4403 metro +45.6723 | selezione n 8496 pnl +46.3039 metro +45.5359
     solo bocciate: n 6187 | apri tutto pnl +24.3143 metro +23.8029 | selezione n 6180 pnl +24.1776 metro +23.6662
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 33971 trade usabili, 15657 di spec passate e 18314 di bocciate, dal 2023-03-01 al 2026-08-17
  finestra 1 [2025-11-01 -> 2026-02-08] train 13588 | soglia 0.40
     apri tutto: n 6794  pnl +29.2621  dd 0.7579  wr 65.6%  metro +28.5042
     selezione : n 6794  pnl +29.2621  dd 0.7579  wr 65.6%  metro +28.5042  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +28.5042)
     con size  : n 6794  pnl +30.1352  dd 0.7805  metro +29.3546  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3338 | apri tutto pnl +16.7820 metro +16.1372 | selezione n 3338 pnl +16.7820 metro +16.1372
     solo bocciate: n 3456 | apri tutto pnl +12.4801 metro +11.9339 | selezione n 3456 pnl +12.4801 metro +11.9339
  finestra 2 [2026-02-08 -> 2026-05-13] train 20382 | soglia 0.50
     apri tutto: n 6795  pnl +36.7287  dd 0.5872  wr 67.0%  metro +36.1415
     selezione : n 6794  pnl +36.7415  dd 0.5872  wr 67.0%  metro +36.1543  -> non batte (margine +0.0128, p_perm 0.335, 95° perc. +36.1869)
     con size  : n 6794  pnl +30.0906  dd 0.5162  metro +29.5744  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3204 | apri tutto pnl +21.1767 metro +20.7013 | selezione n 3203 pnl +21.1895 metro +20.7141
     solo bocciate: n 3591 | apri tutto pnl +15.5520 metro +14.9230 | selezione n 3591 pnl +15.5520 metro +14.9230
  finestra 3 [2026-05-13 -> 2026-08-17] train 27177 | soglia 0.50
     apri tutto: n 6794  pnl +34.9044  dd 0.4556  wr 65.4%  metro +34.4488
     selezione : n 6793  pnl +34.8759  dd 0.4556  wr 65.4%  metro +34.4202  -> non batte (margine -0.0285, p_perm 0.865, 95° perc. +34.4969)
     con size  : n 6793  pnl +29.5096  dd 0.3797  metro +29.1300  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3173 | apri tutto pnl +20.5635 metro +20.0213 | selezione n 3172 pnl +20.5350 metro +19.9928
     solo bocciate: n 3621 | apri tutto pnl +14.3409 metro +13.6804 | selezione n 3621 pnl +14.3409 metro +13.6804
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1832 trade usabili, 1291 di spec passate e 541 di bocciate, dal 2024-01-23 al 2026-08-16
  finestra 1 [2025-11-17 -> 2026-02-10] train   733 | soglia 0.45
     apri tutto: n  366  pnl +0.7583  dd 0.2323  wr 62.6%  metro +0.5260
     selezione : n  347  pnl +0.7456  dd 0.2553  wr 63.1%  metro +0.4903  -> non batte (margine -0.0358, p_perm 0.415, 95° perc. +0.6573)
     con size  : n  347  pnl +0.7949  dd 0.2076  metro +0.5873  (informativo: il verdetto e' sulla selezione)
     solo passate : n  215 | apri tutto pnl +0.2580 metro -0.0775 | selezione n  208 pnl +0.2741 metro -0.1041
     solo bocciate: n  151 | apri tutto pnl +0.5003 metro +0.3619 | selezione n  139 pnl +0.4715 metro +0.3216
  finestra 2 [2026-02-10 -> 2026-05-13] train  1099 | soglia 0.40
     apri tutto: n  367  pnl +1.5968  dd 0.2799  wr 64.8%  metro +1.3169
     selezione : n  357  pnl +1.3500  dd 0.2934  wr 64.4%  metro +1.0566  -> non batte (margine -0.2603, p_perm 0.965, 95° perc. +1.4368)
     con size  : n  357  pnl +1.2053  dd 0.2405  metro +0.9648  (informativo: il verdetto e' sulla selezione)
     solo passate : n  221 | apri tutto pnl +1.1015 metro +0.8313 | selezione n  211 pnl +0.8547 metro +0.5273
     solo bocciate: n  146 | apri tutto pnl +0.4954 metro +0.3222 | selezione n  146 pnl +0.4954 metro +0.3222
  finestra 3 [2026-05-13 -> 2026-08-16] train  1466 | soglia 0.45
     apri tutto: n  366  pnl +2.2438  dd 0.2210  wr 64.2%  metro +2.0228
     selezione : n  352  pnl +1.9115  dd 0.3460  wr 63.9%  metro +1.5655  -> non batte (margine -0.4573, p_perm 0.990, 95° perc. +2.1083)
     con size  : n  352  pnl +1.6463  dd 0.2547  metro +1.3916  (informativo: il verdetto e' sulla selezione)
     solo passate : n  207 | apri tutto pnl +1.6552 metro +1.5167 | selezione n  196 pnl +1.3926 metro +1.2273
     solo bocciate: n  159 | apri tutto pnl +0.5886 metro +0.2935 | selezione n  156 pnl +0.5189 metro +0.2238
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 109280, lam 1.0, intercetta +0.707 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.218
    long_x_banda -0.057
    stop_pct   +0.057
    vol_ratio  -0.032
    dist_ema   -0.031
    bb_pos     +0.027
    atr_pct    +0.026
    is_long    -0.021
    hour_sin   -0.019
    regime_bull -0.011
    stoch_k    -0.009
    hour_cos   +0.008
    market_up  +0.005
    regime_incerto -0.005
    rsi        -0.004
    long_x_mercato -0.002
    regime_bear +0.002
    adx        -0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 109280 righe, soglia 0.50, verdetto NON BATTE, stato ombra.
[selettore] fatto in 60.4s
```
