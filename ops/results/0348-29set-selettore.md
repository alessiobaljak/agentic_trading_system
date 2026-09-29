# 0348-29set-selettore.req

_eseguito: 2026-09-29 06:17 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 41.0s

```
[selettore] 87490 trade da 298 file (192113 duplicati fusi, 235362 gemelle fuse, 0 righe rotte saltate)
[selettore] 1226 coppie coin+strategia; famiglie: reversion 61692, momentum 24409, breakout 1389
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 87490 trade usabili, 35518 di spec passate e 51972 di bocciate, dal 2023-02-27 al 2026-08-14
  finestra 1 [2025-11-04 -> 2026-02-08] train 34996 | soglia 0.50
     apri tutto: n 17498  pnl +74.6177  dd 1.9103  wr 66.4%  metro +72.7073
     selezione : n 17497  pnl +74.5938  dd 1.9103  wr 66.4%  metro +72.6835  -> non batte (margine -0.0238, p_perm 0.880, 95° perc. +72.7414)
     con size  : n 17497  pnl +62.6403  dd 1.5068  metro +61.1335  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7918 | apri tutto pnl +38.7587 metro +37.8947 | selezione n 7918 pnl +38.7587 metro +37.8947
     solo bocciate: n 9580 | apri tutto pnl +35.8589 metro +34.7538 | selezione n 9579 pnl +35.8351 metro +34.7300
  finestra 2 [2026-02-08 -> 2026-05-12] train 52494 | soglia 0.45
     apri tutto: n 17498  pnl +74.7419  dd 0.7911  wr 66.4%  metro +73.9509
     selezione : n 17498  pnl +74.7419  dd 0.7911  wr 66.4%  metro +73.9509  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +73.9509)
     con size  : n 17498  pnl +70.2746  dd 0.6541  metro +69.6204  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7896 | apri tutto pnl +40.2254 metro +39.6452 | selezione n 7896 pnl +40.2254 metro +39.6452
     solo bocciate: n 9602 | apri tutto pnl +34.5166 metro +33.7906 | selezione n 9602 pnl +34.5166 metro +33.7906
  finestra 3 [2026-05-12 -> 2026-08-14] train 69992 | soglia 0.50
     apri tutto: n 17498  pnl +85.6672  dd 0.6502  wr 66.9%  metro +85.0170
     selezione : n 17496  pnl +85.6804  dd 0.6502  wr 66.9%  metro +85.0302  -> non batte (margine +0.0132, p_perm 0.280, 95° perc. +85.0694)
     con size  : n 17496  pnl +73.1076  dd 0.5089  metro +72.5987  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8183 | apri tutto pnl +46.0245 metro +45.5689 | selezione n 8183 pnl +46.0245 metro +45.5689
     solo bocciate: n 9315 | apri tutto pnl +39.6426 metro +39.0535 | selezione n 9313 pnl +39.6559 metro +39.0668
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 61692 trade usabili, 26427 di spec passate e 35265 di bocciate, dal 2023-02-27 al 2026-08-14
  finestra 1 [2025-11-07 -> 2026-02-08] train 24677 | soglia 0.50
     apri tutto: n 12338  pnl +53.5376  dd 2.1863  wr 67.1%  metro +51.3513
     selezione : n 12326  pnl +53.4517  dd 2.1682  wr 67.1%  metro +51.2835  -> non batte (margine -0.0678, p_perm 0.550, 95° perc. +51.4194)
     con size  : n 12326  pnl +45.7881  dd 1.7226  metro +44.0655  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6130 | apri tutto pnl +30.8666 metro +30.0133 | selezione n 6123 pnl +30.7875 metro +29.9342
     solo bocciate: n 6208 | apri tutto pnl +22.6710 metro +21.1448 | selezione n 6203 pnl +22.6642 metro +21.1561
  finestra 2 [2026-02-08 -> 2026-05-12] train 37015 | soglia 0.40
     apri tutto: n 12339  pnl +49.1834  dd 0.7701  wr 66.5%  metro +48.4133
     selezione : n 12339  pnl +49.1834  dd 0.7701  wr 66.5%  metro +48.4133  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +48.4133)
     con size  : n 12339  pnl +51.9657  dd 0.7054  metro +51.2602  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6328 | apri tutto pnl +30.7778 metro +30.1431 | selezione n 6328 pnl +30.7778 metro +30.1431
     solo bocciate: n 6011 | apri tutto pnl +18.4056 metro +17.7493 | selezione n 6011 pnl +18.4056 metro +17.7493
  finestra 3 [2026-05-12 -> 2026-08-14] train 49354 | soglia 0.50
     apri tutto: n 12338  pnl +60.1756  dd 0.9318  wr 68.0%  metro +59.2438
     selezione : n 12327  pnl +60.1522  dd 0.9318  wr 68.0%  metro +59.2204  -> non batte (margine -0.0234, p_perm 0.400, 95° perc. +59.3350)
     con size  : n 12327  pnl +51.8206  dd 0.7701  metro +51.0505  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6581 | apri tutto pnl +35.6081 metro +35.0263 | selezione n 6575 pnl +35.6133 metro +35.0315
     solo bocciate: n 5757 | apri tutto pnl +24.5675 metro +24.1074 | selezione n 5752 pnl +24.5389 metro +24.0788
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 24409 trade usabili, 8248 di spec passate e 16161 di bocciate, dal 2023-03-01 al 2026-08-14
  finestra 1 [2025-10-25 -> 2026-02-05] train  9764 | soglia 0.50
     apri tutto: n 4882  pnl +19.9305  dd 0.6260  wr 64.7%  metro +19.3045
     selezione : n 4862  pnl +19.8558  dd 0.6260  wr 64.6%  metro +19.2298  -> non batte (margine -0.0747, p_perm 0.480, 95° perc. +19.3870)
     con size  : n 4862  pnl +16.2954  dd 0.5446  metro +15.7508  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1644 | apri tutto pnl +6.5770 metro +6.2873 | selezione n 1640 pnl +6.5374 metro +6.2477
     solo bocciate: n 3238 | apri tutto pnl +13.3535 metro +12.8743 | selezione n 3222 pnl +13.3184 metro +12.8393
  finestra 2 [2026-02-05 -> 2026-05-12] train 14646 | soglia 0.50
     apri tutto: n 4881  pnl +23.9350  dd 0.5446  wr 65.8%  metro +23.3904
     selezione : n 4881  pnl +23.9350  dd 0.5446  wr 65.8%  metro +23.3904  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +23.3904)
     con size  : n 4881  pnl +19.5085  dd 0.4609  metro +19.0475  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1399 | apri tutto pnl +8.3681 metro +7.9875 | selezione n 1399 pnl +8.3681 metro +7.9875
     solo bocciate: n 3482 | apri tutto pnl +15.5668 metro +14.9855 | selezione n 3482 pnl +15.5668 metro +14.9855
  finestra 3 [2026-05-12 -> 2026-08-14] train 19527 | soglia 0.40
     apri tutto: n 4882  pnl +23.9526  dd 0.5780  wr 64.4%  metro +23.3746
     selezione : n 4882  pnl +23.9526  dd 0.5780  wr 64.4%  metro +23.3746  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +23.3746)
     con size  : n 4882  pnl +25.1149  dd 0.5839  metro +24.5309  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1479 | apri tutto pnl +9.4852 metro +9.2077 | selezione n 1479 pnl +9.4852 metro +9.2077
     solo bocciate: n 3403 | apri tutto pnl +14.4674 metro +13.7512 | selezione n 3403 pnl +14.4674 metro +13.7512
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1389 trade usabili, 843 di spec passate e 546 di bocciate, dal 2024-01-23 al 2026-08-13
  finestra 1 [2025-12-05 -> 2026-02-26] train   556 | soglia 0.45
     apri tutto: n  278  pnl +1.1835  dd 0.1984  wr 64.0%  metro +0.9851
     selezione : n  271  pnl +1.1734  dd 0.1984  wr 64.2%  metro +0.9750  -> non batte (margine -0.0101, p_perm 0.430, 95° perc. +1.0821)
     con size  : n  271  pnl +1.1873  dd 0.1698  metro +1.0175  (informativo: il verdetto e' sulla selezione)
     solo passate : n  122 | apri tutto pnl +0.7644 metro +0.6351 | selezione n  121 pnl +0.7943 metro +0.6650
     solo bocciate: n  156 | apri tutto pnl +0.4191 metro +0.2321 | selezione n  150 pnl +0.3791 metro +0.2228
  finestra 2 [2026-02-26 -> 2026-05-20] train   834 | soglia 0.55
     apri tutto: n  277  pnl +1.7846  dd 0.2206  wr 68.2%  metro +1.5640
     selezione : n  233  pnl +1.3536  dd 0.2287  wr 67.8%  metro +1.1249  -> non batte (margine -0.4392, p_perm 0.840, 95° perc. +1.5694)
     con size  : n  233  pnl +1.0772  dd 0.1448  metro +0.9324  (informativo: il verdetto e' sulla selezione)
     solo passate : n  147 | apri tutto pnl +1.1425 metro +0.9554 | selezione n  128 pnl +0.9183 metro +0.7230
     solo bocciate: n  130 | apri tutto pnl +0.6421 metro +0.4579 | selezione n  105 pnl +0.4353 metro +0.2700
  finestra 3 [2026-05-20 -> 2026-08-13] train  1111 | soglia 0.40
     apri tutto: n  278  pnl +1.2890  dd 0.2122  wr 60.8%  metro +1.0768
     selezione : n  278  pnl +1.2890  dd 0.2122  wr 60.8%  metro +1.0768  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +1.0768)
     con size  : n  278  pnl +1.3229  dd 0.2106  metro +1.1122  (informativo: il verdetto e' sulla selezione)
     solo passate : n  129 | apri tutto pnl +0.8204 metro +0.5437 | selezione n  129 pnl +0.8204 metro +0.5437
     solo bocciate: n  149 | apri tutto pnl +0.4686 metro +0.1735 | selezione n  149 pnl +0.4686 metro +0.1735
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 87490, lam 1.0, intercetta +0.694 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.190
    bb_pos     +0.065
    stop_pct   +0.054
    long_x_banda -0.050
    dist_ema   -0.043
    atr_pct    +0.039
    vol_ratio  -0.032
    is_long    -0.029
    stoch_k    -0.024
    rsi        -0.016
    regime_bull -0.015
    market_up  +0.012
    hour_sin   -0.012
    long_x_mercato -0.011
    hour_cos   +0.008
    regime_incerto -0.005
    regime_bear -0.001
    adx        +0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 87490 righe, soglia 0.50, verdetto NON BATTE, stato ombra.
[selettore] fatto in 39.6s
```
