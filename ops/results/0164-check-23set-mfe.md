# 0164-check-23set-mfe.req

_eseguito: 2026-09-23 06:02 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 37 · con mfe_r registrato: 37
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 15 trade su 37 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              37     0.85    73%    43%    27%    19%     8%     8%     3%
gen_2031005e                         5     0.20    40%    20%     0%     0%     0%     0%     0%
gen_fa304106                         4     0.52    50%     0%     0%     0%     0%     0%     0%
gen_6d06dca0                         4     1.05    75%    50%    25%     0%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%
gen_ba3a671f                         3     0.30    33%     0%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (23 su 37 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........   7   30%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  15   65%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    4%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.69R, massima 1.23R; con un primo gradino a 0.69R meta' di loro avrebbe incassato
  (il primo gradino qui e' quello GLOBALE; per coppia vale la sua scala)

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              37      -0.208 *      -0.227        -0.481        -0.600  
gen_2031005e                         5      -0.740 *      -0.740        -1.000        -1.000  
gen_fa304106                         4      -1.000 *      -1.000        -1.000        -1.000  
gen_6d06dca0                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_b9bf5d01                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_af734c68                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_ba3a671f                         3      -1.000 *      -1.000        -1.000        -1.000  

(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

--- stderr ---
/root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  return query.where(field_path, op_string, value)
```
