# 0394-1ott-mfe.req

_eseguito: 2026-10-01 06:13 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 7.6s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 204 · con mfe_r registrato: 204
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 81 trade su 204 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             204     0.87    70%    43%    16%     7%     2%     1%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_fa304106                         7     0.10    43%     0%     0%     0%     0%     0%     0%
gen_cd5c842f                         7     1.10    86%    71%    29%    29%    14%    14%    14%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_4465723e                         6     1.36   100%    50%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_ba3a671f                         6     0.33    33%    17%     0%     0%     0%     0%     0%
gen_18c839a0                         5     0.91    80%    40%    20%    20%     0%     0%     0%
gen_bb762669                         5     0.79   100%    40%    20%     0%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e59ad90b                         4     0.87    75%    25%    25%    25%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_4c6df481                         4     1.30    50%    50%    25%    25%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%
gen_bf1e00d4                         4     0.90    75%    25%    25%    25%    25%    25%     0%
gen_771790b1                         3     1.32    67%    67%    33%     0%     0%     0%     0%
gen_f3661202                         3     0.77    67%    33%     0%     0%     0%     0%     0%
gen_c5194ce4                         3     0.05    33%    33%     0%     0%     0%     0%     0%
gen_a640dfa5                         3     1.09   100%   100%     0%     0%     0%     0%     0%
gen_35632db9                         3     0.84    67%    33%     0%     0%     0%     0%     0%
gen_f3124a14                         3     0.58    67%    33%    33%    33%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (88 su 204 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  41   47%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  46   52%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.59R, massima 1.23R; con un primo gradino a 0.59R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             204      -0.350 *      -0.381        -0.745        -0.873  
gen_fca11c08                        14      -0.689        -0.679 *      -0.896        -0.886  
gen_fa304106                         7      -1.000 *      -1.000        -1.000        -1.000  
gen_cd5c842f                         7      +0.200        +0.271 *      -0.171        -0.371  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000  
gen_490a90e5                         7      -0.814 *      -0.814        -1.000        -1.000  
gen_4465723e                         6      -0.275 *      -0.350        -0.758        -1.000  
gen_6d06dca0                         6      -0.200 *      -0.350        -0.517        -1.000  
gen_ba3a671f                         6      -0.783 *      -0.783        -1.000        -1.000  
gen_18c839a0                         5      -0.390        -0.360 *      -0.710        -0.680  
gen_bb762669                         5      -0.390 *      -0.480        -0.710        -1.000  
gen_f238d283                         5      -0.040        +0.020 *      -0.420        -0.360  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000  
gen_e59ad90b                         4      -0.562        -0.525 *      -0.637        -0.600  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_4c6df481                         4      -0.237        -0.200 *      -0.637        -0.600  
gen_b31d8b93                         4      -0.237        -0.200 *      -0.637        -0.600  
gen_bf1e00d4                         4      -0.312        -0.225 *      -0.413        -0.300  
gen_771790b1                         3      +0.017 *      -0.133        -0.517        -1.000  
gen_f3661202                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_c5194ce4                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_a640dfa5                         3      +0.300 *      +0.300        -1.000        -1.000  
gen_35632db9                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_f3124a14                         3      -0.083 *      -0.367        -0.517        -0.467  
gen_b9bf5d01                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_af734c68                         3      -0.567 *      -0.567        -1.000        -1.000  

(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misurare)
  livello = massimo (long) / minimo (short) delle ultime 96 candele a 15m
  oltre il prezzo d'ingresso (192 se in 96 non c'e' niente), in R dello stop.
[backtest] cache ESTESA di 193 candele (invece di riscaricarne 601) (PNUTUSDT 15m)
[backtest] cache ESTESA di 217 candele (invece di riscaricarne 601) (PHAUSDT 15m)
[backtest] cache ESTESA di 97 candele (invece di riscaricarne 697) (HEMIUSDT 15m)
[backtest] cache ESTESA di 169 candele (invece di riscaricarne 1633) (SYRUPUSDT 15m)
[backtest] dati da cache: 505 candele (UBUSDT 15m)
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 1249) (QUSDT 15m)
[backtest] cache ESTESA di 193 candele (invece di riscaricarne 865) (HUMAUSDT 15m)
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 865) (SUIUSDT 15m)
[backtest] cache ESTESA di 193 candele (invece di riscaricarne 1537) (TUTUSDT 15m)
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 1057) (DOTUSDT 15m)
[backtest] cache ESTESA di 169 candele (invece di riscaricarne 1249) (MUBARAKUSDT 15m)
[backtest] dati da binance: 769 candele
[backtest] dati da binance: 1441 candele
[backtest] dati da cache: 313 candele (AIOUSDT 15m)
[backtest] dati da cache: 673 candele (SEIUSDT 15m)
[backtest] dati da cache: 769 candele (XPLUSDT 15m)
[backtest] dati da cache: 385 candele (RAYSOLUSDT 15m)
[backtest] dati da cache: 505 candele (JUPUSDT 15m)
[backtest] dati da cache: 385 candele (GALAUSDT 15m)
[backtest] dati da cache: 385 candele (AXSUSDT 15m)
[backtest] dati da cache: 409 candele (FLOCKUSDT 15m)
[backtest] dati da cache: 385 candele (OPENUSDT 15m)
[backtest] dati da cache: 601 candele (THEUSDT 15m)
[backtest] dati da cache: 1369 candele (ORCAUSDT 15m)
[backtest] dati da cache: 1369 candele (GPSUSDT 15m)
[backtest] dati da cache: 1273 candele (PROMUSDT 15m)
[backtest] dati da cache: 1561 candele (SPXUSDT 15m)
[backtest] dati da cache: 313 candele (BTRUSDT 15m)
[backtest] dati da cache: 481 candele (AVAAIUSDT 15m)
[backtest] dati da cache: 481 candele (TRUMPUSDT 15m)
[backtest] dati da cache: 385 candele (STEEMUSDT 15m)
[backtest] dati da cache: 673 candele (ENAUSDT 15m)
[backtest] dati da cache: 769 candele (BULLAUSDT 15m)
[backtest] dati da cache: 1057 candele (USELESSUSDT 15m)
[backtest] dati da cache: 385 candele (EPICUSDT 15m)
[backtest] dati da cache: 481 candele (BANKUSDT 15m)
[backtest] dati da cache: 577 candele (TAUSDT 15m)
[backtest] dati da cache: 577 candele (SKYAIUSDT 15m)
[backtest] dati da cache: 385 candele (TSTUSDT 15m)
[backtest] dati da cache: 577 candele (ZORAUSDT 15m)
[backtest] dati da cache: 577 candele (XMRUSDT 15m)
[backtest] dati da cache: 385 candele (SOLUSDT 15m)
[backtest] dati da cache: 385 candele (XRPUSDT 15m)
[backtest] dati da cache: 1249 candele (DEXEUSDT 15m)
[backtest] dati da binance: 1249 candele
[backtest] dati da cache: 385 candele (ATOMUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 1249 candele
[backtest] dati da cache: 385 candele (SAHARAUSDT 15m)
[backtest] dati da cache: 481 candele (JTOUSDT 15m)
[backtest] dati da cache: 385 candele (RENDERUSDT 15m)
[backtest] dati da cache: 481 candele (HEIUSDT 15m)
[backtest] dati da cache: 385 candele (ZKUSDT 15m)
[backtest] dati da cache: 577 candele (BICOUSDT 15m)

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
FLOCKUSDT   gen_c5194ce4            short   0.75   2.16   0.05   no    no    no 
SYRUPUSDT   gen_98d56766            short   1.50   4.74   0.49   no    no    no 
JUPUSDT     gen_bb762669            short   1.50   1.57   1.73   si    si    si 
THEUSDT     gen_658b2edb            long    2.00   4.40   1.25   no    no    no 
XPLUSDT     gen_e59ad90b            long    1.50   4.77   0.87   no    no    no 
PROMUSDT    gen_cd5c842f            long    2.00   1.62   0.20   no    no    no 
SPXUSDT     gen_725cb5f4            long    0.75   3.94   0.17   no    no    no 
BTRUSDT     gen_9a383fff            long    1.50   4.55   1.24   no    no    no 
GPSUSDT     gen_8a66a70b            long    2.00   4.46   0.07   no    no    no 
ORCAUSDT    gen_9a383fff            long    1.50   3.52   0.80   no    no    no 
MUBARAKUSDT gen_cf6a181e            short   1.50   6.86   1.49   no    no    no 
SEIUSDT     gen_4f890271            short   2.00   0.88   1.63   no    si    si 
FLOCKUSDT   gen_c5194ce4            short   0.75   1.95   0.00   no    no    no 
PHAUSDT     gen_2b41880d            short   1.50   3.27   1.82   si    no    si 
SYRUPUSDT   gen_98d56766            short   1.50   5.03   1.04   no    no    no 
OPENUSDT    gen_f3661202            long    1.50   0.92   0.77   no    no    no 
MUBARAKUSDT gen_658b2edb            long    2.00   1.13   0.68   no    no    no 
UBUSDT      gen_f3661202            long    2.00   1.52   0.02   no    no    no 
XPLUSDT     gen_e59ad90b            short   1.50   1.50   0.86   no    no    no 
AXSUSDT     gen_b922252e            long    1.50   1.69   1.04   no    no    no 
JUPUSDT     gen_bb762669            long    1.50   3.17   1.50   no    no    no 
RAYSOLUSDT  gen_fa304106            long    2.00   1.41   0.06   no    no    no 
GALAUSDT    gen_b9aa9989            long    1.00   0.51   0.01   no    no    no 
UBUSDT      gen_fb7d035a            long    1.50   2.53   0.84   no    no    no 
HEMIUSDT    gen_f001d778            long    2.00   2.32   1.08   no    no    no 
AIOUSDT     gen_581d4a68            long    2.00   1.40   0.13   no    no    no 
STXUSDT     gen_a5b0e4de            short   2.00   1.06   0.89   no    no    no 
UBUSDT      gen_f3661202            long    2.00   6.51   1.16   no    no    no 
CROSSUSDT   gen_d606fde3            long    2.00   1.74   1.16   no    no    no 
TUTUSDT     gen_4465723e            long    1.50   0.25   0.82   no    si    si 
DOTUSDT     gen_919c110c            short   2.00   3.60   1.18   no    no    no 
SUIUSDT     gen_8c9b332f            short   1.00   2.67   0.82   no    no    no 
QUSDT       gen_85fadf54            long    1.50   3.85   0.01   no    no    no 
HUMAUSDT    gen_771790b1            short   2.00   2.99   0.29   no    no    no 
UBUSDT      gen_fb7d035a            long    1.50   4.62   0.37   no    no    no 
QUSDT       gen_18c839a0            short   1.50   1.63   0.91   no    no    no 
SYRUPUSDT   gen_f3b97917            long    1.00   4.25   0.92   no    no    no 
HEMIUSDT    gen_f4c1300a            short   1.50   2.80   0.89   no    no    no 
PHAUSDT     gen_fa304106            long    1.50   2.26   0.08   no    no    no 
PNUTUSDT    gen_4810faab            long    2.00   2.52   1.62   no    no    no 
(mostrati i 40 piu' recenti su 196)

  trade misurati: 196 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.23R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  20   10%
  raggiunto il livello strutturale ........  13    7%
  raggiunto il piu' vicino dei due ........  28   14%
  Lettura: il livello strutturale sta in mediana a 3.23R (primo gradino mediano 1.50R) e viene raggiunto nel 7% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 14% dei casi; il livello e' piu' vicino del TP1 in 41 trade su 196.
```
