# 0473-4ott-mattina-selettore.req

_eseguito: 2026-10-04 06:12 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 78.9s

```
[selettore] 126082 trade da 756 file (613073 duplicati fusi, 819524 gemelle fuse, 0 righe rotte saltate)
[selettore] 1915 coppie coin+strategia; famiglie: reversion 83093, momentum 39965, breakout 3024
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 126082 trade usabili, 61213 di spec passate e 64869 di bocciate, dal 2023-02-27 al 2026-08-19
  finestra 1 [2025-11-13 -> 2026-02-14] train 50433 | soglia 0.45
     apri tutto: n 25216  pnl +111.9426  dd 1.7509  wr 66.5%  metro +110.1917
     selezione : n 25215  pnl +111.9237  dd 1.7509  wr 66.5%  metro +110.1728  -> non batte (margine -0.0189, p_perm 0.770, 95° perc. +110.2307)
     con size  : n 25215  pnl +106.6156  dd 1.4643  metro +105.1513  (informativo: il verdetto e' sulla selezione)
     solo passate : n 13769 | apri tutto pnl +72.1852 metro +71.5689 | selezione n 13769 pnl +72.1852 metro +71.5689
     solo bocciate: n 11447 | apri tutto pnl +39.7574 metro +38.5250 | selezione n 11446 pnl +39.7385 metro +38.5061
  finestra 2 [2026-02-14 -> 2026-05-16] train 75649 | soglia 0.40
     apri tutto: n 25217  pnl +109.3359  dd 1.3450  wr 66.3%  metro +107.9909
     selezione : n 25217  pnl +109.3359  dd 1.3450  wr 66.3%  metro +107.9909  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +107.9909)
     con size  : n 25217  pnl +115.0229  dd 1.2893  metro +113.7336  (informativo: il verdetto e' sulla selezione)
     solo passate : n 13826 | apri tutto pnl +71.6033 metro +70.9745 | selezione n 13826 pnl +71.6033 metro +70.9745
     solo bocciate: n 11391 | apri tutto pnl +37.7326 metro +36.9409 | selezione n 11391 pnl +37.7326 metro +36.9409
  finestra 3 [2026-05-16 -> 2026-08-19] train 100866 | soglia 0.40
     apri tutto: n 25216  pnl +123.3238  dd 0.7604  wr 67.4%  metro +122.5634
     selezione : n 25216  pnl +123.3238  dd 0.7604  wr 67.4%  metro +122.5634  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +122.5634)
     con size  : n 25216  pnl +129.7377  dd 0.7105  metro +129.0272  (informativo: il verdetto e' sulla selezione)
     solo passate : n 14170 | apri tutto pnl +80.3738 metro +79.7992 | selezione n 14170 pnl +80.3738 metro +79.7992
     solo bocciate: n 11046 | apri tutto pnl +42.9500 metro +42.3589 | selezione n 11046 pnl +42.9500 metro +42.3589
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 83093 trade usabili, 39595 di spec passate e 43498 di bocciate, dal 2023-02-27 al 2026-08-19
  finestra 1 [2025-11-18 -> 2026-02-15] train 33237 | soglia 0.40
     apri tutto: n 16619  pnl +72.3454  dd 2.3789  wr 66.5%  metro +69.9665
     selezione : n 16619  pnl +72.3454  dd 2.3789  wr 66.5%  metro +69.9665  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +69.9665)
     con size  : n 16619  pnl +76.6546  dd 2.2782  metro +74.3764  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9172 | apri tutto pnl +46.7719 metro +45.8079 | selezione n 9172 pnl +46.7719 metro +45.8079
     solo bocciate: n 7447 | apri tutto pnl +25.5735 metro +23.8512 | selezione n 7447 pnl +25.5735 metro +23.8512
  finestra 2 [2026-02-15 -> 2026-05-16] train 49856 | soglia 0.50
     apri tutto: n 16618  pnl +65.3867  dd 1.2752  wr 66.2%  metro +64.1115
     selezione : n 16607  pnl +65.5225  dd 1.2752  wr 66.3%  metro +64.2473  -> BATTE (margine +0.1358, p_perm 0.035, 95° perc. +64.2045)
     con size  : n 16607  pnl +57.2368  dd 1.0478  metro +56.1890  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9355 | apri tutto pnl +44.9080 metro +44.1655 | selezione n 9351 pnl +44.9631 metro +44.2206
     solo bocciate: n 7263 | apri tutto pnl +20.4787 metro +19.7410 | selezione n 7256 pnl +20.5594 metro +19.8217
  finestra 3 [2026-05-16 -> 2026-08-19] train 66474 | soglia 0.50
     apri tutto: n 16619  pnl +82.3549  dd 0.8226  wr 68.3%  metro +81.5323
     selezione : n 16608  pnl +82.3192  dd 0.8226  wr 68.3%  metro +81.4966  -> non batte (margine -0.0357, p_perm 0.440, 95° perc. +81.5996)
     con size  : n 16608  pnl +70.3870  dd 0.6104  metro +69.7766  (informativo: il verdetto e' sulla selezione)
     solo passate : n 9613 | apri tutto pnl +53.5512 metro +52.8177 | selezione n 9607 pnl +53.6058 metro +52.8723
     solo bocciate: n 7006 | apri tutto pnl +28.8037 metro +28.2934 | selezione n 7001 pnl +28.7134 metro +28.2031
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 39965 trade usabili, 19132 di spec passate e 20833 di bocciate, dal 2023-03-01 al 2026-08-19
  finestra 1 [2025-11-05 -> 2026-02-10] train 15986 | soglia 0.40
     apri tutto: n 7993  pnl +36.2769  dd 0.7562  wr 65.8%  metro +35.5207
     selezione : n 7993  pnl +36.2769  dd 0.7562  wr 65.8%  metro +35.5207  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +35.5207)
     con size  : n 7993  pnl +37.4835  dd 0.7553  metro +36.7282  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4133 | apri tutto pnl +22.4839 metro +21.8913 | selezione n 4133 pnl +22.4839 metro +21.8913
     solo bocciate: n 3860 | apri tutto pnl +13.7930 metro +13.2832 | selezione n 3860 pnl +13.7930 metro +13.2832
  finestra 2 [2026-02-10 -> 2026-05-15] train 23979 | soglia 0.50
     apri tutto: n 7993  pnl +40.5874  dd 0.7322  wr 66.8%  metro +39.8552
     selezione : n 7992  pnl +40.6360  dd 0.7322  wr 66.8%  metro +39.9039  -> BATTE (margine +0.0486, p_perm 0.035, 95° perc. +39.8943)
     con size  : n 7992  pnl +34.1716  dd 0.6495  metro +33.5221  (informativo: il verdetto e' sulla selezione)
     solo passate : n 3979 | apri tutto pnl +23.4961 metro +22.9333 | selezione n 3979 pnl +23.4961 metro +22.9333
     solo bocciate: n 4014 | apri tutto pnl +17.0913 metro +16.5060 | selezione n 4013 pnl +17.1400 metro +16.5546
  finestra 3 [2026-05-15 -> 2026-08-19] train 31972 | soglia 0.40
     apri tutto: n 7993  pnl +36.4558  dd 0.7840  wr 65.6%  metro +35.6717
     selezione : n 7993  pnl +36.4558  dd 0.7840  wr 65.6%  metro +35.6717  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +35.6717)
     con size  : n 7993  pnl +38.4996  dd 0.7545  metro +37.7451  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4089 | apri tutto pnl +22.5945 metro +22.0507 | selezione n 4089 pnl +22.5945 metro +22.0507
     solo bocciate: n 3904 | apri tutto pnl +13.8613 metro +13.1150 | selezione n 3904 pnl +13.8613 metro +13.1150
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 3024 trade usabili, 2486 di spec passate e 538 di bocciate, dal 2024-01-14 al 2026-08-19
  finestra 1 [2025-12-07 -> 2026-02-26] train  1210 | soglia 0.45
     apri tutto: n  605  pnl +2.4782  dd 0.4015  wr 65.1%  metro +2.0767
     selezione : n  594  pnl +2.5878  dd 0.4015  wr 65.7%  metro +2.1862  -> non batte (margine +0.1096, p_perm 0.075, 95° perc. +2.2240)
     con size  : n  594  pnl +2.6281  dd 0.4187  metro +2.2094  (informativo: il verdetto e' sulla selezione)
     solo passate : n  455 | apri tutto pnl +2.0483 metro +1.4845 | selezione n  445 pnl +2.2030 metro +1.6580
     solo bocciate: n  150 | apri tutto pnl +0.4299 metro +0.2429 | selezione n  149 pnl +0.3848 metro +0.1978
  finestra 2 [2026-02-26 -> 2026-05-19] train  1815 | soglia 0.45
     apri tutto: n  604  pnl +3.8535  dd 0.5362  wr 67.2%  metro +3.3173
     selezione : n  587  pnl +3.6973  dd 0.5580  wr 67.6%  metro +3.1394  -> non batte (margine -0.1779, p_perm 0.705, 95° perc. +3.4800)
     con size  : n  587  pnl +3.4338  dd 0.4804  metro +2.9534  (informativo: il verdetto e' sulla selezione)
     solo passate : n  478 | apri tutto pnl +3.2337 metro +2.6698 | selezione n  468 pnl +3.1001 metro +2.5371
     solo bocciate: n  126 | apri tutto pnl +0.6197 metro +0.4466 | selezione n  119 pnl +0.5972 metro +0.4241
  finestra 3 [2026-05-19 -> 2026-08-19] train  2419 | soglia 0.40
     apri tutto: n  605  pnl +5.1492  dd 0.3888  wr 66.6%  metro +4.7604
     selezione : n  605  pnl +5.1492  dd 0.3888  wr 66.6%  metro +4.7604  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +4.7604)
     con size  : n  605  pnl +4.9442  dd 0.4023  metro +4.5419  (informativo: il verdetto e' sulla selezione)
     solo passate : n  456 | apri tutto pnl +4.6918 metro +4.3778 | selezione n  456 pnl +4.6918 metro +4.3778
     solo bocciate: n  149 | apri tutto pnl +0.4575 metro +0.1623 | selezione n  149 pnl +0.4575 metro +0.1623
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 126082, lam 1.0, intercetta +0.697 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.213
    stop_pct   +0.070
    long_x_banda -0.063
    bb_pos     +0.039
    vol_ratio  -0.033
    dist_ema   -0.027
    rsi        -0.020
    is_long    -0.018
    hour_sin   -0.016
    hour_cos   +0.012
    atr_pct    +0.012
    regime_bull -0.011
    market_up  +0.008
    regime_bear -0.006
    stoch_k    -0.006
    regime_incerto -0.005
    adx        -0.002
    long_x_mercato -0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 126082 righe, soglia 0.40, verdetto NON BATTE, stato ombra.
[selettore] fatto in 77.2s
```
