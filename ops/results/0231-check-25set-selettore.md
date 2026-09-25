# 0231-check-25set-selettore.req

_eseguito: 2026-09-25 05:13 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 12.5s

```
[selettore] 40997 trade da 22 file (9556 duplicati fusi, 32838 gemelle fuse, 0 righe rotte saltate)
[selettore] 632 coppie coin+strategia; famiglie: reversion 33895, momentum 7102
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 40997 trade usabili, 16685 di spec passate e 24312 di bocciate, dal 2023-02-27 al 2026-08-10
  finestra 1 [2025-10-17 -> 2026-01-28] train 16399 | soglia 0.40
     apri tutto: n 8199  pnl +34.7709  dd 1.4717  wr 67.7%  metro +33.2992
     selezione : n 8198  pnl +34.7815  dd 1.4717  wr 67.8%  metro +33.3098  -> non batte (margine +0.0106, p_perm 0.340, 95° perc. +33.3313)
     con size  : n 8198  pnl +36.4876  dd 1.4809  metro +35.0067  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3911 | apri tutto pnl +19.5638 metro +18.8275 | selezione n 3910 pnl +19.5744 metro +18.8381
     solo bocciate: n 4288 | apri tutto pnl +15.2071 metro +14.3879 | selezione n 4288 pnl +15.2071 metro +14.3879
  finestra 2 [2026-01-28 -> 2026-05-06] train 24598 | soglia 0.45
     apri tutto: n 8200  pnl +32.0074  dd 0.7453  wr 66.9%  metro +31.2621
     selezione : n 8200  pnl +32.0074  dd 0.7453  wr 66.9%  metro +31.2621  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +31.2621)
     con size  : n 8200  pnl +31.4051  dd 0.6623  metro +30.7428  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3958 | apri tutto pnl +17.5052 metro +17.0423 | selezione n 3958 pnl +17.5052 metro +17.0423
     solo bocciate: n 4242 | apri tutto pnl +14.5022 metro +14.1045 | selezione n 4242 pnl +14.5022 metro +14.1045
  finestra 3 [2026-05-06 -> 2026-08-10] train 32798 | soglia 0.50
     apri tutto: n 8199  pnl +35.0682  dd 0.6524  wr 67.5%  metro +34.4158
     selezione : n 8186  pnl +35.0194  dd 0.6524  wr 67.5%  metro +34.3671  -> non batte (margine -0.0487, p_perm 0.490, 95° perc. +34.4883)
     con size  : n 8186  pnl +31.0266  dd 0.5762  metro +30.4504  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4191 | apri tutto pnl +19.6019 metro +19.1360 | selezione n 4184 pnl +19.5984 metro +19.1325
     solo bocciate: n 4008 | apri tutto pnl +15.4663 metro +14.9897 | selezione n 4002 pnl +15.4210 metro +14.9445
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 33895 trade usabili, 13836 di spec passate e 20059 di bocciate, dal 2023-02-27 al 2026-08-10
  finestra 1 [2025-10-30 -> 2026-02-03] train 13558 | soglia 0.40
     apri tutto: n 6779  pnl +28.8246  dd 1.4717  wr 67.6%  metro +27.3529
     selezione : n 6778  pnl +28.8352  dd 1.4717  wr 67.6%  metro +27.3635  -> non batte (margine +0.0106, p_perm 0.330, 95° perc. +27.3841)
     con size  : n 6778  pnl +30.5518  dd 1.4949  metro +29.0569  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3262 | apri tutto pnl +16.4052 metro +15.6689 | selezione n 3261 pnl +16.4158 metro +15.6795
     solo bocciate: n 3517 | apri tutto pnl +12.4194 metro +11.5562 | selezione n 3517 pnl +12.4194 metro +11.5562
  finestra 2 [2026-02-03 -> 2026-05-09] train 20337 | soglia 0.50
     apri tutto: n 6779  pnl +26.3115  dd 0.5929  wr 66.9%  metro +25.7186
     selezione : n 6757  pnl +26.4117  dd 0.5598  wr 67.0%  metro +25.8519  -> BATTE (margine +0.1333, p_perm 0.035, 95° perc. +25.8052)
     con size  : n 6757  pnl +23.7293  dd 0.4507  metro +23.2785  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3377 | apri tutto pnl +15.8133 metro +15.3243 | selezione n 3368 pnl +15.8232 metro +15.3342
     solo bocciate: n 3402 | apri tutto pnl +10.4982 metro +10.1131 | selezione n 3389 pnl +10.5884 metro +10.2033
  finestra 3 [2026-05-09 -> 2026-08-10] train 27116 | soglia 0.45
     apri tutto: n 6779  pnl +30.2095  dd 0.6919  wr 68.1%  metro +29.5175
     selezione : n 6775  pnl +30.2074  dd 0.6919  wr 68.1%  metro +29.5155  -> non batte (margine -0.0021, p_perm 0.330, 95° perc. +29.5639)
     con size  : n 6775  pnl +29.5705  dd 0.6543  metro +28.9162  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3542 | apri tutto pnl +16.4929 metro +16.0317 | selezione n 3539 pnl +16.4923 metro +16.0311
     solo bocciate: n 3237 | apri tutto pnl +13.7166 metro +13.2227 | selezione n 3236 pnl +13.7151 metro +13.2212
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 7102 trade usabili, 2849 di spec passate e 4253 di bocciate, dal 2023-03-01 al 2026-08-10
  finestra 1 [2025-08-21 -> 2025-12-20] train  2841 | soglia 0.55
     apri tutto: n 1420  pnl +6.4638  dd 0.2368  wr 69.2%  metro +6.2270
     selezione : n 1311  pnl +6.0046  dd 0.2368  wr 69.6%  metro +5.7677  -> non batte (margine -0.4592, p_perm 0.470, 95° perc. +6.1781)
     con size  : n 1311  pnl +5.0019  dd 0.1717  metro +4.8302  (informativo: il verdetto e' sulla selezione)
     solo passate : n  645 | apri tutto pnl +3.7077 metro +3.5729 | selezione n  597 pnl +3.5944 metro +3.4468
     solo bocciate: n  775 | apri tutto pnl +2.7561 metro +2.5285 | selezione n  714 pnl +2.4102 metro +2.2189
  finestra 2 [2025-12-20 -> 2026-04-18] train  4261 | soglia 0.40
     apri tutto: n 1421  pnl +4.8704  dd 0.2832  wr 65.7%  metro +4.5872
     selezione : n 1420  pnl +4.9191  dd 0.2832  wr 65.7%  metro +4.6358  -> BATTE (margine +0.0486, p_perm 0.000, 95° perc. +4.6177)
     con size  : n 1420  pnl +5.1526  dd 0.3000  metro +4.8526  (informativo: il verdetto e' sulla selezione)
     solo passate : n  608 | apri tutto pnl +1.7558 metro +1.5618 | selezione n  608 pnl +1.7558 metro +1.5618
     solo bocciate: n  813 | apri tutto pnl +3.1146 metro +2.8849 | selezione n  812 pnl +3.1632 metro +2.9336
  finestra 3 [2026-04-18 -> 2026-08-10] train  5682 | soglia 0.40
     apri tutto: n 1420  pnl +4.3723  dd 0.5016  wr 64.6%  metro +3.8707
     selezione : n 1420  pnl +4.3723  dd 0.5016  wr 64.6%  metro +3.8707  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +3.8707)
     con size  : n 1420  pnl +4.9286  dd 0.5263  metro +4.4022  (informativo: il verdetto e' sulla selezione)
     solo passate : n  620 | apri tutto pnl +2.4373 metro +2.3008 | selezione n  620 pnl +2.4373 metro +2.3008
     solo bocciate: n  800 | apri tutto pnl +1.9350 metro +1.4958 | selezione n  800 pnl +1.9350 metro +1.4958
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 40997, lam 1.0, intercetta +0.716 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.192
    bb_pos     +0.082
    stop_pct   +0.077
    atr_pct    +0.071
    dist_ema   -0.054
    stoch_k    -0.044
    vol_ratio  -0.043
    regime_bull -0.034
    is_long    -0.029
    long_x_mercato -0.025
    adx        +0.022
    hour_sin   -0.014
    regime_incerto -0.014
    hour_cos   +0.013
    long_x_banda -0.011
    market_up  +0.008
    rsi        +0.007
    regime_bear -0.002
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore: questo e' il passo 1 (misura offline); il passo 2 (ombra nel bot) viene dopo, e solo con verdetto «batte».
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.
[selettore] fatto in 11.0s
```
