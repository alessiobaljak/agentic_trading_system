# 0133-mfe-stop-per-classe.req

_eseguito: 2026-09-21 12:35 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 2.3s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 27 · con mfe_r registrato: 27
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 13 trade su 27 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              27     0.69    63%    33%    26%    22%    11%    11%     4%
gen_fa304106                         4     0.52    50%     0%     0%     0%     0%     0%     0%
gen_6d06dca0                         4     1.05    75%    50%    25%     0%     0%     0%     0%
gen_2031005e                         3     0.18     0%     0%     0%     0%     0%     0%     0%
gen_ba3a671f                         3     0.30    33%     0%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (21 su 27 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........   7   33%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  13   62%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    5%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.69R, massima 1.23R; con un primo gradino a 0.69R meta' di loro avrebbe incassato
  (il primo gradino qui e' quello GLOBALE; per coppia vale la sua scala)

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)              27      -0.302        -0.300 *      -0.450        -0.511  
gen_fa304106                         4      -1.000 *      -1.000        -1.000        -1.000  
gen_6d06dca0                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_2031005e                         3      -1.000 *      -1.000        -1.000        -1.000  
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
