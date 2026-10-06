# 0516-6ott-mattina-selettore.req

_eseguito: 2026-10-06 06:13 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 98.8s

```
[selettore] 138267 trade da 927 file (826748 duplicati fusi, 1245046 gemelle fuse, 0 righe rotte saltate)
[selettore] 2177 coppie coin+strategia; famiglie: reversion 91836, momentum 44084, breakout 2347
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 138255 trade usabili (12 scartati: variabili mancanti), 67960 di spec passate e 70295 di bocciate, dal 2023-02-27 al 2026-08-21
  finestra 1 [2025-11-14 -> 2026-02-14] train 55302 | soglia 0.40
     apri tutto: n 27651  pnl +118.9220  dd 1.8147  wr 66.3%  metro +117.1073
     selezione : n 27651  pnl +118.9220  dd 1.8147  wr 66.3%  metro +117.1073  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +117.1073)
     con size  : n 27651  pnl +125.0355  dd 1.7246  metro +123.3109  (informativo: il verdetto e' sulla selezione)
     solo passate : n 15172 | apri tutto pnl +77.6432 metro +76.9600 | selezione n 15172 pnl +77.6432 metro +76.9600
     solo bocciate: n 12479 | apri tutto pnl +41.2788 metro +40.0135 | selezione n 12479 pnl +41.2788 metro +40.0135
  finestra 2 [2026-02-14 -> 2026-05-17] train 82953 | soglia 0.45
     apri tutto: n 27651  pnl +118.6762  dd 1.3709  wr 66.3%  metro +117.3053
     selezione : n 27650  pnl +118.7018  dd 1.3709  wr 66.3%  metro +117.3310  -> non batte (margine +0.0257, p_perm 0.195, 95° perc. +117.3477)
     con size  : n 27650  pnl +113.0877  dd 1.1769  metro +111.9109  (informativo: il verdetto e' sulla selezione)
     solo passate : n 15222 | apri tutto pnl +78.9129 metro +78.1694 | selezione n 15221 pnl +78.9386 metro +78.1950
     solo bocciate: n 12429 | apri tutto pnl +39.7633 metro +38.9198 | selezione n 12429 pnl +39.7633 metro +38.9198
  finestra 3 [2026-05-17 -> 2026-08-21] train 110604 | soglia 0.45
     apri tutto: n 27651  pnl +134.8979  dd 0.7425  wr 67.4%  metro +134.1554
     selezione : n 27651  pnl +134.8979  dd 0.7425  wr 67.4%  metro +134.1554  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +134.1554)
     con size  : n 27651  pnl +127.6043  dd 0.6789  metro +126.9254  (informativo: il verdetto e' sulla selezione)
     solo passate : n 15648 | apri tutto pnl +87.8721 metro +87.2121 | selezione n 15648 pnl +87.8721 metro +87.2121
     solo bocciate: n 12003 | apri tutto pnl +47.0258 metro +46.4874 | selezione n 12003 pnl +47.0258 metro +46.4874
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[reversion] 91824 trade usabili (12 scartati: variabili mancanti), 44346 di spec passate e 47478 di bocciate, dal 2023-02-27 al 2026-08-21
  finestra 1 [2025-11-18 -> 2026-02-16] train 36730 | soglia 0.45
     apri tutto: n 18365  pnl +76.8844  dd 2.5232  wr 66.4%  metro +74.3612
     selezione : n 18365  pnl +76.8844  dd 2.5232  wr 66.4%  metro +74.3612  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +74.3612)
     con size  : n 18365  pnl +74.7451  dd 2.2167  metro +72.5284  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10123 | apri tutto pnl +50.8113 metro +49.6566 | selezione n 10123 pnl +50.8113 metro +49.6566
     solo bocciate: n 8242 | apri tutto pnl +26.0731 metro +24.2818 | selezione n 8242 pnl +26.0731 metro +24.2818
  finestra 2 [2026-02-16 -> 2026-05-17] train 55095 | soglia 0.50
     apri tutto: n 18364  pnl +71.5130  dd 1.2073  wr 66.2%  metro +70.3057
     selezione : n 18352  pnl +71.6667  dd 1.2073  wr 66.2%  metro +70.4594  -> BATTE (margine +0.1536, p_perm 0.020, 95° perc. +70.4117)
     con size  : n 18352  pnl +62.5107  dd 0.9284  metro +61.5823  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10314 | apri tutto pnl +48.8391 metro +48.1025 | selezione n 10309 pnl +48.9344 metro +48.1978
     solo bocciate: n 8050 | apri tutto pnl +22.6740 metro +21.8937 | selezione n 8043 pnl +22.7323 metro +21.9520
  finestra 3 [2026-05-17 -> 2026-08-21] train 73459 | soglia 0.50
     apri tutto: n 18365  pnl +90.7931  dd 0.8417  wr 68.4%  metro +89.9514
     selezione : n 18352  pnl +90.6356  dd 0.8417  wr 68.4%  metro +89.7939  -> non batte (margine -0.1575, p_perm 0.850, 95° perc. +90.0514)
     con size  : n 18352  pnl +76.7174  dd 0.6498  metro +76.0675  (informativo: il verdetto e' sulla selezione)
     solo passate : n 10618 | apri tutto pnl +58.9495 metro +58.2828 | selezione n 10611 pnl +58.9276 metro +58.2609
     solo bocciate: n 7747 | apri tutto pnl +31.8436 metro +31.4052 | selezione n 7741 pnl +31.7081 metro +31.2697
  VERDETTO: NON BATTE (1/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[momentum] 44084 trade usabili, 21896 di spec passate e 22188 di bocciate, dal 2023-03-01 al 2026-08-21
  finestra 1 [2025-11-06 -> 2026-02-11] train 17634 | soglia 0.40
     apri tutto: n 8817  pnl +39.4245  dd 0.8567  wr 66.0%  metro +38.5677
     selezione : n 8817  pnl +39.4245  dd 0.8567  wr 66.0%  metro +38.5677  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +38.5677)
     con size  : n 8817  pnl +41.2092  dd 0.8777  metro +40.3315  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4722 | apri tutto pnl +25.0494 metro +24.2046 | selezione n 4722 pnl +25.0494 metro +24.2046
     solo bocciate: n 4095 | apri tutto pnl +14.3751 metro +13.8772 | selezione n 4095 pnl +14.3751 metro +13.8772
  finestra 2 [2026-02-11 -> 2026-05-16] train 26451 | soglia 0.50
     apri tutto: n 8816  pnl +46.1307  dd 0.7121  wr 67.2%  metro +45.4185
     selezione : n 8806  pnl +46.2103  dd 0.7121  wr 67.2%  metro +45.4982  -> non batte (margine +0.0796, p_perm 0.085, 95° perc. +45.5281)
     con size  : n 8806  pnl +38.4189  dd 0.6565  metro +37.7624  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4592 | apri tutto pnl +28.6556 metro +27.9070 | selezione n 4585 pnl +28.6825 metro +27.9340
     solo bocciate: n 4224 | apri tutto pnl +17.4751 metro +16.8988 | selezione n 4221 pnl +17.5278 metro +16.9515
  finestra 3 [2026-05-16 -> 2026-08-21] train 35267 | soglia 0.40
     apri tutto: n 8817  pnl +41.0870  dd 0.6020  wr 65.8%  metro +40.4850
     selezione : n 8817  pnl +41.0870  dd 0.6020  wr 65.8%  metro +40.4850  -> non batte (margine +0.0000, p_perm 1.000, 95° perc. +40.4850)
     con size  : n 8817  pnl +43.6072  dd 0.5992  metro +43.0080  (informativo: il verdetto e' sulla selezione)
     solo passate : n 4688 | apri tutto pnl +27.0181 metro +26.3361 | selezione n 4688 pnl +27.0181 metro +26.3361
     solo bocciate: n 4129 | apri tutto pnl +14.0689 metro +13.2901 | selezione n 4129 pnl +14.0689 metro +13.2901
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[breakout] 2347 trade usabili, 1718 di spec passate e 629 di bocciate, dal 2024-01-23 al 2026-08-21
  finestra 1 [2025-12-23 -> 2026-03-07] train   939 | soglia 0.50
     apri tutto: n  469  pnl +1.8923  dd 0.3292  wr 62.5%  metro +1.5631
     selezione : n  447  pnl +1.6395  dd 0.3090  wr 62.4%  metro +1.3306  -> non batte (margine -0.2325, p_perm 0.885, 95° perc. +1.7323)
     con size  : n  447  pnl +1.3069  dd 0.2561  metro +1.0509  (informativo: il verdetto e' sulla selezione)
     solo passate : n  317 | apri tutto pnl +1.9253 metro +1.6468 | selezione n  295 pnl +1.6725 metro +1.4143
     solo bocciate: n  152 | apri tutto pnl -0.0330 metro -0.2110 | selezione n  152 pnl -0.0330 metro -0.2110
  finestra 2 [2026-03-07 -> 2026-05-27] train  1408 | soglia 0.50
     apri tutto: n  470  pnl +2.6893  dd 0.3120  wr 64.5%  metro +2.3773
     selezione : n  430  pnl +1.7629  dd 0.3128  wr 64.2%  metro +1.4501  -> non batte (margine -0.9272, p_perm 1.000, 95° perc. +2.4314)
     con size  : n  430  pnl +1.3332  dd 0.2451  metro +1.0881  (informativo: il verdetto e' sulla selezione)
     solo passate : n  316 | apri tutto pnl +1.8693 metro +1.4475 | selezione n  280 pnl +0.9484 metro +0.5286
     solo bocciate: n  154 | apri tutto pnl +0.8200 metro +0.6134 | selezione n  150 pnl +0.8144 metro +0.6501
  finestra 3 [2026-05-27 -> 2026-08-21] train  1878 | soglia 0.45
     apri tutto: n  469  pnl +3.1634  dd 0.3847  wr 61.4%  metro +2.7788
     selezione : n  465  pnl +3.0610  dd 0.3847  wr 61.3%  metro +2.6763  -> non batte (margine -0.1024, p_perm 0.850, 95° perc. +2.9068)
     con size  : n  465  pnl +2.4165  dd 0.3086  metro +2.1079  (informativo: il verdetto e' sulla selezione)
     solo passate : n  319 | apri tutto pnl +2.4665 metro +2.1745 | selezione n  319 pnl +2.4665 metro +2.1745
     solo bocciate: n  150 | apri tutto pnl +0.6969 metro +0.4344 | selezione n  146 pnl +0.5945 metro +0.3320
  VERDETTO: NON BATTE (0/3 finestre; «batte» = sopra la baseline e sopra il 95° percentile di 200 permutazioni)

[modello «tutte»] n 138255, lam 1.0, intercetta +0.699 — coefficienti su variabili standardizzate, in ordine di modulo:
    r1         -0.218
    stop_pct   +0.069
    long_x_banda -0.062
    vol_ratio  -0.034
    bb_pos     +0.026
    dist_ema   -0.023
    is_long    -0.020
    hour_sin   -0.016
    rsi        -0.014
    hour_cos   +0.013
    regime_bull -0.010
    atr_pct    +0.010
    market_up  +0.007
    adx        -0.004
    long_x_mercato +0.001
    regime_bear -0.001
    stoch_k    +0.000
    regime_incerto -0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA (passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.

[firebase] pubblicato selector/current: modello su 138267 righe, soglia 0.45, verdetto NON BATTE, stato ombra.
[selettore] fatto in 97.0s
```
