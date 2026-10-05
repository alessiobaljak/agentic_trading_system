# 0497-5ott-mattina-selettore.req

_eseguito: 2026-10-05 06:12 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 89.0s

```
[selettore] 132464 trade da 831 file (702455 duplicati fusi, 1004270 gemelle fuse, 0 righe rotte saltate)
[selettore] 2052 coppie coin+strategia; famiglie: reversion 88184, momentum 41600, breakout 2680
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 132464 trade usabili, 64636 di spec passate e 67828 di bocciate, dal 2023-02-27 al 2026-08-20
  finestra 1 [2025-11-14 -> 2026-02-14] train 52986 | soglia 0.40
     apri tutto: n 26493  pnl +113.9437  dd 1.7582  wr 66.4%  metro +112.1855
     selezione : n 26492  pnl +113.9248  dd 1.7582  wr 66.4%  metro +112.1666  -> non batte (margine -0.0189, p_perm 0.795, 95° perc. +112.2226)
     con size  : n 26492  pnl +120.1587  dd 1.6508  metro +118.5079  (informativo: il verdetto e' sulla selezione)
     solo passate : n 14499 | apri tutto pnl +72.8919 metro +72.2393 | selezione n 14499 pnl +72.8919 metro +72.2393
     solo bocciate: n 11994 | apri tutto pnl +41.0518 metro +39.7974 | selezione n 11993 pnl +41.0329 metro +39.7785
  finestra 2 [2026-02-14 -> 2026-05-17] train 79479 | soglia 0.40
     apri tutto: n 26492  pnl +111.3808  dd 1.4204  wr 66.3%  metro +109.9604
     selezione : n 26492  pnl +111.3808  dd 1.4204  wr 66.3%  metro +109.9604  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +109.9604)
     con size  : n 26492  pnl +117.4411  dd 1.3638  metro +116.0773  (informativo: il verdetto e' sulla selezione)
     solo passate : n 14553 | apri tutto pnl +72.7311 metro +72.0676 | selezione n 14553 pnl +72.7311 metro +72.0676
     solo bocciate: n 11939 | apri tutto pnl +38.6497 metro +37.8225 | selezione n 11939 pnl +38.6497 metro +37.8225
  finestra 3 [2026-05-17 -> 2026-08-20] train 105971 | soglia 0.45
     apri tutto: n 26493  pnl +128.0275  dd 0.7670  wr 67.4%  metro +127.2606
     selezione : n 26493  pnl +128.0275  dd 0.7670  wr 67.4%  metro +127.2606  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +127.2606)
     con size  : n 26493  pnl +121.7760  dd 0.6483  metro +121.1277  (informativo: il verdetto e' sulla selezione)
     solo passate : n 14944 | apri tutto pnl +83.2315 metro +82.5132 | selezione n 14944 pnl +83.2315 metro +82.5132
     solo bocciate: n 11549 | apri tutto pnl +44.7961 metro +44.1235 | selezione n 11549 pnl +44.7961 metro +44.1235
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 88184 trade usabili, 42309 di spec passate e 45875 di bocciate, dal 2023-02-27 al 2026-08-20
  finestra 1 [2025-11-19 -> 2026-02-16] train 35274 | soglia 0.45
     apri tutto: n 17637  pnl +73.6480  dd 2.5073  wr 66.4%  metro +71.1407
     selezione : n 17637  pnl +73.6480  dd 2.5073  wr 66.4%  metro +71.1407  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +71.1407)
     con size  : n 17637  pnl +71.6321  dd 2.1979  metro +69.4342  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9719 | apri tutto pnl +48.0133 metro +46.9288 | selezione n 9719 pnl +48.0133 metro +46.9288
     solo bocciate: n 7918 | apri tutto pnl +25.6347 metro +23.8489 | selezione n 7918 pnl +25.6347 metro +23.8489
  finestra 2 [2026-02-16 -> 2026-05-17] train 52911 | soglia 0.50
     apri tutto: n 17636  pnl +67.2819  dd 1.1981  wr 66.2%  metro +66.0838
     selezione : n 17619  pnl +67.3854  dd 1.1981  wr 66.2%  metro +66.1873  -> BATTE (margine +0.1036, p_perm 0.025, 95° perc. +66.1651)
     con size  : n 17619  pnl +58.8555  dd 0.9440  metro +57.9115  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9903 | apri tutto pnl +45.5012 metro +44.8303 | selezione n 9895 pnl +45.5398 metro +44.8688
     solo bocciate: n 7733 | apri tutto pnl +21.7806 metro +21.0073 | selezione n 7724 pnl +21.8457 metro +21.0724
  finestra 3 [2026-05-17 -> 2026-08-20] train 70547 | soglia 0.50
     apri tutto: n 17637  pnl +85.8007  dd 0.8523  wr 68.3%  metro +84.9484
     selezione : n 17628  pnl +85.7286  dd 0.8523  wr 68.3%  metro +84.8763  -> non batte (margine -0.0721, p_perm 0.675, 95° perc. +85.0092)
     con size  : n 17628  pnl +73.1195  dd 0.6966  metro +72.4229  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10182 | apri tutto pnl +55.4954 metro +54.7944 | selezione n 10177 pnl +55.5029 metro +54.8019
     solo bocciate: n 7455 | apri tutto pnl +30.3053 metro +29.8531 | selezione n 7451 pnl +30.2257 metro +29.7735
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 41600 trade usabili, 20185 di spec passate e 21415 di bocciate, dal 2023-03-01 al 2026-08-20
  finestra 1 [2025-11-03 -> 2026-02-08] train 16640 | soglia 0.40
     apri tutto: n 8320  pnl +38.2358  dd 0.8921  wr 66.2%  metro +37.3437
     selezione : n 8320  pnl +38.2358  dd 0.8921  wr 66.2%  metro +37.3437  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +37.3437)
     con size  : n 8320  pnl +40.0187  dd 1.0043  metro +39.0144  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4349 | apri tutto pnl +23.5480 metro +22.6942 | selezione n 4349 pnl +23.5480 metro +22.6942
     solo bocciate: n 3971 | apri tutto pnl +14.6877 metro +14.1871 | selezione n 3971 pnl +14.6877 metro +14.1871
  finestra 2 [2026-02-08 -> 2026-05-14] train 24960 | soglia 0.40
     apri tutto: n 8320  pnl +41.8439  dd 0.6110  wr 67.0%  metro +41.2329
     selezione : n 8320  pnl +41.8439  dd 0.6110  wr 67.0%  metro +41.2329  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +41.2329)
     con size  : n 8320  pnl +43.3550  dd 0.6786  metro +42.6764  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4249 | apri tutto pnl +24.7317 metro +24.0955 | selezione n 4249 pnl +24.7317 metro +24.0955
     solo bocciate: n 4071 | apri tutto pnl +17.1122 metro +16.5398 | selezione n 4071 pnl +17.1122 metro +16.5398
  finestra 3 [2026-05-14 -> 2026-08-20] train 33280 | soglia 0.40
     apri tutto: n 8320  pnl +37.8219  dd 0.7105  wr 65.6%  metro +37.1114
     selezione : n 8320  pnl +37.8219  dd 0.7105  wr 65.6%  metro +37.1114  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +37.1114)
     con size  : n 8320  pnl +40.1097  dd 0.6707  metro +39.4391  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4295 | apri tutto pnl +23.6756 metro +23.0476 | selezione n 4295 pnl +23.6756 metro +23.0476
     solo bocciate: n 4025 | apri tutto pnl +14.1463 metro +13.3396 | selezione n 4025 pnl +14.1463 metro +13.3396
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 2680 trade usabili, 2142 di spec passate e 538 di bocciate, dal 2024-01-23 al 2026-08-20
  finestra 1 [2025-12-24 -> 2026-03-11] train  1072 | soglia 0.40
     apri tutto: n  536  pnl +2.7975  dd 0.2307  wr 66.0%  metro +2.5668
     selezione : n  535  pnl +2.7723  dd 0.2307  wr 66.0%  metro +2.5416  -> non batte (margine -0.0252, p_perm 0.745, 95° perc. +2.6071)
     con size  : n  535  pnl +2.8552  dd 0.2444  metro +2.6108  (informativo: il verdetto e' sulla selezione)
     solo passate : n  403 | apri tutto pnl +2.6789 metro +2.4839 | selezione n  402 pnl +2.6537 metro +2.4587
     solo bocciate: n  133 | apri tutto pnl +0.1186 metro -0.0683 | selezione n  133 pnl +0.1186 metro -0.0683
  finestra 2 [2026-03-11 -> 2026-05-29] train  1608 | soglia 0.45
     apri tutto: n  536  pnl +3.9480  dd 0.3956  wr 68.3%  metro +3.5523
     selezione : n  524  pnl +3.6487  dd 0.3439  wr 68.3%  metro +3.3047  -> non batte (margine -0.2476, p_perm 0.895, 95° perc. +3.6889)
     con size  : n  524  pnl +3.1559  dd 0.3040  metro +2.8519  (informativo: il verdetto e' sulla selezione)
     solo passate : n  404 | apri tutto pnl +3.1612 metro +2.7498 | selezione n  393 pnl +2.8795 metro +2.5237
     solo bocciate: n  132 | apri tutto pnl +0.7867 metro +0.6136 | selezione n  131 pnl +0.7692 metro +0.5961
  finestra 3 [2026-05-29 -> 2026-08-20] train  2144 | soglia 0.40
     apri tutto: n  536  pnl +4.3118  dd 0.2761  wr 64.4%  metro +4.0357
     selezione : n  536  pnl +4.3118  dd 0.2761  wr 64.4%  metro +4.0357  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +4.0357)
     con size  : n  536  pnl +4.1769  dd 0.2675  metro +3.9094  (informativo: il verdetto e' sulla selezione)
     solo passate : n  408 | apri tutto pnl +4.0013 metro +3.7999 | selezione n  408 pnl +4.0013 metro +3.7999
     solo bocciate: n  128 | apri tutto pnl +0.3105 metro +0.0153 | selezione n  128 pnl +0.3105 metro +0.0153
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 132464, lam 1.0, intercetta +0.700 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.218
    stop_pct   +0.073
    long_x_banda -0.062
    vol_ratio  -0.035
    bb_pos     +0.027
    dist_ema   -0.026
    is_long    -0.019
    hour_sin   -0.017
    regime_bull -0.013
    hour_cos   +0.012
    rsi        -0.011
    market_up  +0.006
    atr_pct    +0.005
    adx        -0.002
    regime_bear -0.001
    long_x_mercato -0.001
    stoch_k    +0.000
    regime_incerto +0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 132464 righe, soglia 0.40, verdetto NON BATTE, stato ombra.
[selettore] fatto in 87.4s
```
