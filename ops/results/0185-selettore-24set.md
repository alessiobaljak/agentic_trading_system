# 0185-selettore-24set.req

_eseguito: 2026-09-24 06:36 UTC_

**richiesta:** `selettore`
**eseguito:** `.venv/bin/python -m scripts.selettore_report`
**esito:** codice 0 in 2.5s

```
[selettore] 165 trade da 1 file (0 duplicati fusi, 0 righe rotte saltate)
[selettore] 1 coppie coin+strategia; famiglie: reversion 165
[selettore] minimo train per finestra: 500; soglie candidate: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65

[tutte] 165 trade usabili, dal 2023-03-13 al 2026-08-02
  finestra 1: train 66 trade < minimo -> campione insufficiente
  finestra 2: train 99 trade < minimo -> campione insufficiente
  finestra 3: train 132 trade < minimo -> campione insufficiente
  VERDETTO: CAMPIONE INSUFFICIENTE (0/3 finestre)

[reversion] 165 trade usabili, dal 2023-03-13 al 2026-08-02
  finestra 1: train 66 trade < minimo -> campione insufficiente
  finestra 2: train 99 trade < minimo -> campione insufficiente
  finestra 3: train 132 trade < minimo -> campione insufficiente
  VERDETTO: CAMPIONE INSUFFICIENTE (0/3 finestre)

[modello «tutte»] n 165, lam 1.0, intercetta +0.749 — coefficienti su variabili standardizzate, in ordine di modulo:
    adx        +0.803
    stoch_k    -0.779
    hour_cos   +0.654
    is_long    -0.499
    rsi        +0.465
    dist_ema   +0.176
    hour_sin   +0.108
    vol_ratio  +0.098
    stop_pct   +0.081
    bb_pos     -0.066
    atr_pct    +0.012
    r1         +0.000
    market_up  +0.000
  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)

Il bot NON usa ancora il selettore: questo e' il passo 1 (misura offline); il passo 2 (ombra nel bot) viene dopo, e solo con verdetto «batte».
[firebase] connesso (Firestore + RTDB)

[firebase] pubblicato selector/report.
[selettore] fatto in 1.0s
```
