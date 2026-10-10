# 0576-10ott-mattina-selettore.req

_eseguito: 2026-10-10 03:55 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 142.6s

```
[selettore] 156798 trade da 1213 file (1219696 duplicati fusi, 2299475 gemelle fuse, 0 righe rotte saltate)
[selettore] 2603 coppie coin+strategia; famiglie: reversion 103103, momentum 51477, breakout 2072, altro 146
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 156786 trade usabili (12 scartati: variabili mancanti), 80375 di spec passate e 76411 di bocciate, dal 2023-02-27 al 2026-08-25
  finestra 1 [2025-11-20 -> 2026-02-19] train 62714 | soglia 0.45
     apri tutto: n 31357  pnl +138.0895  dd 1.8228  wr 66.7%  metro +136.2668
     selezione : n 31353  pnl +138.0014  dd 1.8228  wr 66.7%  metro +136.1787  -> non batte (margine -0.0881, p_perm 0.935, 95° perc. +136.3179)
     con size  : n 31353  pnl +131.7247  dd 1.5454  metro +130.1794  (informativo: il verdetto e' sulla selezione)
     solo passate : n 18074 | apri tutto pnl +96.7617 metro +95.9923 | selezione n 18072 pnl +96.7084 metro +95.9390
     solo bocciate: n 13283 | apri tutto pnl +41.3278 metro +40.1047 | selezione n 13281 pnl +41.2930 metro +40.0699
  finestra 2 [2026-02-19 -> 2026-05-21] train 94071 | soglia 0.45
     apri tutto: n 31358  pnl +133.0666  dd 1.2815  wr 66.3%  metro +131.7851
     selezione : n 31355  pnl +133.0861  dd 1.2815  wr 66.3%  metro +131.8046  -> non batte (margine +0.0194, p_perm 0.285, 95° perc. +131.8462)
     con size  : n 31355  pnl +127.9316  dd 1.1315  metro +126.8001  (informativo: il verdetto e' sulla selezione)
     solo passate : n 18128 | apri tutto pnl +91.9050 metro +90.9543 | selezione n 18126 pnl +91.9041 metro +90.9534
     solo bocciate: n 13230 | apri tutto pnl +41.1616 metro +40.3961 | selezione n 13229 pnl +41.1819 metro +40.4164
  finestra 3 [2026-05-21 -> 2026-08-25] train 125429 | soglia 0.45
     apri tutto: n 31357  pnl +160.9830  dd 0.6661  wr 67.7%  metro +160.3169
     selezione : n 31356  pnl +160.9996  dd 0.6661  wr 67.7%  metro +160.3334  -> non batte (margine +0.0166, p_perm 0.150, 95° perc. +160.3558)
     con size  : n 31356  pnl +152.8662  dd 0.6319  metro +152.2343  (informativo: il verdetto e' sulla selezione)
     solo passate : n 18629 | apri tutto pnl +111.2813 metro +110.6309 | selezione n 18628 pnl +111.2979 metro +110.6475
     solo bocciate: n 12728 | apri tutto pnl +49.7017 metro +49.1616 | selezione n 12728 pnl +49.7017 metro +49.1616
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 103091 trade usabili (12 scartati: variabili mancanti), 50989 di spec passate e 52102 di bocciate, dal 2023-02-27 al 2026-08-25
  finestra 1 [2025-11-22 -> 2026-02-20] train 41236 | soglia 0.40
     apri tutto: n 20618  pnl +90.8041  dd 2.5170  wr 66.7%  metro +88.2871
     selezione : n 20618  pnl +90.8041  dd 2.5170  wr 66.7%  metro +88.2871  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +88.2871)
     con size  : n 20618  pnl +96.1897  dd 2.5149  metro +93.6749  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11811 | apri tutto pnl +63.7140 metro +62.3968 | selezione n 11811 pnl +63.7140 metro +62.3968
     solo bocciate: n 8807 | apri tutto pnl +27.0901 metro +25.3437 | selezione n 8807 pnl +27.0901 metro +25.3437
  finestra 2 [2026-02-20 -> 2026-05-21] train 61854 | soglia 0.50
     apri tutto: n 20619  pnl +80.6789  dd 1.1822  wr 66.0%  metro +79.4967
     selezione : n 20592  pnl +80.7615  dd 1.1822  wr 66.1%  metro +79.5793  -> non batte (margine +0.0826, p_perm 0.055, 95° perc. +79.5829)
     con size  : n 20592  pnl +70.6722  dd 0.9678  metro +69.7044  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11983 | apri tutto pnl +55.7693 metro +54.8054 | selezione n 11970 pnl +55.8615 metro +54.8976
     solo bocciate: n 8636 | apri tutto pnl +24.9096 metro +24.1956 | selezione n 8622 pnl +24.9000 metro +24.2022
  finestra 3 [2026-05-21 -> 2026-08-25] train 82473 | soglia 0.50
     apri tutto: n 20618  pnl +108.3961  dd 0.8816  wr 68.5%  metro +107.5145
     selezione : n 20601  pnl +108.1970  dd 0.8816  wr 68.5%  metro +107.3154  -> non batte (margine -0.1991, p_perm 0.850, 95° perc. +107.5951)
     con size  : n 20601  pnl +91.8513  dd 0.7241  metro +91.1272  (informativo: il verdetto e' sulla selezione)
     solo passate : n 12371 | apri tutto pnl +74.2947 metro +73.7285 | selezione n 12360 pnl +74.1930 metro +73.6268
     solo bocciate: n 8247 | apri tutto pnl +34.1014 metro +33.5720 | selezione n 8241 pnl +34.0040 metro +33.4746
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 51477 trade usabili, 27677 di spec passate e 23800 di bocciate, dal 2023-03-01 al 2026-08-25
  finestra 1 [2025-11-11 -> 2026-02-14] train 20591 | soglia 0.50
     apri tutto: n 10295  pnl +44.1204  dd 0.9642  wr 66.4%  metro +43.1562
     selezione : n 10287  pnl +44.0109  dd 0.9642  wr 66.4%  metro +43.0467  -> non batte (margine -0.1096, p_perm 0.820, 95° perc. +43.2436)
     con size  : n 10287  pnl +37.6632  dd 0.7795  metro +36.8837  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6005 | apri tutto pnl +30.6603 metro +29.7485 | selezione n 6003 pnl +30.6445 metro +29.7327
     solo bocciate: n 4290 | apri tutto pnl +13.4601 metro +13.0068 | selezione n 4284 pnl +13.3664 metro +12.9130
  finestra 2 [2026-02-14 -> 2026-05-19] train 30886 | soglia 0.50
     apri tutto: n 10296  pnl +49.5369  dd 0.5740  wr 67.2%  metro +48.9629
     selezione : n 10276  pnl +49.7088  dd 0.5740  wr 67.3%  metro +49.1349  -> BATTE (margine +0.1719, p_perm 0.010, 95° perc. +49.0598)
     con size  : n 10276  pnl +42.0619  dd 0.4855  metro +41.5765  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5790 | apri tutto pnl +33.4675 metro +32.9897 | selezione n 5775 pnl +33.5200 metro +33.0421
     solo bocciate: n 4506 | apri tutto pnl +16.0694 metro +15.4906 | selezione n 4501 pnl +16.1888 metro +15.6101
  finestra 3 [2026-05-19 -> 2026-08-25] train 41182 | soglia 0.50
     apri tutto: n 10295  pnl +48.8703  dd 0.6708  wr 66.5%  metro +48.1995
     selezione : n 10285  pnl +48.7560  dd 0.6708  wr 66.5%  metro +48.0852  -> non batte (margine -0.1143, p_perm 0.770, 95° perc. +48.3170)
     con size  : n 10285  pnl +42.1470  dd 0.5434  metro +41.6036  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5914 | apri tutto pnl +33.8954 metro +33.3389 | selezione n 5904 pnl +33.7810 metro +33.2246
     solo bocciate: n 4381 | apri tutto pnl +14.9750 metro +14.4583 | selezione n 4381 pnl +14.9750 metro +14.4583
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 2072 trade usabili, 1563 di spec passate e 509 di bocciate, dal 2024-01-23 al 2026-08-25
  finestra 1 [2025-12-30 -> 2026-03-17] train   829 | soglia 0.55
     apri tutto: n  414  pnl +2.1218  dd 0.3285  wr 65.0%  metro +1.7933
     selezione : n  327  pnl +1.4507  dd 0.3988  wr 65.1%  metro +1.0519  -> non batte (margine -0.7414, p_perm 0.825, 95° perc. +1.8411)
     con size  : n  327  pnl +1.0900  dd 0.2491  metro +0.8408  (informativo: il verdetto e' sulla selezione)
     solo passate : n  301 | apri tutto pnl +1.9896 metro +1.6427 | selezione n  240 pnl +1.4562 metro +1.1404
     solo bocciate: n  113 | apri tutto pnl +0.1322 metro -0.0332 | selezione n   87 pnl -0.0055 metro -0.1974
  finestra 2 [2026-03-17 -> 2026-06-01] train  1243 | soglia 0.50
     apri tutto: n  415  pnl +2.8017  dd 0.3739  wr 63.4%  metro +2.4278
     selezione : n  398  pnl +2.4116  dd 0.4835  wr 63.1%  metro +1.9281  -> non batte (margine -0.4998, p_perm 0.980, 95° perc. +2.5882)
     con size  : n  398  pnl +1.7262  dd 0.3993  metro +1.3269  (informativo: il verdetto e' sulla selezione)
     solo passate : n  296 | apri tutto pnl +2.0613 metro +1.5670 | selezione n  280 pnl +1.6967 metro +1.1150
     solo bocciate: n  119 | apri tutto pnl +0.7405 metro +0.5828 | selezione n  118 pnl +0.7149 metro +0.5573
  finestra 3 [2026-06-01 -> 2026-08-25] train  1658 | soglia 0.50
     apri tutto: n  414  pnl +3.0843  dd 0.3052  wr 61.6%  metro +2.7792
     selezione : n  413  pnl +3.0442  dd 0.3052  wr 61.5%  metro +2.7391  -> non batte (margine -0.0401, p_perm 0.850, 95° perc. +2.8300)
     con size  : n  413  pnl +2.3247  dd 0.2503  metro +2.0744  (informativo: il verdetto e' sulla selezione)
     solo passate : n  293 | apri tutto pnl +2.4453 metro +2.2047 | selezione n  292 pnl +2.4052 metro +2.1645
     solo bocciate: n  121 | apri tutto pnl +0.6391 metro +0.3975 | selezione n  121 pnl +0.6391 metro +0.3975
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[altro] 146 trade usabili, dal 2025-09-03 al 2026-08-18
  finestra 1: train 58 trade < minimo -> campione insufficiente
  finestra 2: train 87 trade < minimo -> campione insufficiente
  finestra 3: train 117 trade < minimo -> campione insufficiente
  VERDETTO: CAMPIONE INSUFFICIENTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 156786, lam 1.0, intercetta +0.711 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.233
    stop_pct   +0.071
    long_x_banda -0.065
    vol_ratio  -0.036
    rsi        -0.025
    stoch_k    +0.018
    dist_ema   -0.015
    atr_pct    +0.014
    hour_sin   -0.013
    is_long    -0.013
    market_up  +0.013
    hour_cos   +0.009
    regime_bull -0.009
    bb_pos     +0.008
    long_x_mercato -0.005
    regime_bear -0.002
    adx        +0.002
    regime_incerto -0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 156798 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 140.7s
```
