# 0297-controllo-27set-mfe.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 6.4s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 111 · con mfe_r registrato: 111
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 45 trade su 111 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             111     0.82    68%    37%    16%    10%     4%     3%     1%
gen_fca11c08                        10     0.22    40%    10%     0%     0%     0%     0%     0%
gen_ba3a671f                         6     0.33    33%    17%     0%     0%     0%     0%     0%
gen_2031005e                         6     0.80    50%    33%     0%     0%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_fa304106                         5     0.52    60%     0%     0%     0%     0%     0%     0%
gen_6d06dca0                         5     1.05    80%    60%    40%     0%     0%     0%     0%
gen_cd5c842f                         4     2.10   100%    75%    50%    50%    25%    25%    25%
gen_bf1e00d4                         4     0.90    75%    25%    25%    25%    25%    25%     0%
gen_4465723e                         4     1.36   100%    50%    25%     0%     0%     0%     0%
gen_490a90e5                         4     0.67    75%     0%     0%     0%     0%     0%     0%
gen_18c839a0                         4     1.42    75%    50%    25%    25%     0%     0%     0%
gen_b31d8b93                         3     1.23    67%    67%    33%    33%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (58 su 111 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  23   40%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  34   59%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    2%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.62R, massima 1.23R; con un primo gradino a 0.62R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             111      -0.402 *      -0.417        -0.714        -0.809  
gen_fca11c08                        10      -0.870 *      -0.870        -1.000        -1.000  
gen_ba3a671f                         6      -0.783 *      -0.783        -1.000        -1.000  
gen_2031005e                         6      -0.567 *      -0.567        -1.000        -1.000  
gen_f238d283                         5      -0.040        +0.020 *      -0.420        -0.360  
gen_fa304106                         5      -1.000 *      -1.000        -1.000        -1.000  
gen_6d06dca0                         5      -0.040 *      -0.220        -0.420        -1.000  
gen_cd5c842f                         4      +0.450        +0.575 *      +0.450        +0.100  
gen_bf1e00d4                         4      -0.312        -0.225 *      -0.413        -0.300  
gen_4465723e                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_490a90e5                         4      -1.000 *      -1.000        -1.000        -1.000  
gen_18c839a0                         4      -0.237        -0.200 *      -0.637        -0.600  
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
[backtest] cache ESTESA di 121 candele (invece di riscaricarne 1081) (PROMUSDT 15m)
[backtest] dati da binance: 409 candele
[backtest] dati da binance: 313 candele
[backtest] dati da binance: 313 candele
[backtest] cache ESTESA di 313 candele (invece di riscaricarne 1177) (VETUSDT 15m)
[backtest] cache ESTESA di 313 candele (invece di riscaricarne 1369) (SPXUSDT 15m)
[backtest] cache ESTESA di 212 candele (invece di riscaricarne 1153) (GPSUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] cache riusata (tagliata da 2026-09-26): 1057 candele (ORCAUSDT 15m)
[backtest] cache riusata (tagliata da 2026-09-26): 961 candele (STXUSDT 15m)
[backtest] cache riusata (tagliata da 2026-09-26): 577 candele (DOTUSDT 15m)
[backtest] cache riusata (tagliata da 2026-09-26): 1057 candele (TUTUSDT 15m)
[backtest] cache ESTESA di 212 candele (invece di riscaricarne 1249) (DEXEUSDT 15m)
[backtest] cache riusata (tagliata da 2026-09-26): 385 candele (HUMAUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] cache ESTESA di 481 candele (invece di riscaricarne 1249) (SYRUPUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] cache riusata (tagliata da 2026-09-26): 769 candele (USELESSUSDT 15m)
[backtest] cache riusata (tagliata da 2026-09-26): 1153 candele (NEIROUSDT 15m)
[backtest] dati da cache: 793 candele (QUSDT 15m)
[backtest] dati da cache: 769 candele (MUBARAKUSDT 15m)
[backtest] dati da cache: 385 candele (XMRUSDT 15m)
[backtest] dati da cache: 385 candele (ZORAUSDT 15m)
[backtest] dati da cache: 385 candele (SUIUSDT 15m)
[backtest] dati da cache: 385 candele (SAHARAUSDT 15m)
[backtest] dati da cache: 481 candele (JTOUSDT 15m)
[backtest] dati da cache: 385 candele (ENAUSDT 15m)
[backtest] dati da cache: 385 candele (SKYAIUSDT 15m)
[backtest] dati da cache: 385 candele (RENDERUSDT 15m)
[backtest] dati da cache: 409 candele (XPLUSDT 15m)
[backtest] dati da cache: 481 candele (HEIUSDT 15m)
[backtest] dati da cache: 409 candele (BULLAUSDT 15m)
[backtest] dati da cache: 366 candele (ZKUSDT 15m)
[backtest] dati da cache: 577 candele (BICOUSDT 15m)

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
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
SYRUPUSDT   gen_b7d57ce7            short   2.00   2.69   0.43   no    no    no 
NEIROUSDT   gen_e132204b            long    1.50   1.02   0.62   no    no    no 
QUSDT       gen_cde82a91            short   1.50   5.62   0.94   no    no    no 
THEUSDT     gen_658b2edb            short   2.00   1.73   1.30   no    no    no 
TAUSDT      gen_bf2be656            long    1.50   1.60   0.33   no    no    no 
USELESSUSDT gen_c0fd1d91            long    1.50   4.52   0.02   no    no    no 
SYRUPUSDT   gen_4c6df481            long    2.00   1.47   2.31   si    si    si 
SEIUSDT     gen_4f890271            short   2.00   4.98   1.09   no    no    no 
HUMAUSDT    gen_fca11c08            short   2.00   4.73   0.10   no    no    no 
MITOUSDT    gen_8b91ba18            long    2.00   2.46   0.85   no    no    no 
TUTUSDT     gen_4465723e            long    1.50   3.03   1.36   no    no    no 
TSTUSDT     gen_a640dfa5            short   2.00   1.84   1.09   no    no    no 
DEXEUSDT    gen_887d87df            long    1.50   1.40   1.14   no    no    no 
HUMAUSDT    gen_fca11c08            short   2.00   5.94   0.10   no    no    no 
HUMAUSDT    gen_fca11c08            short   2.00   5.44   0.21   no    no    no 
DOTUSDT     gen_fca11c08            short   1.50   5.37   0.04   no    no    no 
ORCAUSDT    gen_fca11c08            short   1.50   5.48   0.82   no    no    no 
CROSSUSDT   gen_d606fde3            long    2.00   1.05   0.29   no    no    no 
XRPUSDT     gen_50905b4a            long    1.50  11.18   0.49   no    no    no 
VETUSDT     gen_b2f350ff            long    2.00   4.42   0.72   no    no    no 
SPXUSDT     gen_ba3a671f            long    0.75   3.16   1.32   si    no    si 
GPSUSDT     gen_bf1e00d4            long    1.50   2.50   0.90   no    no    no 
PROMUSDT    gen_cd5c842f            short   2.00   4.20   2.10   si    no    si 
AVAAIUSDT   gen_e50a9211            long    1.50   3.81   0.45   no    no    no 
JUPUSDT     gen_bb762669            short   1.50   1.79   0.79   no    no    no 
MITOUSDT    gen_8b91ba18            long    2.00   4.39   1.33   no    no    no 
(mostrati i 40 piu' recenti su 102)

  trade misurati: 102 · saltati: 9 (livello assente (prezzo gia' oltre tutto, o nessuna candela prima): 1, senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 4.07R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  11   11%
  raggiunto il livello strutturale ........   2    2%
  raggiunto il piu' vicino dei due ........  12   12%
  Lettura: il livello strutturale sta in mediana a 4.07R (primo gradino mediano 1.50R) e viene raggiunto nel 2% dei trade contro il 11% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 12% dei casi; il livello e' piu' vicino del TP1 in 13 trade su 102.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
