# 0453-3ott-mattina-selettore.req

_eseguito: 2026-10-03 06:11 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 71.3s

```
[selettore] 118414 trade da 672 file (518975 duplicati fusi, 658233 gemelle fuse, 0 righe rotte saltate)
[selettore] 1753 coppie coin+strategia; famiglie: reversion 78183, momentum 37882, breakout 2349
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 118414 trade usabili, 56918 di spec passate e 61496 di bocciate, dal 2023-02-27 al 2026-08-18
  finestra 1 [2025-11-12 -> 2026-02-12] train 47366 | soglia 0.45
     apri tutto: n 23683  pnl +102.2803  dd 1.8020  wr 66.7%  metro +100.4784
     selezione : n 23683  pnl +102.2803  dd 1.8020  wr 66.7%  metro +100.4784  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +100.4784)
     con size  : n 23683  pnl +97.6453  dd 1.5237  metro +96.1216  (informativo: il verdetto e' sulla selezione)
     solo passate : n 12731 | apri tutto pnl +64.6077 metro +63.9421 | selezione n 12731 pnl +64.6077 metro +63.9421
     solo bocciate: n 10952 | apri tutto pnl +37.6726 metro +36.4253 | selezione n 10952 pnl +37.6726 metro +36.4253
  finestra 2 [2026-02-12 -> 2026-05-15] train 71049 | soglia 0.40
     apri tutto: n 23682  pnl +104.8931  dd 0.9962  wr 66.8%  metro +103.8970
     selezione : n 23682  pnl +104.8931  dd 0.9962  wr 66.8%  metro +103.8970  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +103.8970)
     con size  : n 23682  pnl +110.2591  dd 0.9515  metro +109.3076  (informativo: il verdetto e' sulla selezione)
     solo passate : n 12879 | apri tutto pnl +67.7418 metro +67.0973 | selezione n 12879 pnl +67.7418 metro +67.0973
     solo bocciate: n 10803 | apri tutto pnl +37.1514 metro +36.4384 | selezione n 10803 pnl +37.1514 metro +36.4384
  finestra 3 [2026-05-15 -> 2026-08-18] train 94731 | soglia 0.45
     apri tutto: n 23683  pnl +113.3360  dd 0.8226  wr 67.4%  metro +112.5134
     selezione : n 23683  pnl +113.3360  dd 0.8226  wr 67.4%  metro +112.5134  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +112.5134)
     con size  : n 23683  pnl +108.4500  dd 0.7477  metro +107.7023  (informativo: il verdetto e' sulla selezione)
     solo passate : n 13087 | apri tutto pnl +73.8090 metro +73.1799 | selezione n 13087 pnl +73.8090 metro +73.1799
     solo bocciate: n 10596 | apri tutto pnl +39.5270 metro +38.9154 | selezione n 10596 pnl +39.5270 metro +38.9154
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 78183 trade usabili, 37024 di spec passate e 41159 di bocciate, dal 2023-02-27 al 2026-08-18
  finestra 1 [2025-11-16 -> 2026-02-14] train 31273 | soglia 0.45
     apri tutto: n 15637  pnl +67.5229  dd 2.2290  wr 66.9%  metro +65.2940
     selezione : n 15636  pnl +67.5341  dd 2.2290  wr 66.9%  metro +65.3051  -> non batte (margine +0.0111, p_perm 0.280, 95° perc. +65.3240)
     con size  : n 15636  pnl +65.0241  dd 1.9152  metro +63.1090  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8531 | apri tutto pnl +42.5527 metro +41.7388 | selezione n 8530 pnl +42.5638 metro +41.7499
     solo bocciate: n 7106 | apri tutto pnl +24.9703 metro +23.3517 | selezione n 7106 pnl +24.9703 metro +23.3517
  finestra 2 [2026-02-14 -> 2026-05-16] train 46910 | soglia 0.50
     apri tutto: n 15636  pnl +61.7159  dd 1.2047  wr 66.6%  metro +60.5112
     selezione : n 15621  pnl +61.8665  dd 1.2047  wr 66.6%  metro +60.6618  -> BATTE (margine +0.1506, p_perm 0.025, 95° perc. +60.6061)
     con size  : n 15621  pnl +54.0855  dd 0.9948  metro +53.0908  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8751 | apri tutto pnl +41.9093 metro +41.2442 | selezione n 8745 pnl +41.9481 metro +41.2831
     solo bocciate: n 6885 | apri tutto pnl +19.8065 metro +19.1209 | selezione n 6876 pnl +19.9183 metro +19.2327
  finestra 3 [2026-05-16 -> 2026-08-18] train 62546 | soglia 0.50
     apri tutto: n 15637  pnl +73.8264  dd 0.7960  wr 68.3%  metro +73.0304
     selezione : n 15621  pnl +73.6249  dd 0.7960  wr 68.3%  metro +72.8288  -> non batte (margine -0.2015, p_perm 0.910, 95° perc. +73.1247)
     con size  : n 15621  pnl +63.3838  dd 0.6740  metro +62.7098  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8987 | apri tutto pnl +48.2571 metro +47.4518 | selezione n 8978 pnl +48.1949 metro +47.3896
     solo bocciate: n 6650 | apri tutto pnl +25.5693 metro +25.0473 | selezione n 6643 pnl +25.4299 metro +24.9079
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 37882 trade usabili, 18083 di spec passate e 19799 di bocciate, dal 2023-03-01 al 2026-08-18
  finestra 1 [2025-11-02 -> 2026-02-08] train 15153 | soglia 0.40
     apri tutto: n 7576  pnl +33.2812  dd 0.8156  wr 66.2%  metro +32.4657
     selezione : n 7576  pnl +33.2812  dd 0.8156  wr 66.2%  metro +32.4657  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +32.4657)
     con size  : n 7576  pnl +34.9050  dd 0.8119  metro +34.0930  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3878 | apri tutto pnl +20.8656 metro +20.1159 | selezione n 3878 pnl +20.8656 metro +20.1159
     solo bocciate: n 3698 | apri tutto pnl +12.4157 metro +11.8556 | selezione n 3698 pnl +12.4157 metro +11.8556
  finestra 2 [2026-02-08 -> 2026-05-13] train 22729 | soglia 0.50
     apri tutto: n 7577  pnl +39.0487  dd 0.6269  wr 67.2%  metro +38.4219
     selezione : n 7572  pnl +39.1771  dd 0.6269  wr 67.3%  metro +38.5502  -> BATTE (margine +0.1283, p_perm 0.025, 95° perc. +38.5235)
     con size  : n 7572  pnl +32.4469  dd 0.5524  metro +31.8944  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3773 | apri tutto pnl +22.5207 metro +21.8702 | selezione n 3771 pnl +22.5963 metro +21.9458
     solo bocciate: n 3804 | apri tutto pnl +16.5280 metro +15.9602 | selezione n 3801 pnl +16.5807 metro +16.0130
  finestra 3 [2026-05-13 -> 2026-08-18] train 30306 | soglia 0.50
     apri tutto: n 7576  pnl +37.5557  dd 0.5531  wr 66.0%  metro +37.0026
     selezione : n 7575  pnl +37.5463  dd 0.5531  wr 66.0%  metro +36.9932  -> non batte (margine -0.0094, p_perm 0.485, 95° perc. +37.0505)
     con size  : n 7575  pnl +32.0680  dd 0.4139  metro +31.6541  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3755 | apri tutto pnl +23.5914 metro +23.1880 | selezione n 3754 pnl +23.5820 metro +23.1692
     solo bocciate: n 3821 | apri tutto pnl +13.9644 metro +13.2615 | selezione n 3821 pnl +13.9644 metro +13.2615
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 2349 trade usabili, 1811 di spec passate e 538 di bocciate, dal 2024-01-23 al 2026-08-17
  finestra 1 [2025-12-05 -> 2026-02-26] train   940 | soglia 0.40
     apri tutto: n  470  pnl +2.3418  dd 0.2467  wr 67.5%  metro +2.0951
     selezione : n  469  pnl +2.3166  dd 0.2467  wr 67.4%  metro +2.0699  -> non batte (margine -0.0252, p_perm 0.795, 95° perc. +2.1379)
     con size  : n  469  pnl +2.5235  dd 0.2433  metro +2.2802  (informativo: il verdetto e' sulla selezione)
     solo passate : n  316 | apri tutto pnl +1.9279 metro +1.6798 | selezione n  315 pnl +1.9027 metro +1.6546
     solo bocciate: n  154 | apri tutto pnl +0.4139 metro +0.2269 | selezione n  154 pnl +0.4139 metro +0.2269
  finestra 2 [2026-02-26 -> 2026-05-23] train  1410 | soglia 0.40
     apri tutto: n  469  pnl +2.9626  dd 0.2190  wr 67.2%  metro +2.7436
     selezione : n  466  pnl +2.9223  dd 0.2190  wr 67.4%  metro +2.7033  -> non batte (margine -0.0403, p_perm 0.730, 95° perc. +2.8157)
     con size  : n  466  pnl +2.7415  dd 0.2525  metro +2.4890  (informativo: il verdetto e' sulla selezione)
     solo passate : n  336 | apri tutto pnl +2.3234 metro +2.0941 | selezione n  334 pnl +2.2647 metro +2.0487
     solo bocciate: n  133 | apri tutto pnl +0.6392 metro +0.4660 | selezione n  132 pnl +0.6576 metro +0.4845
  finestra 3 [2026-05-23 -> 2026-08-17] train  1879 | soglia 0.40
     apri tutto: n  470  pnl +2.9697  dd 0.4223  wr 62.3%  metro +2.5474
     selezione : n  470  pnl +2.9697  dd 0.4223  wr 62.3%  metro +2.5474  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +2.5474)
     con size  : n  470  pnl +2.6801  dd 0.3889  metro +2.2912  (informativo: il verdetto e' sulla selezione)
     solo passate : n  328 | apri tutto pnl +2.5316 metro +2.2445 | selezione n  328 pnl +2.5316 metro +2.2445
     solo bocciate: n  142 | apri tutto pnl +0.4380 metro +0.1429 | selezione n  142 pnl +0.4380 metro +0.1429
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 118414, lam 1.0, intercetta +0.710 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.230
    stop_pct   +0.070
    long_x_banda -0.059
    bb_pos     +0.036
    vol_ratio  -0.032
    dist_ema   -0.027
    is_long    -0.022
    rsi        -0.021
    hour_sin   -0.017
    atr_pct    +0.011
    regime_bull -0.011
    hour_cos   +0.010
    regime_incerto -0.006
    stoch_k    -0.005
    market_up  +0.005
    adx        -0.003
    regime_bear -0.003
    long_x_mercato -0.002
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 118414 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 69.7s
```
