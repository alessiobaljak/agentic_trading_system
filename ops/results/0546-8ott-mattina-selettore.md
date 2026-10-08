# 0546-8ott-mattina-selettore.req

_eseguito: 2026-10-08 03:55 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 121.8s

```
[selettore] 147490 trade da 1107 file (1041570 duplicati fusi, 1760638 gemelle fuse, 0 righe rotte saltate)
[selettore] 2397 coppie coin+strategia; famiglie: reversion 97147, momentum 48087, breakout 2256
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 147478 trade usabili (12 scartati: variabili mancanti), 74742 di spec passate e 72736 di bocciate, dal 2023-02-27 al 2026-08-23
  finestra 1 [2025-11-18 -> 2026-02-17] train 58991 | soglia 0.45
     apri tutto: n 29496  pnl +130.2070  dd 1.8300  wr 66.6%  metro +128.3771
     selezione : n 29494  pnl +130.1616  dd 1.8300  wr 66.6%  metro +128.3316  -> non batte (margine -0.0455, p_perm 0.875, 95° perc. +128.4289)
     con size  : n 29494  pnl +124.9840  dd 1.5627  metro +123.4213  (informativo: il verdetto e' sulla selezione)
     solo passate : n 16706 | apri tutto pnl +89.3641 metro +88.5740 | selezione n 16706 pnl +89.3641 metro +88.5740
     solo bocciate: n 12790 | apri tutto pnl +40.8429 metro +39.6335 | selezione n 12788 pnl +40.7975 metro +39.5880
  finestra 2 [2026-02-17 -> 2026-05-19] train 88487 | soglia 0.45
     apri tutto: n 29495  pnl +123.4877  dd 1.2782  wr 66.3%  metro +122.2095
     selezione : n 29494  pnl +123.5134  dd 1.2782  wr 66.3%  metro +122.2351  -> non batte (margine +0.0257, p_perm 0.110, 95° perc. +122.2436)
     con size  : n 29494  pnl +118.5713  dd 1.1693  metro +117.4021  (informativo: il verdetto e' sulla selezione)
     solo passate : n 16731 | apri tutto pnl +83.9952 metro +82.9180 | selezione n 16730 pnl +84.0209 metro +82.9437
     solo bocciate: n 12764 | apri tutto pnl +39.4925 metro +38.6939 | selezione n 12764 pnl +39.4925 metro +38.6939
  finestra 3 [2026-05-19 -> 2026-08-23] train 117982 | soglia 0.45
     apri tutto: n 29496  pnl +147.1493  dd 0.7860  wr 67.6%  metro +146.3633
     selezione : n 29496  pnl +147.1493  dd 0.7860  wr 67.6%  metro +146.3633  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +146.3633)
     con size  : n 29496  pnl +140.0232  dd 0.6899  metro +139.3332  (informativo: il verdetto e' sulla selezione)
     solo passate : n 17238 | apri tutto pnl +99.1532 metro +98.5874 | selezione n 17238 pnl +99.1532 metro +98.5874
     solo bocciate: n 12258 | apri tutto pnl +47.9960 metro +47.4708 | selezione n 12258 pnl +47.9960 metro +47.4708
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 97135 trade usabili (12 scartati: variabili mancanti), 48120 di spec passate e 49015 di bocciate, dal 2023-02-27 al 2026-08-23
  finestra 1 [2025-11-22 -> 2026-02-19] train 38854 | soglia 0.45
     apri tutto: n 19427  pnl +81.1784  dd 2.4725  wr 66.4%  metro +78.7059
     selezione : n 19424  pnl +81.2446  dd 2.4725  wr 66.4%  metro +78.7720  -> BATTE (margine +0.0661, p_perm 0.040, 95° perc. +78.7610)
     con size  : n 19424  pnl +78.8002  dd 2.1509  metro +76.6493  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11072 | apri tutto pnl +56.3071 metro +55.1248 | selezione n 11069 pnl +56.3732 metro +55.1909
     solo bocciate: n 8355 | apri tutto pnl +24.8713 metro +23.0515 | selezione n 8355 pnl +24.8713 metro +23.0515
  finestra 2 [2026-02-19 -> 2026-05-20] train 58281 | soglia 0.50
     apri tutto: n 19427  pnl +75.5277  dd 1.2429  wr 66.3%  metro +74.2848
     selezione : n 19406  pnl +75.5959  dd 1.2429  wr 66.3%  metro +74.3530  -> non batte (margine +0.0681, p_perm 0.080, 95° perc. +74.3870)
     con size  : n 19406  pnl +66.1399  dd 0.9926  metro +65.1473  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11175 | apri tutto pnl +52.4166 metro +51.4703 | selezione n 11166 pnl +52.5099 metro +51.5636
     solo bocciate: n 8252 | apri tutto pnl +23.1111 metro +22.3755 | selezione n 8240 pnl +23.0860 metro +22.3504
  finestra 3 [2026-05-20 -> 2026-08-23] train 77708 | soglia 0.50
     apri tutto: n 19427  pnl +98.1629  dd 1.0493  wr 68.3%  metro +97.1135
     selezione : n 19414  pnl +97.9813  dd 1.0493  wr 68.3%  metro +96.9320  -> non batte (margine -0.1816, p_perm 0.920, 95° perc. +97.1881)
     con size  : n 19414  pnl +83.1109  dd 0.8465  metro +82.2644  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11595 | apri tutto pnl +65.8068 metro +65.2503 | selezione n 11587 pnl +65.6739 metro +65.1173
     solo bocciate: n 7832 | apri tutto pnl +32.3560 metro +31.8300 | selezione n 7827 pnl +32.3075 metro +31.7814
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 48087 trade usabili, 24986 di spec passate e 23101 di bocciate, dal 2023-03-01 al 2026-08-23
  finestra 1 [2025-11-07 -> 2026-02-11] train 19235 | soglia 0.40
     apri tutto: n 9617  pnl +43.0941  dd 0.8442  wr 66.2%  metro +42.2498
     selezione : n 9617  pnl +43.0941  dd 0.8442  wr 66.2%  metro +42.2498  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +42.2498)
     con size  : n 9617  pnl +45.5251  dd 0.9367  metro +44.5885  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5383 | apri tutto pnl +28.8444 metro +28.0466 | selezione n 5383 pnl +28.8444 metro +28.0466
     solo bocciate: n 4234 | apri tutto pnl +14.2496 metro +13.7460 | selezione n 4234 pnl +14.2496 metro +13.7460
  finestra 2 [2026-02-11 -> 2026-05-17] train 28852 | soglia 0.40
     apri tutto: n 9618  pnl +48.0404  dd 0.6829  wr 67.2%  metro +47.3575
     selezione : n 9618  pnl +48.0404  dd 0.6829  wr 67.2%  metro +47.3575  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +47.3575)
     con size  : n 9618  pnl +49.8851  dd 0.7474  metro +49.1377  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5231 | apri tutto pnl +30.2583 metro +29.6378 | selezione n 5231 pnl +30.2583 metro +29.6378
     solo bocciate: n 4387 | apri tutto pnl +17.7822 metro +17.1865 | selezione n 4387 pnl +17.7822 metro +17.1865
  finestra 3 [2026-05-17 -> 2026-08-23] train 38470 | soglia 0.50
     apri tutto: n 9617  pnl +45.0438  dd 0.6664  wr 66.2%  metro +44.3775
     selezione : n 9608  pnl +44.9589  dd 0.6664  wr 66.2%  metro +44.2926  -> non batte (margine -0.0849, p_perm 0.675, 95° perc. +44.4754)
     con size  : n 9608  pnl +39.4141  dd 0.4994  metro +38.9147  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5325 | apri tutto pnl +30.5413 metro +29.9720 | selezione n 5317 pnl +30.4388 metro +29.8695
     solo bocciate: n 4292 | apri tutto pnl +14.5025 metro +13.8701 | selezione n 4291 pnl +14.5201 metro +13.8877
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 2256 trade usabili, 1636 di spec passate e 620 di bocciate, dal 2024-01-23 al 2026-08-23
  finestra 1 [2025-12-27 -> 2026-03-09] train   902 | soglia 0.55
     apri tutto: n  451  pnl +1.7628  dd 0.2735  wr 64.1%  metro +1.4893
     selezione : n  383  pnl +1.1557  dd 0.3032  wr 65.0%  metro +0.8524  -> non batte (margine -0.6369, p_perm 0.935, 95° perc. +1.6822)
     con size  : n  383  pnl +0.9982  dd 0.1948  metro +0.8034  (informativo: il verdetto e' sulla selezione)
     solo passate : n  313 | apri tutto pnl +1.8271 metro +1.5633 | selezione n  262 pnl +1.1844 metro +0.8685
     solo bocciate: n  138 | apri tutto pnl -0.0643 metro -0.2594 | selezione n  121 pnl -0.0287 metro -0.2151
  finestra 2 [2026-03-09 -> 2026-05-26] train  1353 | soglia 0.50
     apri tutto: n  452  pnl +3.4169  dd 0.2089  wr 66.1%  metro +3.2081
     selezione : n  414  pnl +2.9024  dd 0.2243  wr 66.4%  metro +2.6780  -> non batte (margine -0.5300, p_perm 0.830, 95° perc. +3.2921)
     con size  : n  414  pnl +2.2859  dd 0.1883  metro +2.0975  (informativo: il verdetto e' sulla selezione)
     solo passate : n  310 | apri tutto pnl +2.7061 metro +2.4150 | selezione n  277 pnl +2.2104 metro +1.9169
     solo bocciate: n  142 | apri tutto pnl +0.7109 metro +0.5043 | selezione n  137 pnl +0.6920 metro +0.5088
  finestra 3 [2026-05-27 -> 2026-08-23] train  1805 | soglia 0.50
     apri tutto: n  451  pnl +3.4726  dd 0.5554  wr 62.7%  metro +2.9172
     selezione : n  428  pnl +2.9628  dd 0.6665  wr 62.2%  metro +2.2962  -> non batte (margine -0.6209, p_perm 0.995, 95° perc. +3.0711)
     con size  : n  428  pnl +2.3908  dd 0.5055  metro +1.8853  (informativo: il verdetto e' sulla selezione)
     solo passate : n  298 | apri tutto pnl +2.7590 metro +2.4015 | selezione n  281 pnl +2.3198 metro +1.8512
     solo bocciate: n  153 | apri tutto pnl +0.7136 metro +0.4511 | selezione n  147 pnl +0.6430 metro +0.3805
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 147478, lam 1.0, intercetta +0.706 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.232
    stop_pct   +0.077
    long_x_banda -0.061
    vol_ratio  -0.033
    bb_pos     +0.025
    rsi        -0.025
    is_long    -0.018
    hour_sin   -0.016
    dist_ema   -0.015
    hour_cos   +0.014
    market_up  +0.009
    regime_bull -0.006
    atr_pct    +0.006
    adx        -0.003
    regime_incerto +0.003
    regime_bear +0.002
    stoch_k    +0.001
    long_x_mercato -0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 147490 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 120.2s
```
