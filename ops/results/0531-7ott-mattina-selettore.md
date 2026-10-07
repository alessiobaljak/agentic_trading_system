# 0531-7ott-mattina-selettore.req

_eseguito: 2026-10-07 06:14 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 119.7s

```
[selettore] 144760 trade da 1023 file (943352 duplicati fusi, 1512444 gemelle fuse, 0 righe rotte saltate)
[selettore] 2307 coppie coin+strategia; famiglie: reversion 95301, momentum 47432, breakout 2027
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 144748 trade usabili (12 scartati: variabili mancanti), 72561 di spec passate e 72187 di bocciate, dal 2023-02-27 al 2026-08-22
  finestra 1 [2025-11-16 -> 2026-02-15] train 57899 | soglia 0.40
     apri tutto: n 28950  pnl +126.6795  dd 1.6743  wr 66.5%  metro +125.0052
     selezione : n 28950  pnl +126.6795  dd 1.6743  wr 66.5%  metro +125.0052  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +125.0052)
     con size  : n 28950  pnl +133.1431  dd 1.5596  metro +131.5834  (informativo: il verdetto e' sulla selezione)
     solo passate : n 16239 | apri tutto pnl +85.7995 metro +85.1566 | selezione n 16239 pnl +85.7995 metro +85.1566
     solo bocciate: n 12711 | apri tutto pnl +40.8799 metro +39.6446 | selezione n 12711 pnl +40.8799 metro +39.6446
  finestra 2 [2026-02-15 -> 2026-05-18] train 86849 | soglia 0.40
     apri tutto: n 28949  pnl +123.2826  dd 1.2803  wr 66.5%  metro +122.0023
     selezione : n 28949  pnl +123.2826  dd 1.2803  wr 66.5%  metro +122.0023  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +122.0023)
     con size  : n 28949  pnl +129.8709  dd 1.2307  metro +128.6403  (informativo: il verdetto e' sulla selezione)
     solo passate : n 16261 | apri tutto pnl +82.8237 metro +81.9702 | selezione n 16261 pnl +82.8237 metro +81.9702
     solo bocciate: n 12688 | apri tutto pnl +40.4590 metro +39.6540 | selezione n 12688 pnl +40.4590 metro +39.6540
  finestra 3 [2026-05-18 -> 2026-08-22] train 115798 | soglia 0.45
     apri tutto: n 28950  pnl +141.5395  dd 0.8731  wr 67.5%  metro +140.6664
     selezione : n 28950  pnl +141.5395  dd 0.8731  wr 67.5%  metro +140.6664  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +140.6664)
     con size  : n 28950  pnl +134.6127  dd 0.7568  metro +133.8559  (informativo: il verdetto e' sulla selezione)
     solo passate : n 16737 | apri tutto pnl +93.9810 metro +93.3516 | selezione n 16737 pnl +93.9810 metro +93.3516
     solo bocciate: n 12213 | apri tutto pnl +47.5585 metro +47.0260 | selezione n 12213 pnl +47.5585 metro +47.0260
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 95289 trade usabili (12 scartati: variabili mancanti), 46586 di spec passate e 48703 di bocciate, dal 2023-02-27 al 2026-08-22
  finestra 1 [2025-11-20 -> 2026-02-18] train 38116 | soglia 0.45
     apri tutto: n 19058  pnl +80.0881  dd 2.4389  wr 66.5%  metro +77.6493
     selezione : n 19058  pnl +80.0881  dd 2.4389  wr 66.5%  metro +77.6493  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +77.6493)
     con size  : n 19058  pnl +77.5231  dd 2.1856  metro +75.3375  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10726 | apri tutto pnl +55.0589 metro +53.8588 | selezione n 10726 pnl +55.0589 metro +53.8588
     solo bocciate: n 8332 | apri tutto pnl +25.0292 metro +23.1494 | selezione n 8332 pnl +25.0292 metro +23.1494
  finestra 2 [2026-02-18 -> 2026-05-19] train 57174 | soglia 0.50
     apri tutto: n 19057  pnl +73.6159  dd 1.2256  wr 66.3%  metro +72.3902
     selezione : n 19050  pnl +73.6829  dd 1.2256  wr 66.3%  metro +72.4572  -> non batte (margine +0.0670, p_perm 0.060, 95° perc. +72.4615)
     con size  : n 19050  pnl +64.3084  dd 0.9757  metro +63.3327  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10848 | apri tutto pnl +50.9217 metro +50.0754 | selezione n 10846 pnl +50.9636 metro +50.1174
     solo bocciate: n 8209 | apri tutto pnl +22.6942 metro +21.9363 | selezione n 8204 pnl +22.7193 metro +21.9614
  finestra 3 [2026-05-19 -> 2026-08-22] train 76231 | soglia 0.50
     apri tutto: n 19058  pnl +95.1322  dd 1.0691  wr 68.5%  metro +94.0631
     selezione : n 19051  pnl +95.0629  dd 1.0691  wr 68.5%  metro +93.9938  -> non batte (margine -0.0693, p_perm 0.720, 95° perc. +94.1399)
     con size  : n 19051  pnl +80.7381  dd 0.8459  metro +79.8922  (informativo: il verdetto e' sulla selezione)
     solo passate : n 11218 | apri tutto pnl +62.4286 metro +61.8342 | selezione n 11215 pnl +62.3970 metro +61.8025
     solo bocciate: n 7840 | apri tutto pnl +32.7035 metro +32.1703 | selezione n 7836 pnl +32.6659 metro +32.1326
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 47432 trade usabili, 24571 di spec passate e 22861 di bocciate, dal 2023-03-01 al 2026-08-22
  finestra 1 [2025-11-03 -> 2026-02-09] train 18973 | soglia 0.40
     apri tutto: n 9486  pnl +43.7159  dd 0.9222  wr 66.3%  metro +42.7938
     selezione : n 9486  pnl +43.7159  dd 0.9222  wr 66.3%  metro +42.7938  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +42.7938)
     con size  : n 9486  pnl +45.8193  dd 0.8973  metro +44.9220  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5289 | apri tutto pnl +29.3714 metro +28.6281 | selezione n 5289 pnl +29.3714 metro +28.6281
     solo bocciate: n 4197 | apri tutto pnl +14.3445 metro +13.8408 | selezione n 4197 pnl +14.3445 metro +13.8408
  finestra 2 [2026-02-09 -> 2026-05-15] train 28459 | soglia 0.50
     apri tutto: n 9487  pnl +48.0518  dd 0.6025  wr 67.2%  metro +47.4493
     selezione : n 9473  pnl +48.1425  dd 0.6025  wr 67.2%  metro +47.5400  -> non batte (margine +0.0907, p_perm 0.060, 95° perc. +47.5535)
     con size  : n 9473  pnl +40.4156  dd 0.5472  metro +39.8684  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5156 | apri tutto pnl +30.4400 metro +29.9096 | selezione n 5146 pnl +30.4599 metro +29.9295
     solo bocciate: n 4331 | apri tutto pnl +17.6119 metro +17.0292 | selezione n 4327 pnl +17.6827 metro +17.1001
  finestra 3 [2026-05-15 -> 2026-08-22] train 37946 | soglia 0.50
     apri tutto: n 9486  pnl +44.7209  dd 0.7380  wr 65.9%  metro +43.9829
     selezione : n 9479  pnl +44.6013  dd 0.7380  wr 66.0%  metro +43.8633  -> non batte (margine -0.1196, p_perm 0.810, 95° perc. +44.0766)
     con size  : n 9479  pnl +38.6833  dd 0.5511  metro +38.1322  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5220 | apri tutto pnl +30.2732 metro +29.6423 | selezione n 5214 pnl +30.1360 metro +29.5051
     solo bocciate: n 4266 | apri tutto pnl +14.4477 metro +13.7320 | selezione n 4265 pnl +14.4653 metro +13.7496
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 2027 trade usabili, 1404 di spec passate e 623 di bocciate, dal 2024-01-23 al 2026-08-21
  finestra 1 [2025-12-31 -> 2026-03-14] train   811 | soglia 0.55
     apri tutto: n  405  pnl +1.8349  dd 0.3020  wr 65.7%  metro +1.5328
     selezione : n  348  pnl +1.4136  dd 0.3196  wr 65.2%  metro +1.0939  -> non batte (margine -0.4389, p_perm 0.850, 95° perc. +1.6593)
     con size  : n  348  pnl +1.1378  dd 0.2221  metro +0.9157  (informativo: il verdetto e' sulla selezione)
     solo passate : n  268 | apri tutto pnl +1.7631 metro +1.5299 | selezione n  235 pnl +1.4518 metro +1.1932
     solo bocciate: n  137 | apri tutto pnl +0.0717 metro -0.1063 | selezione n  113 pnl -0.0382 metro -0.2667
  finestra 2 [2026-03-14 -> 2026-05-31] train  1216 | soglia 0.45
     apri tutto: n  406  pnl +2.3988  dd 0.3240  wr 66.3%  metro +2.0747
     selezione : n  397  pnl +1.9721  dd 0.3006  wr 66.0%  metro +1.6715  -> non batte (margine -0.4033, p_perm 1.000, 95° perc. +2.1688)
     con size  : n  397  pnl +1.6392  dd 0.2632  metro +1.3760  (informativo: il verdetto e' sulla selezione)
     solo passate : n  257 | apri tutto pnl +1.5712 metro +1.2503 | selezione n  250 pnl +1.1408 metro +0.7713
     solo bocciate: n  149 | apri tutto pnl +0.8276 metro +0.6209 | selezione n  147 pnl +0.8313 metro +0.6481
  finestra 3 [2026-05-31 -> 2026-08-21] train  1622 | soglia 0.45
     apri tutto: n  405  pnl +2.1034  dd 0.3669  wr 61.2%  metro +1.7365
     selezione : n  405  pnl +2.1034  dd 0.3669  wr 61.2%  metro +1.7365  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +1.7365)
     con size  : n  405  pnl +1.7878  dd 0.3143  metro +1.4735  (informativo: il verdetto e' sulla selezione)
     solo passate : n  262 | apri tutto pnl +1.5231 metro +1.2146 | selezione n  262 pnl +1.5231 metro +1.2146
     solo bocciate: n  143 | apri tutto pnl +0.5803 metro +0.3178 | selezione n  143 pnl +0.5803 metro +0.3178
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 144748, lam 1.0, intercetta +0.707 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.231
    stop_pct   +0.075
    long_x_banda -0.062
    vol_ratio  -0.032
    bb_pos     +0.028
    is_long    -0.019
    dist_ema   -0.018
    rsi        -0.017
    hour_sin   -0.014
    market_up  +0.011
    hour_cos   +0.011
    regime_bull -0.008
    stoch_k    -0.005
    atr_pct    +0.005
    adx        -0.004
    regime_incerto +0.003
    regime_bear +0.002
    long_x_mercato +0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 144760 righe, soglia 0.40, verdetto NON BATTE, stato ombra.
[selettore] fatto in 117.9s
```
