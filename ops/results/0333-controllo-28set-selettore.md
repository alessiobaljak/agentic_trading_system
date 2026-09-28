# 0333-controllo-28set-selettore.req

_eseguito: 2026-09-28 06:19 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 32.8s

```
[selettore] 81490 trade da 212 file (145230 duplicati fusi, 188002 gemelle fuse, 0 righe rotte saltate)
[selettore] 1137 coppie coin+strategia; famiglie: reversion 58630, momentum 21486, breakout 1374
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 81490 trade usabili, 32283 di spec passate e 49207 di bocciate, dal 2023-02-27 al 2026-08-13
  finestra 1 [2025-11-03 -> 2026-02-07] train 32596 | soglia 0.50
     apri tutto: n 16298  pnl +72.8876  dd 1.7754  wr 66.8%  metro +71.1122
     selezione : n 16291  pnl +72.8127  dd 1.7689  wr 66.8%  metro +71.0438  -> non batte (margine -0.0684, p_perm 0.715, 95° perc. +71.1855)
     con size  : n 16291  pnl +61.1294  dd 1.4301  metro +59.6993  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7230 | apri tutto pnl +39.7049 metro +38.8526 | selezione n 7226 pnl +39.6661 metro +38.8138
     solo bocciate: n 9068 | apri tutto pnl +33.1827 metro +32.2405 | selezione n 9065 pnl +33.1466 metro +32.2110
  finestra 2 [2026-02-07 -> 2026-05-12] train 48894 | soglia 0.45
     apri tutto: n 16298  pnl +70.5721  dd 0.8285  wr 66.4%  metro +69.7436
     selezione : n 16298  pnl +70.5721  dd 0.8285  wr 66.4%  metro +69.7436  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +69.7436)
     con size  : n 16298  pnl +66.9580  dd 0.6898  metro +66.2682  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7203 | apri tutto pnl +37.7098 metro +37.1597 | selezione n 7203 pnl +37.7098 metro +37.1597
     solo bocciate: n 9095 | apri tutto pnl +32.8624 metro +32.1777 | selezione n 9095 pnl +32.8624 metro +32.1777
  finestra 3 [2026-05-12 -> 2026-08-13] train 65192 | soglia 0.40
     apri tutto: n 16298  pnl +81.0302  dd 0.6692  wr 67.2%  metro +80.3610
     selezione : n 16298  pnl +81.0302  dd 0.6692  wr 67.2%  metro +80.3610  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +80.3610)
     con size  : n 16298  pnl +85.9131  dd 0.6814  metro +85.2317  (informativo: il verdetto e' sulla selezione)
     solo passate : n 7500 | apri tutto pnl +43.4651 metro +42.9686 | selezione n 7500 pnl +43.4651 metro +42.9686
     solo bocciate: n 8798 | apri tutto pnl +37.5651 metro +36.8078 | selezione n 8798 pnl +37.5651 metro +36.8078
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 58630 trade usabili, 24413 di spec passate e 34217 di bocciate, dal 2023-02-27 al 2026-08-13
  finestra 1 [2025-11-07 -> 2026-02-07] train 23452 | soglia 0.40
     apri tutto: n 11726  pnl +52.8564  dd 2.0436  wr 67.2%  metro +50.8128
     selezione : n 11726  pnl +52.8564  dd 2.0436  wr 67.2%  metro +50.8128  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +50.8128)
     con size  : n 11726  pnl +55.6546  dd 2.0306  metro +53.6240  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5685 | apri tutto pnl +30.9287 metro +30.0978 | selezione n 5685 pnl +30.9287 metro +30.0978
     solo bocciate: n 6041 | apri tutto pnl +21.9278 metro +20.5741 | selezione n 6041 pnl +21.9278 metro +20.5741
  finestra 2 [2026-02-07 -> 2026-05-12] train 35178 | soglia 0.50
     apri tutto: n 11726  pnl +49.0203  dd 0.7689  wr 66.7%  metro +48.2514
     selezione : n 11701  pnl +49.1245  dd 0.7689  wr 66.8%  metro +48.3556  -> BATTE (margine +0.1042, p_perm 0.030, 95° perc. +48.3174)
     con size  : n 11701  pnl +42.8119  dd 0.5552  metro +42.2567  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5874 | apri tutto pnl +31.0697 metro +30.5390 | selezione n 5866 pnl +31.1123 metro +30.5815
     solo bocciate: n 5852 | apri tutto pnl +17.9506 metro +17.2998 | selezione n 5835 pnl +18.0122 metro +17.3614
  finestra 3 [2026-05-12 -> 2026-08-13] train 46904 | soglia 0.50
     apri tutto: n 11726  pnl +58.8110  dd 0.8868  wr 68.2%  metro +57.9242
     selezione : n 11705  pnl +58.5769  dd 0.8868  wr 68.2%  metro +57.6901  -> non batte (margine -0.2341, p_perm 0.880, 95° perc. +58.0205)
     con size  : n 11705  pnl +51.0232  dd 0.7643  metro +50.2589  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6144 | apri tutto pnl +35.1122 metro +34.6118 | selezione n 6133 pnl +34.9589 metro +34.4585
     solo bocciate: n 5582 | apri tutto pnl +23.6988 metro +23.2660 | selezione n 5572 pnl +23.6180 metro +23.1853
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 21486 trade usabili, 7049 di spec passate e 14437 di bocciate, dal 2023-03-01 al 2026-08-13
  finestra 1 [2025-10-21 -> 2026-02-04] train  8594 | soglia 0.45
     apri tutto: n 4297  pnl +16.3865  dd 0.5181  wr 64.8%  metro +15.8684
     selezione : n 4296  pnl +16.3804  dd 0.5181  wr 64.8%  metro +15.8623  -> non batte (margine -0.0061, p_perm 0.450, 95° perc. +15.9009)
     con size  : n 4296  pnl +15.2668  dd 0.5002  metro +14.7666  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1406 | apri tutto pnl +6.7146 metro +6.5065 | selezione n 1406 pnl +6.7146 metro +6.5065
     solo bocciate: n 2891 | apri tutto pnl +9.6719 metro +9.1693 | selezione n 2890 pnl +9.6658 metro +9.1632
  finestra 2 [2026-02-04 -> 2026-05-12] train 12891 | soglia 0.50
     apri tutto: n 4298  pnl +21.4044  dd 0.4273  wr 66.3%  metro +20.9771
     selezione : n 4294  pnl +21.2045  dd 0.4273  wr 66.3%  metro +20.7773  -> non batte (margine -0.1998, p_perm 0.990, 95° perc. +21.0667)
     con size  : n 4294  pnl +17.4715  dd 0.3876  metro +17.0839  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1175 | apri tutto pnl +6.2858 metro +6.0057 | selezione n 1175 pnl +6.2858 metro +6.0057
     solo bocciate: n 3123 | apri tutto pnl +15.1186 metro +14.5377 | selezione n 3119 pnl +14.9188 metro +14.3379
  finestra 3 [2026-05-12 -> 2026-08-13] train 17189 | soglia 0.40
     apri tutto: n 4297  pnl +20.4394  dd 0.5552  wr 64.6%  metro +19.8842
     selezione : n 4297  pnl +20.4394  dd 0.5552  wr 64.6%  metro +19.8842  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +19.8842)
     con size  : n 4297  pnl +21.8212  dd 0.5530  metro +21.2682  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1240 | apri tutto pnl +7.1465 metro +6.9432 | selezione n 1240 pnl +7.1465 metro +6.9432
     solo bocciate: n 3057 | apri tutto pnl +13.2929 metro +12.5880 | selezione n 3057 pnl +13.2929 metro +12.5880
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1374 trade usabili, 821 di spec passate e 553 di bocciate, dal 2024-01-23 al 2026-08-13
  finestra 1 [2025-11-28 -> 2026-02-23] train   550 | soglia 0.40
     apri tutto: n  275  pnl +1.3918  dd 0.2121  wr 63.3%  metro +1.1797
     selezione : n  274  pnl +1.4260  dd 0.2121  wr 63.5%  metro +1.2139  -> BATTE (margine +0.0342, p_perm 0.040, 95° perc. +1.2112)
     con size  : n  274  pnl +1.4605  dd 0.2139  metro +1.2466  (informativo: il verdetto e' sulla selezione)
     solo passate : n  112 | apri tutto pnl +0.8866 metro +0.7947 | selezione n  111 pnl +0.9208 metro +0.8289
     solo bocciate: n  163 | apri tutto pnl +0.5052 metro +0.3182 | selezione n  163 pnl +0.5052 metro +0.3182
  finestra 2 [2026-02-24 -> 2026-05-19] train   825 | soglia 0.45
     apri tutto: n  274  pnl +1.6992  dd 0.2246  wr 65.0%  metro +1.4747
     selezione : n  264  pnl +1.5110  dd 0.2447  wr 65.1%  metro +1.2664  -> non batte (margine -0.2083, p_perm 0.950, 95° perc. +1.5675)
     con size  : n  264  pnl +1.3838  dd 0.1979  metro +1.1860  (informativo: il verdetto e' sulla selezione)
     solo passate : n  139 | apri tutto pnl +1.0531 metro +0.8729 | selezione n  132 pnl +0.9023 metro +0.7020
     solo bocciate: n  135 | apri tutto pnl +0.6461 metro +0.4619 | selezione n  132 pnl +0.6087 metro +0.4245
  finestra 3 [2026-05-19 -> 2026-08-13] train  1099 | soglia 0.45
     apri tutto: n  275  pnl +1.4300  dd 0.2047  wr 60.4%  metro +1.2253
     selezione : n  272  pnl +1.3603  dd 0.2047  wr 60.3%  metro +1.1556  -> non batte (margine -0.0697, p_perm 0.855, 95° perc. +1.2915)
     con size  : n  272  pnl +1.2287  dd 0.1792  metro +1.0495  (informativo: il verdetto e' sulla selezione)
     solo passate : n  124 | apri tutto pnl +0.9658 metro +0.7728 | selezione n  124 pnl +0.9658 metro +0.7728
     solo bocciate: n  151 | apri tutto pnl +0.4642 metro +0.1690 | selezione n  148 pnl +0.3944 metro +0.0993
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 81490, lam 1.0, intercetta +0.705 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.209
    bb_pos     +0.064
    stop_pct   +0.050
    atr_pct    +0.048
    long_x_banda -0.044
    dist_ema   -0.039
    vol_ratio  -0.033
    is_long    -0.027
    stoch_k    -0.025
    regime_bull -0.017
    rsi        -0.017
    hour_sin   -0.016
    long_x_mercato -0.012
    market_up  +0.008
    hour_cos   +0.005
    regime_bear +0.004
    regime_incerto -0.002
    adx        -0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 81490 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 31.6s
```
