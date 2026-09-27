# 0301-controllo-27set-selettore.req

_eseguito: 2026-09-27 06:24 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 25.5s

```
[selettore] 68151 trade da 120 file (95557 duplicati fusi, 145198 gemelle fuse, 0 righe rotte saltate)
[selettore] 996 coppie coin+strategia; famiglie: reversion 51428, momentum 16265, breakout 458
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 68151 trade usabili, 26658 di spec passate e 41493 di bocciate, dal 2023-02-27 al 2026-08-12
  finestra 1 [2025-11-01 -> 2026-02-06] train 27260 | soglia 0.50
     apri tutto: n 13630  pnl +60.6300  dd 1.5748  wr 66.8%  metro +59.0552
     selezione : n 13621  pnl +60.6144  dd 1.5682  wr 66.9%  metro +59.0462  -> non batte (margine -0.0090, p_perm 0.335, 95° perc. +59.1382)
     con size  : n 13621  pnl +50.8309  dd 1.2765  metro +49.5544  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6036 | apri tutto pnl +32.8385 metro +32.0231 | selezione n 6028 pnl +32.8164 metro +32.0009
     solo bocciate: n 7594 | apri tutto pnl +27.7915 metro +26.9616 | selezione n 7593 pnl +27.7981 metro +26.9748
  finestra 2 [2026-02-06 -> 2026-05-10] train 40890 | soglia 0.50
     apri tutto: n 13631  pnl +57.2733  dd 0.7478  wr 66.5%  metro +56.5255
     selezione : n 13620  pnl +57.2906  dd 0.7478  wr 66.5%  metro +56.5428  -> non batte (margine +0.0173, p_perm 0.220, 95° perc. +56.6044)
     con size  : n 13620  pnl +49.2172  dd 0.5572  metro +48.6600  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5953 | apri tutto pnl +29.8007 metro +29.3132 | selezione n 5949 pnl +29.8497 metro +29.3622
     solo bocciate: n 7678 | apri tutto pnl +27.4726 metro +26.9765 | selezione n 7671 pnl +27.4409 metro +26.9448
  finestra 3 [2026-05-10 -> 2026-08-12] train 54521 | soglia 0.50
     apri tutto: n 13630  pnl +65.9303  dd 0.5555  wr 67.4%  metro +65.3747
     selezione : n 13628  pnl +65.9351  dd 0.5555  wr 67.4%  metro +65.3796  -> non batte (margine +0.0049, p_perm 0.345, 95° perc. +65.4225)
     con size  : n 13628  pnl +57.6167  dd 0.4742  metro +57.1425  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6167 | apri tutto pnl +35.8431 metro +35.3909 | selezione n 6166 pnl +35.8364 metro +35.3842
     solo bocciate: n 7463 | apri tutto pnl +30.0871 metro +29.4272 | selezione n 7462 pnl +30.0987 metro +29.4388
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 51428 trade usabili, 21395 di spec passate e 30033 di bocciate, dal 2023-02-27 al 2026-08-12
  finestra 1 [2025-11-02 -> 2026-02-05] train 20571 | soglia 0.40
     apri tutto: n 10286  pnl +46.7693  dd 1.8103  wr 67.4%  metro +44.9590
     selezione : n 10286  pnl +46.7693  dd 1.8103  wr 67.4%  metro +44.9590  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +44.9590)
     con size  : n 10286  pnl +48.8425  dd 1.8244  metro +47.0181  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5000 | apri tutto pnl +27.0552 metro +26.2384 | selezione n 5000 pnl +27.0552 metro +26.2384
     solo bocciate: n 5286 | apri tutto pnl +19.7141 metro +18.6585 | selezione n 5286 pnl +19.7141 metro +18.6585
  finestra 2 [2026-02-05 -> 2026-05-09] train 30857 | soglia 0.50
     apri tutto: n 10285  pnl +42.9606  dd 0.6956  wr 66.8%  metro +42.2650
     selezione : n 10267  pnl +43.1587  dd 0.6526  wr 66.9%  metro +42.5061  -> BATTE (margine +0.2411, p_perm 0.005, 95° perc. +42.3379)
     con size  : n 10267  pnl +37.8947  dd 0.4798  metro +37.4148  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5081 | apri tutto pnl +26.0650 metro +25.5737 | selezione n 5076 pnl +26.1057 metro +25.6145
     solo bocciate: n 5204 | apri tutto pnl +16.8956 metro +16.3439 | selezione n 5191 pnl +17.0529 metro +16.5012
  finestra 3 [2026-05-09 -> 2026-08-12] train 41142 | soglia 0.50
     apri tutto: n 10286  pnl +49.8064  dd 0.7274  wr 68.1%  metro +49.0791
     selezione : n 10269  pnl +49.6342  dd 0.7274  wr 68.1%  metro +48.9068  -> non batte (margine -0.1722, p_perm 0.850, 95° perc. +49.1540)
     con size  : n 10269  pnl +43.5143  dd 0.6327  metro +42.8816  (informativo: il verdetto e' sulla selezione)
     solo passate : n 5343 | apri tutto pnl +31.4848 metro +31.0527 | selezione n 5335 pnl +31.4729 metro +31.0408
     solo bocciate: n 4943 | apri tutto pnl +18.3216 metro +17.8928 | selezione n 4934 pnl +18.1613 metro +17.7325
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 16265 trade usabili, 4805 di spec passate e 11460 di bocciate, dal 2023-03-01 al 2026-08-12
  finestra 1 [2025-11-02 -> 2026-02-10] train  6506 | soglia 0.40
     apri tutto: n 3253  pnl +11.9833  dd 0.6068  wr 64.7%  metro +11.3766
     selezione : n 3253  pnl +11.9833  dd 0.6068  wr 64.7%  metro +11.3766  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +11.3766)
     con size  : n 3253  pnl +12.3773  dd 0.6492  metro +11.7282  (informativo: il verdetto e' sulla selezione)
     solo passate : n  934 | apri tutto pnl +4.5807 metro +4.3894 | selezione n  934 pnl +4.5807 metro +4.3894
     solo bocciate: n 2319 | apri tutto pnl +7.4027 metro +6.8907 | selezione n 2319 pnl +7.4027 metro +6.8907
  finestra 2 [2026-02-10 -> 2026-05-15] train  9759 | soglia 0.55
     apri tutto: n 3253  pnl +15.0971  dd 0.4439  wr 66.4%  metro +14.6532
     selezione : n 3245  pnl +15.0325  dd 0.4254  wr 66.3%  metro +14.6071  -> non batte (margine -0.0460, p_perm 0.565, 95° perc. +14.7440)
     con size  : n 3245  pnl +11.1511  dd 0.3250  metro +10.8261  (informativo: il verdetto e' sulla selezione)
     solo passate : n  807 | apri tutto pnl +3.3822 metro +3.1925 | selezione n  805 pnl +3.3635 metro +3.1739
     solo bocciate: n 2446 | apri tutto pnl +11.7149 metro +11.1357 | selezione n 2440 pnl +11.6690 metro +11.0898
  finestra 3 [2026-05-15 -> 2026-08-12] train 13012 | soglia 0.40
     apri tutto: n 3253  pnl +14.9429  dd 0.5006  wr 64.6%  metro +14.4423
     selezione : n 3253  pnl +14.9429  dd 0.5006  wr 64.6%  metro +14.4423  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +14.4423)
     con size  : n 3253  pnl +16.0764  dd 0.5194  metro +15.5569  (informativo: il verdetto e' sulla selezione)
     solo passate : n  786 | apri tutto pnl +4.2243 metro +4.0372 | selezione n  786 pnl +4.2243 metro +4.0372
     solo bocciate: n 2467 | apri tutto pnl +10.7186 metro +10.1710 | selezione n 2467 pnl +10.7186 metro +10.1710
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 458 trade usabili, dal 2024-01-23 al 2026-08-10
  finestra 1: train 183 trade < minimo -> campione insufficiente
  finestra 2: train 275 trade < minimo -> campione insufficiente
  finestra 3: train 366 trade < minimo -> campione insufficiente
  VERDETTO: CAMPIONE INSUFFICIENTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 68151, lam 1.0, intercetta +0.709 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.209
    bb_pos     +0.061
    atr_pct    +0.058
    is_long    -0.049
    dist_ema   -0.048
    stop_pct   +0.047
    stoch_k    -0.033
    vol_ratio  -0.031
    long_x_banda -0.030
    rsi        -0.022
    long_x_mercato -0.022
    hour_sin   -0.017
    regime_bull -0.013
    regime_bear +0.009
    regime_incerto +0.004
    hour_cos   +0.001
    adx        +0.001
    market_up  -0.001
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 68151 righe, soglia 0.50, verdetto NON BATTE, stato ombra.
[selettore] fatto in 24.2s
```
