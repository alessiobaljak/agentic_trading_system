# 0237-controllo-25set-mfe.req

_eseguito: 2026-09-25 06:10 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 2.5s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 55 · con mfe_r registrato: 55
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 16 trade su 55 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              55     0.84    71%    44%    24%    15%     5%     5%     2%
gen_fa304106                         5     0.52    60%     0%     0%     0%     0%     0%     0%
gen_ba3a671f                         5     0.30    20%     0%     0%     0%     0%     0%     0%
gen_6d06dca0                         5     1.05    80%    60%    40%     0%     0%     0%     0%
gen_2031005e                         5     0.20    40%    20%     0%     0%     0%     0%     0%
gen_18c839a0                         4     1.42    75%    50%    25%    25%     0%     0%     0%
gen_bf1e00d4                         3     0.81    67%    33%    33%    33%    33%    33%     0%
gen_f238d283                         3     2.23   100%   100%    67%    67%     0%     0%     0%
gen_b31d8b93                         3     1.23    67%    67%    33%    33%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (32 su 55 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  11   34%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  20   62%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    3%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.67R, massima 1.23R; con un primo gradino a 0.67R meta' di loro avrebbe incassato
  (il primo gradino qui e' quello GLOBALE; per coppia vale la sua scala)

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              55      -0.254 *      -0.280        -0.572        -0.702  
gen_fa304106                         5      -1.000 *      -1.000        -1.000        -1.000  
gen_ba3a671f                         5      -1.000 *      -1.000        -1.000        -1.000  
gen_6d06dca0                         5      -0.040 *      -0.220        -0.420        -1.000  
gen_2031005e                         5      -0.740 *      -0.740        -1.000        -1.000  
gen_18c839a0                         4      -0.237        -0.200 *      -0.637        -0.600  
gen_bf1e00d4                         3      -0.083        +0.033 *      -0.217        -0.067  
gen_f238d283                         3      +0.600        +0.700 *      -0.033        +0.067  
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
[backtest] dati da binance: 409 candele
[backtest] cache ESTESA di 44 candele (invece di riscaricarne 409) (BULLAUSDT 15m)
[backtest] dati da cache: 942 candele (GPSUSDT 15m)
[backtest] dati da cache: 366 candele (JTOUSDT 15m)
[backtest] dati da cache: 1038 candele (DEXEUSDT 15m)
[backtest] dati da cache: 654 candele (QUSDT 15m)
[backtest] dati da cache: 366 candele (ZKUSDT 15m)
[backtest] dati da cache: 462 candele (DOTUSDT 15m)
[backtest] dati da cache: 1057 candele (SPXUSDT 15m)
[backtest] dati da cache: 865 candele (VETUSDT 15m)
[backtest] dati da cache: 577 candele (MUBARAKUSDT 15m)
[backtest] dati da cache: 481 candele (USELESSUSDT 15m)
[backtest] dati da cache: 577 candele (BICOUSDT 15m)
[backtest] dati da cache: 577 candele (PROMUSDT 15m)
[backtest] dati da cache: 577 candele (STXUSDT 15m)
[backtest] dati da cache: 769 candele (SYRUPUSDT 15m)
[backtest] dati da cache: 673 candele (TUTUSDT 15m)
[backtest] dati da cache: 673 candele (ORCAUSDT 15m)
[backtest] dati da cache: 385 candele (NEIROUSDT 15m)

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
DEXEUSDT    gen_b31d8b93            long    1.50   0.87   1.23   no    si    si 
STXUSDT     gen_b9bf5d01            long    1.50   1.36   0.74   no    no    no 
VETUSDT     gen_6d06dca0            short   1.50   4.04   0.85   no    no    no 
DEXEUSDT    gen_fa304106            short   1.50   2.06   0.59   no    no    no 
SPXUSDT     gen_ba3a671f            long    1.50   3.74   0.56   no    no    no 
SPXUSDT     gen_ba3a671f            long    1.50   6.51   0.30   no    no    no 
DEXEUSDT    gen_fa304106            short   1.50   0.98   0.10   no    no    no 
ORCAUSDT    gen_6d06dca0            short   1.50   2.40   1.05   no    no    no 
STXUSDT     gen_b9bf5d01            long    1.50   1.74   0.69   no    no    no 
DEXEUSDT    gen_fa304106            long    1.50   1.45   0.00   no    no    no 
QUSDT       gen_18c839a0            short   1.50   4.71   0.90   no    no    no 
USELESSUSDT gen_2031005e            short   1.50   1.94   0.11   no    no    no 
PROMUSDT    gen_cd5c842f            short   1.50   1.59   0.62   no    no    no 
USELESSUSDT gen_2031005e            short   1.50   2.65   0.20   no    no    no 
USELESSUSDT gen_2031005e            short   1.50   3.33   0.18   no    no    no 
USELESSUSDT gen_2031005e            short   1.50   3.82   1.35   no    no    no 
MUBARAKUSDT gen_1f7ead60            short   1.50   6.66   0.00   no    no    no 
SYRUPUSDT   gen_af734c68            short   1.50   6.66   1.41   no    no    no 
MUBARAKUSDT gen_2053cba6            short   1.50   6.40   1.05   no    no    no 
STXUSDT     gen_b9bf5d01            long    1.50   1.86   1.27   no    no    no 
MUBARAKUSDT gen_2053cba6            short   1.50   7.43   1.98   si    no    si 
USELESSUSDT gen_2031005e            short   1.50   4.16   0.80   no    no    no 
VETUSDT     gen_6d06dca0            short   1.50   3.82   1.59   si    no    si 
MUBARAKUSDT gen_ff3e4154            long    1.50   1.64   0.84   no    no    no 
SPXUSDT     gen_ba3a671f            long    1.50   4.14   0.33   no    no    no 
QUSDT       gen_18c839a0            long    1.50   2.39   0.32   no    no    no 
DOTUSDT     gen_919c110c            long    1.50   5.16   1.61   si    no    si 
SPXUSDT     gen_ba3a671f            long    1.50   4.57   0.14   no    no    no 
QUSDT       gen_18c839a0            short   1.50   3.36   1.42   no    no    no 
DEXEUSDT    gen_fa304106            short   1.50   6.70   0.64   no    no    no 
QUSDT       gen_18c839a0            short   1.50   4.28   2.15   si    no    si 
ZKUSDT      gen_98837ec2            long    1.50   9.32   0.13   no    no    no 
DEXEUSDT    gen_b31d8b93            long    1.50   3.96   0.00   no    no    no 
GPSUSDT     gen_bf1e00d4            long    1.50   4.85   0.06   no    no    no 
JTOUSDT     gen_35632db9            long    1.50   5.59   1.25   no    no    no 
BULLAUSDT   gen_7ac562e3            short   1.50   3.46   1.26   no    no    no 
GPSUSDT     gen_bf1e00d4            long    1.50   6.25   0.81   no    no    no 
JTOUSDT     gen_f238d283            short   1.50   3.43   1.37   no    no    no 
XPLUSDT     gen_a220b439            short   1.50   4.09   0.67   no    no    no 
BULLAUSDT   gen_7ac562e3            short   1.50   8.72   1.13   no    no    no 
(mostrati i 40 piu' recenti su 47)

  trade misurati: 47 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 4.04R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........   5   11%
  raggiunto il livello strutturale ........   1    2%
  raggiunto il piu' vicino dei due ........   6   13%
  Lettura: il livello strutturale sta in mediana a 4.04R (primo gradino mediano 1.50R) e viene raggiunto nel 2% dei trade contro il 11% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 13% dei casi; il livello e' piu' vicino del TP1 in 5 trade su 47.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
