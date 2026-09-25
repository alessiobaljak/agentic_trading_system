# 0249-selettore-pubblica-modello.req

_eseguito: 2026-09-25 12:08 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 13.6s

```
[selettore] 41404 trade da 34 file (11761 duplicati fusi, 32871 gemelle fuse, 0 righe rotte saltate)
[selettore] 635 coppie coin+strategia; famiglie: reversion 34078, momentum 7326
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 41404 trade usabili, 17098 di spec passate e 24306 di bocciate, dal 2023-02-27 al 2026-08-10
  finestra 1 [2025-10-17 -> 2026-01-27] train 16562 | soglia 0.40
     apri tutto: n 8281  pnl +34.8420  dd 1.4717  wr 67.7%  metro +33.3703
     selezione : n 8281  pnl +34.8420  dd 1.4717  wr 67.7%  metro +33.3703  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +33.3703)
     con size  : n 8281  pnl +36.5384  dd 1.4782  metro +35.0602  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3980 | apri tutto pnl +19.7247 metro +18.9913 | selezione n 3980 pnl +19.7247 metro +18.9913
     solo bocciate: n 4301 | apri tutto pnl +15.1173 metro +14.2982 | selezione n 4301 pnl +15.1173 metro +14.2982
  finestra 2 [2026-01-27 -> 2026-05-05] train 24843 | soglia 0.45
     apri tutto: n 8280  pnl +32.5113  dd 0.7561  wr 66.8%  metro +31.7552
     selezione : n 8280  pnl +32.5113  dd 0.7561  wr 66.8%  metro +31.7552  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +31.7552)
     con size  : n 8280  pnl +31.7179  dd 0.6701  metro +31.0478  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4030 | apri tutto pnl +18.0582 metro +17.5967 | selezione n 4030 pnl +18.0582 metro +17.5967
     solo bocciate: n 4250 | apri tutto pnl +14.4531 metro +14.0554 | selezione n 4250 pnl +14.4531 metro +14.0554
  finestra 3 [2026-05-06 -> 2026-08-10] train 33123 | soglia 0.50
     apri tutto: n 8281  pnl +35.3903  dd 0.6532  wr 67.4%  metro +34.7371
     selezione : n 8268  pnl +35.3416  dd 0.6532  wr 67.4%  metro +34.6883  -> non batte (margine -0.0487, p_perm 0.370, 95° perc. +34.8055)
     con size  : n 8268  pnl +31.2777  dd 0.5703  metro +30.7074  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4265 | apri tutto pnl +19.9596 metro +19.4979 | selezione n 4258 pnl +19.9561 metro +19.4945
     solo bocciate: n 4016 | apri tutto pnl +15.4307 metro +14.9541 | selezione n 4010 pnl +15.3854 metro +14.9089
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 34078 trade usabili, 14025 di spec passate e 20053 di bocciate, dal 2023-02-27 al 2026-08-10
  finestra 1 [2025-10-30 -> 2026-02-03] train 13631 | soglia 0.40
     apri tutto: n 6816  pnl +28.9331  dd 1.4717  wr 67.5%  metro +27.4614
     selezione : n 6815  pnl +28.9437  dd 1.4717  wr 67.5%  metro +27.4720  -> non batte (margine +0.0106, p_perm 0.330, 95° perc. +27.4911)
     con size  : n 6815  pnl +30.6836  dd 1.4916  metro +29.1919  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3312 | apri tutto pnl +16.6973 metro +15.9639 | selezione n 3311 pnl +16.7079 metro +15.9745
     solo bocciate: n 3504 | apri tutto pnl +12.2358 metro +11.3726 | selezione n 3504 pnl +12.2358 metro +11.3726
  finestra 2 [2026-02-03 -> 2026-05-09] train 20447 | soglia 0.45
     apri tutto: n 6815  pnl +26.7088  dd 0.5929  wr 66.9%  metro +26.1160
     selezione : n 6812  pnl +26.7370  dd 0.5929  wr 66.9%  metro +26.1442  -> non batte (margine +0.0282, p_perm 0.110, 95° perc. +26.1630)
     con size  : n 6812  pnl +26.6023  dd 0.4970  metro +26.1052  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3417 | apri tutto pnl +16.3387 metro +15.8510 | selezione n 3416 pnl +16.3328 metro +15.8452
     solo bocciate: n 3398 | apri tutto pnl +10.3702 metro +9.9851 | selezione n 3396 pnl +10.4042 metro +10.0191
  finestra 3 [2026-05-09 -> 2026-08-10] train 27262 | soglia 0.45
     apri tutto: n 6816  pnl +30.4155  dd 0.6849  wr 68.0%  metro +29.7306
     selezione : n 6812  pnl +30.4134  dd 0.6849  wr 68.0%  metro +29.7285  -> non batte (margine -0.0021, p_perm 0.335, 95° perc. +29.7732)
     con size  : n 6812  pnl +29.7851  dd 0.6499  metro +29.1352  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3581 | apri tutto pnl +16.7436 metro +16.3001 | selezione n 3578 pnl +16.7429 metro +16.2995
     solo bocciate: n 3235 | apri tutto pnl +13.6719 metro +13.1780 | selezione n 3234 pnl +13.6705 metro +13.1765
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 7326 trade usabili, 3073 di spec passate e 4253 di bocciate, dal 2023-03-01 al 2026-08-10
  finestra 1 [2025-08-12 -> 2025-12-16] train  2930 | soglia 0.55
     apri tutto: n 1465  pnl +7.0005  dd 0.2368  wr 70.0%  metro +6.7637
     selezione : n 1311  pnl +6.2993  dd 0.2342  wr 70.6%  metro +6.0652  -> non batte (margine -0.6985, p_perm 0.475, 95° perc. +6.4743)
     con size  : n 1311  pnl +5.2222  dd 0.1758  metro +5.0464  (informativo: il verdetto e' sulla selezione)
     solo passate : n  665 | apri tutto pnl +3.8699 metro +3.7352 | selezione n  598 pnl +3.5960 metro +3.4476
     solo bocciate: n  800 | apri tutto pnl +3.1306 metro +2.9405 | selezione n  713 pnl +2.7033 metro +2.5302
  finestra 2 [2025-12-16 -> 2026-04-16] train  4395 | soglia 0.40
     apri tutto: n 1466  pnl +4.4373  dd 0.2832  wr 65.1%  metro +4.1540
     selezione : n 1465  pnl +4.4859  dd 0.2832  wr 65.2%  metro +4.2026  -> BATTE (margine +0.0486, p_perm 0.010, 95° perc. +4.1814)
     con size  : n 1465  pnl +4.6764  dd 0.2965  metro +4.3799  (informativo: il verdetto e' sulla selezione)
     solo passate : n  637 | apri tutto pnl +1.6008 metro +1.4068 | selezione n  637 pnl +1.6008 metro +1.4068
     solo bocciate: n  829 | apri tutto pnl +2.8365 metro +2.6068 | selezione n  828 pnl +2.8851 metro +2.6554
  finestra 3 [2026-04-16 -> 2026-08-10] train  5861 | soglia 0.40
     apri tutto: n 1465  pnl +4.7425  dd 0.5349  wr 64.6%  metro +4.2076
     selezione : n 1465  pnl +4.7425  dd 0.5349  wr 64.6%  metro +4.2076  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +4.2076)
     con size  : n 1465  pnl +5.2834  dd 0.5557  metro +4.7278  (informativo: il verdetto e' sulla selezione)
     solo passate : n  653 | apri tutto pnl +2.5470 metro +2.3383 | selezione n  653 pnl +2.5470 metro +2.3383
     solo bocciate: n  812 | apri tutto pnl +2.1955 metro +1.7562 | selezione n  812 pnl +2.1955 metro +1.7562
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 41404, lam 1.0, intercetta +0.715 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.192
    bb_pos     +0.079
    stop_pct   +0.076
    atr_pct    +0.071
    dist_ema   -0.055
    stoch_k    -0.048
    vol_ratio  -0.043
    regime_bull -0.034
    is_long    -0.032
    long_x_mercato -0.029
    adx        +0.022
    hour_cos   +0.013
    long_x_banda -0.012
    regime_incerto -0.012
    rsi        +0.011
    hour_sin   -0.011
    market_up  +0.006
    regime_bear +0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 41404 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 12.4s
```
