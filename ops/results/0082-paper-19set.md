# 0082-paper-19set.req

_eseguito: 2026-09-19 06:01 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 10  (10 con apertura nota)
Giorni coperti:          4
Trade/giorno:            min 1 · media 2.5 · max 6
Durata media holding:    5.3h  (min 0.7h · max 13.3h)
Posizioni contemporanee: MAX 4 · media nel tempo 0.9
Coin distinte:           9
Strategie distinte:      8

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long        5     2/5      2.05         0.74R
short       5     0/5    -12.18         0.52R

Regime ALL'APERTURA x direzione:
  bull_trending      long 3 · short 4
  high_uncertainty   long 1
  sideways           long 1 · short 1

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend          3 trade · PnL    -4.06
  CONTROTREND       4 trade · PnL   -10.16
  regime neutro     3 trade · PnL     4.09

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.
```
