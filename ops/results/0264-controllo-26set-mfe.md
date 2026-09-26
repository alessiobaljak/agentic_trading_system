# 0264-controllo-26set-mfe.req

_eseguito: 2026-09-26 06:05 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 7.3s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 84 · con mfe_r registrato: 84
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 27 trade su 84 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              84     0.84    69%    37%    19%    11%     5%     4%     1%
gen_2031005e                         6     0.80    50%    33%     0%     0%     0%     0%     0%
gen_fca11c08                         5     0.88    60%    20%     0%     0%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_fa304106                         5     0.52    60%     0%     0%     0%     0%     0%     0%
gen_ba3a671f                         5     0.30    20%     0%     0%     0%     0%     0%     0%
gen_6d06dca0                         5     1.05    80%    60%    40%     0%     0%     0%     0%
gen_490a90e5                         4     0.67    75%     0%     0%     0%     0%     0%     0%
gen_18c839a0                         4     1.42    75%    50%    25%    25%     0%     0%     0%
gen_4465723e                         3     0.82   100%    33%    33%     0%     0%     0%     0%
gen_cd5c842f                         3     1.05   100%    67%    33%    33%    33%    33%    33%
gen_bf1e00d4                         3     0.81    67%    33%    33%    33%    33%    33%     0%
gen_b31d8b93                         3     1.23    67%    67%    33%    33%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (45 su 84 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  18   40%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  26   58%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    2%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.65R, massima 1.23R; con un primo gradino a 0.65R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              84      -0.375 *      -0.399        -0.657        -0.786  
gen_2031005e                         6      -0.567 *      -0.567        -1.000        -1.000  
gen_fca11c08                         5      -0.740 *      -0.740        -1.000        -1.000  
gen_f238d283                         5      -0.040        +0.020 *      -0.420        -0.360  
gen_fa304106                         5      -1.000 *      -1.000        -1.000        -1.000  
gen_ba3a671f                         5      -1.000 *      -1.000        -1.000        -1.000  
gen_6d06dca0                         5      -0.040 *      -0.220        -0.420        -1.000  
gen_490a90e5                         4      -1.000 *      -1.000        -1.000        -1.000  
gen_18c839a0                         4      -0.237        -0.200 *      -0.637        -0.600  
gen_4465723e                         3      -0.417 *      -0.567        -0.517        -1.000  
gen_cd5c842f                         3      +0.350        +0.467 *      +0.450        -0.067  
gen_bf1e00d4                         3      -0.083        +0.033 *      -0.217        -0.067  
gen_b31d8b93                         3      +0.017        +0.067 *      -0.517        -0.467  
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
[backtest] cache ESTESA di 140 candele (invece di riscaricarne 793) (QUSDT 15m)
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 1057) (ORCAUSDT 15m)
[backtest] cache ESTESA di 193 candele (invece di riscaricarne 769) (MUBARAKUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 769) (USELESSUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] cache ESTESA di 116 candele (invece di riscaricarne 577) (DOTUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 1057) (TUTUSDT 15m)
[backtest] cache ESTESA di 116 candele (invece di riscaricarne 481) (JTOUSDT 15m)
[backtest] cache ESTESA di 769 candele (invece di riscaricarne 1153) (NEIROUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] dati da cache: 409 candele (XPLUSDT 15m)
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 961) (STXUSDT 15m)
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 961) (PROMUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da cache: 409 candele (BULLAUSDT 15m)
[backtest] dati da cache: 942 candele (GPSUSDT 15m)
[backtest] dati da cache: 1038 candele (DEXEUSDT 15m)
[backtest] dati da cache: 366 candele (ZKUSDT 15m)
[backtest] dati da cache: 1057 candele (SPXUSDT 15m)
[backtest] dati da cache: 865 candele (VETUSDT 15m)
[backtest] dati da cache: 577 candele (BICOUSDT 15m)
[backtest] dati da cache: 769 candele (SYRUPUSDT 15m)

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
DEXEUSDT    gen_fa304106            short   1.50   6.70   0.64   no    no    no 
QUSDT       gen_18c839a0            short   1.50   4.28   2.15   si    no    si 
ZKUSDT      gen_98837ec2            long    1.50   9.32   0.13   no    no    no 
DEXEUSDT    gen_b31d8b93            long    1.50   3.96   0.00   no    no    no 
GPSUSDT     gen_bf1e00d4            long    1.50   4.85   0.06   no    no    no 
HEIUSDT     gen_e6ddc613            long    1.50   2.52   0.88   no    no    no 
JTOUSDT     gen_35632db9            long    1.50   5.59   1.25   no    no    no 
BULLAUSDT   gen_7ac562e3            short   1.50   3.46   1.26   no    no    no 
GPSUSDT     gen_bf1e00d4            long    1.50   6.25   0.81   no    no    no 
JTOUSDT     gen_f238d283            short   1.50   3.43   1.37   no    no    no 
XPLUSDT     gen_a220b439            short   1.50   4.09   0.67   no    no    no 
BULLAUSDT   gen_7ac562e3            short   1.50   8.72   1.13   no    no    no 
PROMUSDT    gen_cd5c842f            long    1.50   3.49   1.05   no    no    no 
TUTUSDT     gen_4465723e            short   1.50   1.43   0.82   no    no    no 
RENDERUSDT  gen_acfd527a            short   1.50   4.30   0.65   no    no    no 
SAHARAUSDT  gen_6b94025f            long    1.50   3.17   3.06   si    no    si 
XPLUSDT     gen_b437a671            short   1.50   5.04   0.47   no    no    no 
NEIROUSDT   gen_f3124a14            short   1.50   3.15   0.41   no    no    no 
STXUSDT     gen_acfd527a            short   1.50   2.72   0.00   no    no    no 
ENAUSDT     gen_bb762669            short   1.50   4.19   0.66   no    no    no 
HUMAUSDT    gen_771790b1            short   1.50   6.15   1.97   si    no    si 
ORCAUSDT    gen_fca11c08            short   1.50   4.11   0.22   no    no    no 
JTOUSDT     gen_f238d283            short   1.50   5.85   0.03   no    no    no 
SKYAIUSDT   gen_c61d9322            short   1.50   1.40   1.13   no    no    no 
HUMAUSDT    gen_fca11c08            short   1.50   4.79   0.00   no    no    no 
SUIUSDT     gen_490a90e5            short   1.50   5.83   0.07   no    no    no 
JTOUSDT     gen_f238d283            short   1.50   5.89   0.87   no    no    no 
DOTUSDT     gen_fca11c08            short   1.50   3.91   0.90   no    no    no 
SUIUSDT     gen_490a90e5            short   1.50   5.49   0.67   no    no    no 
SUIUSDT     gen_490a90e5            short   1.50   5.19   0.52   no    no    no 
HUMAUSDT    gen_a32bee42            short   1.50   4.40   0.00   no    no    no 
DOTUSDT     gen_fca11c08            short   1.50   3.40   0.88   no    no    no 
USELESSUSDT gen_2031005e            short   1.50   2.75   1.11   no    no    no 
ZORAUSDT    gen_2c248ee9            long    1.50   2.42   0.84   no    no    no 
SUIUSDT     gen_490a90e5            short   1.50   4.20   0.97   no    no    no 
XMRUSDT     gen_35632db9            long    1.50   2.87   0.84   no    no    no 
MUBARAKUSDT gen_1f7ead60            short   1.50   5.15   0.21   no    no    no 
MUBARAKUSDT gen_49c2f657            short   1.50   4.78   1.59   si    no    si 
QUSDT       gen_bf2be656            long    1.50   4.17   0.43   no    no    no 
ORCAUSDT    gen_fca11c08            short   1.50   3.76   1.41   no    no    no 
(mostrati i 40 piu' recenti su 76)

  trade misurati: 76 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 4.10R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........   8   11%
  raggiunto il livello strutturale ........   1    1%
  raggiunto il piu' vicino dei due ........   9   12%
  Lettura: il livello strutturale sta in mediana a 4.10R (primo gradino mediano 1.50R) e viene raggiunto nel 1% dei trade contro il 11% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 12% dei casi; il livello e' piu' vicino del TP1 in 7 trade su 76.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
