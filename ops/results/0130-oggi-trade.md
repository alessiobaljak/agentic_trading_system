# 0130-oggi-trade.req

_eseguito: 2026-09-21 10:07 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.4s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 24  (24 con apertura nota)
Giorni coperti:          6
Trade/giorno:            min 1 · media 4.0 · max 6
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 5
Durata media holding:    5.1h  (min 0.2h · max 13.3h)
Posizioni contemporanee: MAX 4 · media nel tempo 1.1
Coin distinte:           12
Strategie distinte:      12

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       11    3/11    -15.59         0.69R
short      13    2/13    -30.11         0.59R

Regime ALL'APERTURA x direzione:
  bear_trending      long 2 · short 2
  bull_trending      long 5 · short 5
  high_uncertainty   long 1 · short 4
  sideways           long 3 · short 2

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend          7 trade · PnL   -17.18
  CONTROTREND       7 trade · PnL   -17.35
  regime neutro    10 trade · PnL   -11.16

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.
```
