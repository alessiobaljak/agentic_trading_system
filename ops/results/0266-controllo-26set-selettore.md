# 0266-controllo-26set-selettore.req

_eseguito: 2026-09-26 06:09 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 22.4s

```
[selettore] 54912 trade da 67 file (40242 duplicati fusi, 69585 gemelle fuse, 0 righe rotte saltate)
[selettore] 811 coppie coin+strategia; famiglie: reversion 43674, momentum 11238
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 54912 trade usabili, 22980 di spec passate e 31932 di bocciate, dal 2023-02-27 al 2026-08-11
  finestra 1 [2025-10-21 -> 2026-01-31] train 21965 | soglia 0.45
     apri tutto: n 10982  pnl +48.5021  dd 1.5369  wr 67.5%  metro +46.9652
     selezione : n 10980  pnl +48.5046  dd 1.5369  wr 67.5%  metro +46.9677  -> non batte (margine +0.0025, p_perm 0.370, 95° perc. +47.0055)
     con size  : n 10980  pnl +45.5638  dd 1.3862  metro +44.1776  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5236 | apri tutto pnl +28.7134 metro +28.0006 | selezione n 5234 pnl +28.7159 metro +28.0031
     solo bocciate: n 5746 | apri tutto pnl +19.7886 metro +18.9096 | selezione n 5746 pnl +19.7886 metro +18.9096
  finestra 2 [2026-01-31 -> 2026-05-08] train 32947 | soglia 0.50
     apri tutto: n 10983  pnl +48.1044  dd 0.8862  wr 67.2%  metro +47.2182
     selezione : n 10981  pnl +48.1384  dd 0.8862  wr 67.2%  metro +47.2522  -> non batte (margine +0.0340, p_perm 0.095, 95° perc. +47.2630)
     con size  : n 10981  pnl +41.9795  dd 0.6810  metro +41.2985  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5293 | apri tutto pnl +27.1375 metro +26.7278 | selezione n 5293 pnl +27.1375 metro +26.7278
     solo bocciate: n 5690 | apri tutto pnl +20.9669 metro +20.3765 | selezione n 5688 pnl +21.0009 metro +20.4106
  finestra 3 [2026-05-08 -> 2026-08-11] train 43930 | soglia 0.50
     apri tutto: n 10982  pnl +51.9993  dd 0.6741  wr 67.7%  metro +51.3252
     selezione : n 10979  pnl +52.0184  dd 0.6741  wr 67.7%  metro +51.3443  -> non batte (margine +0.0191, p_perm 0.150, 95° perc. +51.3749)
     con size  : n 10979  pnl +46.0504  dd 0.5828  metro +45.4676  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5489 | apri tutto pnl +31.9073 metro +31.5181 | selezione n 5487 pnl +31.9148 metro +31.5256
     solo bocciate: n 5493 | apri tutto pnl +20.0920 metro +19.4865 | selezione n 5492 pnl +20.1036 metro +19.4981
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 43674 trade usabili, 18705 di spec passate e 24969 di bocciate, dal 2023-02-27 al 2026-08-11
  finestra 1 [2025-10-28 -> 2026-02-01] train 17470 | soglia 0.40
     apri tutto: n 8735  pnl +39.9128  dd 1.6292  wr 67.8%  metro +38.2836
     selezione : n 8734  pnl +39.9234  dd 1.6292  wr 67.8%  metro +38.2942  -> non batte (margine +0.0106, p_perm 0.330, 95° perc. +38.3139)
     con size  : n 8734  pnl +41.6379  dd 1.6240  metro +40.0139  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4407 | apri tutto pnl +25.3330 metro +24.6113 | selezione n 4406 pnl +25.3436 metro +24.6220
     solo bocciate: n 4328 | apri tutto pnl +14.5798 metro +13.5406 | selezione n 4328 pnl +14.5798 metro +13.5406
  finestra 2 [2026-02-01 -> 2026-05-08] train 26205 | soglia 0.50
     apri tutto: n 8734  pnl +37.6323  dd 0.6646  wr 67.2%  metro +36.9677
     selezione : n 8728  pnl +37.6997  dd 0.6646  wr 67.2%  metro +37.0351  -> BATTE (margine +0.0675, p_perm 0.040, 95° perc. +37.0245)
     con size  : n 8728  pnl +33.2508  dd 0.4870  metro +32.7638  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4535 | apri tutto pnl +23.6315 metro +23.1923 | selezione n 4532 pnl +23.6540 metro +23.2148
     solo bocciate: n 4199 | apri tutto pnl +14.0008 metro +13.4866 | selezione n 4196 pnl +14.0457 metro +13.5315
  finestra 3 [2026-05-08 -> 2026-08-11] train 34939 | soglia 0.50
     apri tutto: n 8735  pnl +42.8764  dd 0.7114  wr 68.4%  metro +42.1650
     selezione : n 8724  pnl +42.7932  dd 0.7114  wr 68.4%  metro +42.0818  -> non batte (margine -0.0832, p_perm 0.695, 95° perc. +42.2287)
     con size  : n 8724  pnl +37.8048  dd 0.6216  metro +37.1832  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4727 | apri tutto pnl +27.9708 metro +27.6010 | selezione n 4720 pnl +27.9352 metro +27.5654
     solo bocciate: n 4008 | apri tutto pnl +14.9056 metro +14.4329 | selezione n 4004 pnl +14.8580 metro +14.3854
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 11238 trade usabili, 4275 di spec passate e 6963 di bocciate, dal 2023-03-01 al 2026-08-11
  finestra 1 [2025-09-22 -> 2026-01-18] train  4495 | soglia 0.45
     apri tutto: n 2248  pnl +8.8458  dd 0.4966  wr 67.3%  metro +8.3492
     selezione : n 2248  pnl +8.8458  dd 0.4966  wr 67.3%  metro +8.3492  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +8.3492)
     con size  : n 2248  pnl +8.6645  dd 0.4550  metro +8.2095  (informativo: il verdetto e' sulla selezione)
     solo passate : n  869 | apri tutto pnl +4.2508 metro +4.0440 | selezione n  869 pnl +4.2508 metro +4.0440
     solo bocciate: n 1379 | apri tutto pnl +4.5950 metro +4.1607 | selezione n 1379 pnl +4.5950 metro +4.1607
  finestra 2 [2026-01-18 -> 2026-05-04] train  6743 | soglia 0.55
     apri tutto: n 2247  pnl +9.7199  dd 0.2709  wr 66.6%  metro +9.4490
     selezione : n 2224  pnl +9.4756  dd 0.2807  wr 66.5%  metro +9.1949  -> non batte (margine -0.2541, p_perm 0.870, 95° perc. +9.5543)
     con size  : n 2224  pnl +7.2840  dd 0.2154  metro +7.0687  (informativo: il verdetto e' sulla selezione)
     solo passate : n  709 | apri tutto pnl +2.4970 metro +2.3421 | selezione n  706 pnl +2.5219 metro +2.3670
     solo bocciate: n 1538 | apri tutto pnl +7.2229 metro +6.8963 | selezione n 1518 pnl +6.9537 metro +6.6271
  finestra 3 [2026-05-04 -> 2026-08-11] train  8990 | soglia 0.40
     apri tutto: n 2248  pnl +9.4408  dd 0.4012  wr 65.3%  metro +9.0396
     selezione : n 2248  pnl +9.4408  dd 0.4012  wr 65.3%  metro +9.0396  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +9.0396)
     con size  : n 2248  pnl +10.2502  dd 0.4303  metro +9.8199  (informativo: il verdetto e' sulla selezione)
     solo passate : n  758 | apri tutto pnl +4.0164 metro +3.8788 | selezione n  758 pnl +4.0164 metro +3.8788
     solo bocciate: n 1490 | apri tutto pnl +5.4244 metro +4.8769 | selezione n 1490 pnl +5.4244 metro +4.8769
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 54912, lam 1.0, intercetta +0.728 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.209
    atr_pct    +0.079
    is_long    -0.049
    stop_pct   +0.045
    dist_ema   -0.043
    bb_pos     +0.041
    vol_ratio  -0.035
    regime_bull -0.029
    stoch_k    -0.022
    long_x_mercato -0.022
    long_x_banda -0.020
    hour_sin   -0.016
    rsi        -0.013
    adx        +0.008
    regime_incerto -0.007
    regime_bear +0.006
    market_up  -0.002
    hour_cos   -0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 54912 righe, soglia 0.50, verdetto NON BATTE, stato ombra.
[selettore] fatto in 21.0s
```
