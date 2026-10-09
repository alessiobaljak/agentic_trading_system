# 0561-9ott-mattina-selettore.req

_eseguito: 2026-10-09 03:56 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 128.1s

```
[selettore] 153557 trade da 1180 file (1140071 duplicati fusi, 2043057 gemelle fuse, 0 righe rotte saltate)
[selettore] 2549 coppie coin+strategia; famiglie: reversion 101329, momentum 50251, breakout 1977
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 153545 trade usabili (12 scartati: variabili mancanti), 77956 di spec passate e 75589 di bocciate, dal 2023-02-27 al 2026-08-24
  finestra 1 [2025-11-18 -> 2026-02-18] train 61418 | soglia 0.45
     apri tutto: n 30709  pnl +135.3311  dd 1.9969  wr 66.7%  metro +133.3342
     selezione : n 30707  pnl +135.2856  dd 1.9969  wr 66.7%  metro +133.2887  -> non batte (margine -0.0455, p_perm 0.885, 95° perc. +133.3822)
     con size  : n 30707  pnl +129.7922  dd 1.6921  metro +128.1001  (informativo: il verdetto e' sulla selezione)
     solo passate : n 17396 | apri tutto pnl +92.9144 metro +92.0859 | selezione n 17396 pnl +92.9144 metro +92.0859
     solo bocciate: n 13313 | apri tutto pnl +42.4167 metro +41.0990 | selezione n 13311 pnl +42.3712 metro +41.0535
  finestra 2 [2026-02-18 -> 2026-05-20] train 92127 | soglia 0.45
     apri tutto: n 30709  pnl +126.1891  dd 1.3056  wr 66.3%  metro +124.8835
     selezione : n 30707  pnl +126.1882  dd 1.3056  wr 66.3%  metro +124.8826  -> non batte (margine -0.0009, p_perm 0.455, 95° perc. +124.9269)
     con size  : n 30707  pnl +121.5233  dd 1.1089  metro +120.4144  (informativo: il verdetto e' sulla selezione)
     solo passate : n 17493 | apri tutto pnl +85.6029 metro +84.7014 | selezione n 17491 pnl +85.6020 metro +84.7005
     solo bocciate: n 13216 | apri tutto pnl +40.5862 metro +39.7898 | selezione n 13216 pnl +40.5862 metro +39.7898
  finestra 3 [2026-05-20 -> 2026-08-24] train 122836 | soglia 0.45
     apri tutto: n 30709  pnl +154.9564  dd 0.7509  wr 67.6%  metro +154.2056
     selezione : n 30709  pnl +154.9564  dd 0.7509  wr 67.6%  metro +154.2056  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +154.2056)
     con size  : n 30709  pnl +147.0773  dd 0.6969  metro +146.3805  (informativo: il verdetto e' sulla selezione)
     solo passate : n 17945 | apri tutto pnl +105.3389 metro +104.6851 | selezione n 17945 pnl +105.3389 metro +104.6851
     solo bocciate: n 12764 | apri tutto pnl +49.6176 metro +49.0462 | selezione n 12764 pnl +49.6176 metro +49.0462
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 101317 trade usabili (12 scartati: variabili mancanti), 49887 di spec passate e 51430 di bocciate, dal 2023-02-27 al 2026-08-24
  finestra 1 [2025-11-20 -> 2026-02-19] train 40527 | soglia 0.45
     apri tutto: n 20263  pnl +88.1287  dd 2.6522  wr 66.6%  metro +85.4765
     selezione : n 20262  pnl +88.1526  dd 2.6522  wr 66.6%  metro +85.5004  -> non batte (margine +0.0239, p_perm 0.140, 95° perc. +85.5156)
     con size  : n 20262  pnl +85.2702  dd 2.3347  metro +82.9355  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11430 | apri tutto pnl +60.4809 metro +59.1755 | selezione n 11429 pnl +60.5048 metro +59.1994
     solo bocciate: n 8833 | apri tutto pnl +27.6478 metro +25.7754 | selezione n 8833 pnl +27.6478 metro +25.7754
  finestra 2 [2026-02-19 -> 2026-05-20] train 60790 | soglia 0.50
     apri tutto: n 20264  pnl +77.5259  dd 1.2078  wr 66.0%  metro +76.3181
     selezione : n 20254  pnl +77.4749  dd 1.2078  wr 66.0%  metro +76.2671  -> non batte (margine -0.0510, p_perm 0.625, 95° perc. +76.4051)
     con size  : n 20254  pnl +68.0385  dd 0.9970  metro +67.0414  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11625 | apri tutto pnl +53.7917 metro +52.7653 | selezione n 11618 pnl +53.7507 metro +52.7243
     solo bocciate: n 8639 | apri tutto pnl +23.7342 metro +22.9853 | selezione n 8636 pnl +23.7242 metro +22.9915
  finestra 3 [2026-05-20 -> 2026-08-24] train 81054 | soglia 0.50
     apri tutto: n 20263  pnl +102.6272  dd 0.8566  wr 68.2%  metro +101.7706
     selezione : n 20245  pnl +102.4540  dd 0.8566  wr 68.2%  metro +101.5974  -> non batte (margine -0.1732, p_perm 0.820, 95° perc. +101.8206)
     con size  : n 20245  pnl +86.7187  dd 0.6948  metro +86.0239  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11974 | apri tutto pnl +68.4055 metro +67.7741 | selezione n 11963 pnl +68.3181 metro +67.6867
     solo bocciate: n 8289 | apri tutto pnl +34.2217 metro +33.7384 | selezione n 8282 pnl +34.1359 metro +33.6526
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 50251 trade usabili, 26602 di spec passate e 23649 di bocciate, dal 2023-03-01 al 2026-08-24
  finestra 1 [2025-11-12 -> 2026-02-14] train 20100 | soglia 0.40
     apri tutto: n 10050  pnl +43.8405  dd 0.8756  wr 66.7%  metro +42.9648
     selezione : n 10050  pnl +43.8405  dd 0.8756  wr 66.7%  metro +42.9648  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +42.9648)
     con size  : n 10050  pnl +46.2176  dd 0.8695  metro +45.3480  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5767 | apri tutto pnl +30.0443 metro +29.3147 | selezione n 5767 pnl +30.0443 metro +29.3147
     solo bocciate: n 4283 | apri tutto pnl +13.7961 metro +13.3730 | selezione n 4283 pnl +13.7961 metro +13.3730
  finestra 2 [2026-02-14 -> 2026-05-19] train 30150 | soglia 0.40
     apri tutto: n 10051  pnl +46.4464  dd 0.6080  wr 67.2%  metro +45.8383
     selezione : n 10051  pnl +46.4464  dd 0.6080  wr 67.2%  metro +45.8383  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +45.8383)
     con size  : n 10051  pnl +48.7737  dd 0.6744  metro +48.0993  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5548 | apri tutto pnl +30.0503 metro +29.4605 | selezione n 5548 pnl +30.0503 metro +29.4605
     solo bocciate: n 4503 | apri tutto pnl +16.3961 metro +15.7953 | selezione n 4503 pnl +16.3961 metro +15.7953
  finestra 3 [2026-05-19 -> 2026-08-24] train 40201 | soglia 0.50
     apri tutto: n 10050  pnl +49.1817  dd 0.6228  wr 66.7%  metro +48.5589
     selezione : n 10041  pnl +49.0685  dd 0.6228  wr 66.7%  metro +48.4457  -> non batte (margine -0.1132, p_perm 0.785, 95° perc. +48.6541)
     con size  : n 10041  pnl +42.4894  dd 0.5071  metro +41.9823  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5700 | apri tutto pnl +34.4183 metro +33.9613 | selezione n 5691 pnl +34.3051 metro +33.8481
     solo bocciate: n 4350 | apri tutto pnl +14.7634 metro +14.0884 | selezione n 4350 pnl +14.7634 metro +14.0884
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1977 trade usabili, 1467 di spec passate e 510 di bocciate, dal 2024-01-23 al 2026-08-24
  finestra 1 [2025-12-21 -> 2026-03-07] train   791 | soglia 0.55
     apri tutto: n  395  pnl +2.2152  dd 0.1997  wr 66.1%  metro +2.0155
     selezione : n  324  pnl +1.5386  dd 0.2382  wr 67.3%  metro +1.3004  -> non batte (margine -0.7151, p_perm 0.900, 95° perc. +1.9448)
     con size  : n  324  pnl +1.2674  dd 0.1599  metro +1.1075  (informativo: il verdetto e' sulla selezione)
     solo passate : n  270 | apri tutto pnl +2.0365 metro +1.8551 | selezione n  222 pnl +1.3585 metro +1.1568
     solo bocciate: n  125 | apri tutto pnl +0.1787 metro +0.0133 | selezione n  102 pnl +0.1800 metro +0.0524
  finestra 2 [2026-03-07 -> 2026-05-26] train  1186 | soglia 0.45
     apri tutto: n  396  pnl +3.0322  dd 0.2915  wr 66.7%  metro +2.7407
     selezione : n  386  pnl +2.6272  dd 0.3070  wr 66.1%  metro +2.3202  -> non batte (margine -0.4205, p_perm 1.000, 95° perc. +2.8521)
     con size  : n  386  pnl +2.4440  dd 0.3028  metro +2.1412  (informativo: il verdetto e' sulla selezione)
     solo passate : n  277 | apri tutto pnl +2.3310 metro +2.0473 | selezione n  269 pnl +1.9730 metro +1.6893
     solo bocciate: n  119 | apri tutto pnl +0.7012 metro +0.5435 | selezione n  117 pnl +0.6542 metro +0.4751
  finestra 3 [2026-05-26 -> 2026-08-24] train  1582 | soglia 0.40
     apri tutto: n  395  pnl +3.0718  dd 0.5043  wr 63.0%  metro +2.5675
     selezione : n  395  pnl +3.0718  dd 0.5043  wr 63.0%  metro +2.5675  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +2.5675)
     con size  : n  395  pnl +2.9568  dd 0.5171  metro +2.4396  (informativo: il verdetto e' sulla selezione)
     solo passate : n  262 | apri tutto pnl +2.3330 metro +1.9757 | selezione n  262 pnl +2.3330 metro +1.9757
     solo bocciate: n  133 | apri tutto pnl +0.7388 metro +0.4972 | selezione n  133 pnl +0.7388 metro +0.4972
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 153545, lam 1.0, intercetta +0.708 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.228
    stop_pct   +0.077
    long_x_banda -0.060
    vol_ratio  -0.033
    rsi        -0.029
    is_long    -0.019
    bb_pos     +0.019
    dist_ema   -0.019
    hour_sin   -0.014
    market_up  +0.012
    stoch_k    +0.010
    atr_pct    +0.010
    hour_cos   +0.010
    regime_bull -0.007
    adx        -0.004
    regime_bear -0.001
    long_x_mercato -0.000
    regime_incerto -0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 153557 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 126.5s
```
