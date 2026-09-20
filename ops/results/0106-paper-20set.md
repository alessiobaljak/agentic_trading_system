# 0106-paper-20set.req

_eseguito: 2026-09-20 04:31 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 15  (15 con apertura nota)
Giorni coperti:          5
Trade/giorno:            min 1 · media 3.0 · max 6
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 2
Durata media holding:    5.7h  (min 0.7h · max 13.3h)
Posizioni contemporanee: MAX 4 · media nel tempo 1.0
Coin distinte:           10
Strategie distinte:      10

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long        7     3/7      0.53         1.23R
short       8     1/8    -18.52         0.72R

Regime ALL'APERTURA x direzione:
  bull_trending      long 4 · short 5
  high_uncertainty   long 1 · short 1
  sideways           long 2 · short 2

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend          4 trade · PnL    -6.47
  CONTROTREND       5 trade · PnL    -8.99
  regime neutro     6 trade · PnL    -2.53

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.
```
