# 0368-30set-selettore.req

_eseguito: 2026-09-30 06:17 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 45.6s

```
[selettore] 92257 trade da 392 file (250438 duplicati fusi, 299127 gemelle fuse, 0 righe rotte saltate)
[selettore] 1314 coppie coin+strategia; famiglie: reversion 64576, momentum 26339, breakout 1342
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 92257 trade usabili, 38701 di spec passate e 53556 di bocciate, dal 2023-02-27 al 2026-08-15
  finestra 1 [2025-11-05 -> 2026-02-08] train 36903 | soglia 0.50
     apri tutto: n 18451  pnl +80.5577  dd 1.9086  wr 66.3%  metro +78.6491
     selezione : n 18448  pnl +80.5341  dd 1.9086  wr 66.3%  metro +78.6255  -> non batte (margine -0.0237, p_perm 0.665, 95° perc. +78.7057)
     con size  : n 18448  pnl +66.9450  dd 1.4941  metro +65.4508  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8616 | apri tutto pnl +43.3829 metro +42.5676 | selezione n 8614 pnl +43.3831 metro +42.5678
     solo bocciate: n 9835 | apri tutto pnl +37.1748 metro +36.0592 | selezione n 9834 pnl +37.1510 metro +36.0354
  finestra 2 [2026-02-08 -> 2026-05-12] train 55354 | soglia 0.45
     apri tutto: n 18452  pnl +78.8284  dd 0.8772  wr 66.4%  metro +77.9513
     selezione : n 18452  pnl +78.8284  dd 0.8772  wr 66.4%  metro +77.9513  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +77.9513)
     con size  : n 18452  pnl +74.3855  dd 0.7431  metro +73.6425  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8561 | apri tutto pnl +43.7661 metro +43.2089 | selezione n 8561 pnl +43.7661 metro +43.2089
     solo bocciate: n 9891 | apri tutto pnl +35.0623 metro +34.3250 | selezione n 9891 pnl +35.0623 metro +34.3250
  finestra 3 [2026-05-12 -> 2026-08-15] train 73806 | soglia 0.40
     apri tutto: n 18451  pnl +87.4150  dd 0.6934  wr 66.6%  metro +86.7216
     selezione : n 18451  pnl +87.4150  dd 0.6934  wr 66.6%  metro +86.7216  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +86.7216)
     con size  : n 18451  pnl +91.8799  dd 0.7004  metro +91.1795  (informativo: il verdetto e' sulla selezione)
     solo passate : n 8856 | apri tutto pnl +47.8136 metro +47.3817 | selezione n 8856 pnl +47.8136 metro +47.3817
     solo bocciate: n 9595 | apri tutto pnl +39.6014 metro +39.1453 | selezione n 9595 pnl +39.6014 metro +39.1453
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 64576 trade usabili, 28349 di spec passate e 36227 di bocciate, dal 2023-02-27 al 2026-08-15
  finestra 1 [2025-11-09 -> 2026-02-09] train 25830 | soglia 0.40
     apri tutto: n 12915  pnl +55.4446  dd 2.1813  wr 66.7%  metro +53.2633
     selezione : n 12915  pnl +55.4446  dd 2.1813  wr 66.7%  metro +53.2633  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +53.2633)
     con size  : n 12915  pnl +58.2134  dd 2.1652  metro +56.0482  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6555 | apri tutto pnl +32.1040 metro +31.2207 | selezione n 6555 pnl +32.1040 metro +31.2207
     solo bocciate: n 6360 | apri tutto pnl +23.3406 metro +21.8496 | selezione n 6360 pnl +23.3406 metro +21.8496
  finestra 2 [2026-02-09 -> 2026-05-13] train 38745 | soglia 0.40
     apri tutto: n 12916  pnl +52.3090  dd 0.7918  wr 66.4%  metro +51.5172
     selezione : n 12916  pnl +52.3090  dd 0.7918  wr 66.4%  metro +51.5172  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +51.5172)
     con size  : n 12916  pnl +55.3087  dd 0.7374  metro +54.5713  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6745 | apri tutto pnl +33.3903 metro +32.7611 | selezione n 6745 pnl +33.3903 metro +32.7611
     solo bocciate: n 6171 | apri tutto pnl +18.9187 metro +18.2062 | selezione n 6171 pnl +18.9187 metro +18.2062
  finestra 3 [2026-05-13 -> 2026-08-15] train 51661 | soglia 0.50
     apri tutto: n 12915  pnl +60.7861  dd 0.7625  wr 67.6%  metro +60.0236
     selezione : n 12896  pnl +60.5759  dd 0.7625  wr 67.6%  metro +59.8134  -> non batte (margine -0.2102, p_perm 0.885, 95° perc. +60.1176)
     con size  : n 12896  pnl +51.7771  dd 0.6495  metro +51.1276  (informativo: il verdetto e' sulla selezione)
     solo passate : n 6999 | apri tutto pnl +36.8399 metro +36.3257 | selezione n 6989 pnl +36.7789 metro +36.2647
     solo bocciate: n 5916 | apri tutto pnl +23.9461 metro +23.3722 | selezione n 5907 pnl +23.7969 metro +23.2230
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 26339 trade usabili, 9556 di spec passate e 16783 di bocciate, dal 2023-03-01 al 2026-08-15
  finestra 1 [2025-10-22 -> 2026-02-03] train 10536 | soglia 0.40
     apri tutto: n 5268  pnl +22.2811  dd 0.5993  wr 64.9%  metro +21.6818
     selezione : n 5268  pnl +22.2811  dd 0.5993  wr 64.9%  metro +21.6818  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +21.6818)
     con size  : n 5268  pnl +22.8228  dd 0.6069  metro +22.2158  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1924 | apri tutto pnl +9.5621 metro +9.1960 | selezione n 1924 pnl +9.5621 metro +9.1960
     solo bocciate: n 3344 | apri tutto pnl +12.7190 metro +12.2005 | selezione n 3344 pnl +12.7190 metro +12.2005
  finestra 2 [2026-02-03 -> 2026-05-10] train 15804 | soglia 0.50
     apri tutto: n 5267  pnl +25.4272  dd 0.5386  wr 66.0%  metro +24.8886
     selezione : n 5267  pnl +25.4272  dd 0.5386  wr 66.0%  metro +24.8886  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +24.8886)
     con size  : n 5267  pnl +21.0319  dd 0.4620  metro +20.5699  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1659 | apri tutto pnl +9.9670 metro +9.6475 | selezione n 1659 pnl +9.9670 metro +9.6475
     solo bocciate: n 3608 | apri tutto pnl +15.4602 metro +14.8192 | selezione n 3608 pnl +15.4602 metro +14.8192
  finestra 3 [2026-05-10 -> 2026-08-15] train 21071 | soglia 0.45
     apri tutto: n 5268  pnl +25.6820  dd 0.5836  wr 64.7%  metro +25.0984
     selezione : n 5268  pnl +25.6820  dd 0.5836  wr 64.7%  metro +25.0984  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +25.0984)
     con size  : n 5268  pnl +24.5535  dd 0.5412  metro +24.0122  (informativo: il verdetto e' sulla selezione)
     solo passate : n 1712 | apri tutto pnl +10.3668 metro +10.0311 | selezione n 1712 pnl +10.3668 metro +10.0311
     solo bocciate: n 3556 | apri tutto pnl +15.3152 metro +14.6470 | selezione n 3556 pnl +15.3152 metro +14.6470
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 1342 trade usabili, 796 di spec passate e 546 di bocciate, dal 2024-01-23 al 2026-08-13
  finestra 1 [2025-12-11 -> 2026-03-03] train   537 | soglia 0.55
     apri tutto: n  268  pnl +0.8155  dd 0.2730  wr 61.6%  metro +0.5425
     selezione : n  233  pnl +0.7726  dd 0.2424  wr 62.2%  metro +0.5303  -> non batte (margine -0.0122, p_perm 0.420, 95° perc. +0.7405)
     con size  : n  233  pnl +0.6326  dd 0.1359  metro +0.4966  (informativo: il verdetto e' sulla selezione)
     solo passate : n  116 | apri tutto pnl +0.4391 metro +0.2179 | selezione n  103 pnl +0.4821 metro +0.2916
     solo bocciate: n  152 | apri tutto pnl +0.3764 metro +0.1895 | selezione n  130 pnl +0.2905 metro +0.1264
  finestra 2 [2026-03-04 -> 2026-05-22] train   805 | soglia 0.60
     apri tutto: n  269  pnl +1.9012  dd 0.1745  wr 68.4%  metro +1.7267
     selezione : n  152  pnl +1.2160  dd 0.1181  wr 71.0%  metro +1.0979  -> non batte (margine -0.6287, p_perm 0.240, 95° perc. +1.3060)
     con size  : n  152  pnl +0.7979  dd 0.0771  metro +0.7208  (informativo: il verdetto e' sulla selezione)
     solo passate : n  143 | apri tutto pnl +1.2152 metro +1.0727 | selezione n   81 pnl +0.6399 metro +0.5298
     solo bocciate: n  126 | apri tutto pnl +0.6860 metro +0.5018 | selezione n   71 pnl +0.5761 metro +0.4365
  finestra 3 [2026-05-22 -> 2026-08-13] train  1074 | soglia 0.40
     apri tutto: n  268  pnl +0.8407  dd 0.2429  wr 57.5%  metro +0.5978
     selezione : n  265  pnl +0.7579  dd 0.2429  wr 57.4%  metro +0.5150  -> non batte (margine -0.0827, p_perm 0.860, 95° perc. +0.6983)
     con size  : n  265  pnl +0.7231  dd 0.2433  metro +0.4798  (informativo: il verdetto e' sulla selezione)
     solo passate : n  123 | apri tutto pnl +0.3833 metro +0.1292 | selezione n  123 pnl +0.3833 metro +0.1292
     solo bocciate: n  145 | apri tutto pnl +0.4574 metro +0.1622 | selezione n  142 pnl +0.3746 metro +0.0795
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 92257, lam 1.0, intercetta +0.686 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.197
    bb_pos     +0.055
    stop_pct   +0.048
    long_x_banda -0.047
    atr_pct    +0.041
    is_long    -0.033
    dist_ema   -0.032
    rsi        -0.029
    vol_ratio  -0.029
    stoch_k    -0.016
    hour_sin   -0.015
    market_up  +0.015
    regime_bull -0.014
    regime_incerto -0.011
    long_x_mercato -0.008
    hour_cos   +0.004
    regime_bear -0.003
    adx        +0.002
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 92257 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 44.3s
```
