# 0140-check-22set-trades.req

_eseguito: 2026-09-22 06:01 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.5s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 35  (35 con apertura nota)
Giorni coperti:          6
Trade/giorno:            min 1 · media 5.8 · max 16
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16
Durata media holding:    5.9h  (min 0.1h · max 24.0h)
Posizioni contemporanee: MAX 7 · media nel tempo 1.7
Coin distinte:           14
Strategie distinte:      16

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       14    6/14      4.75         0.99R
short      21    7/21    -33.40         0.85R

Regime ALL'APERTURA x direzione:
  bear_trending      long 3 · short 2
  bull_trending      long 6 · short 8
  high_uncertainty   long 2 · short 9
  sideways           long 3 · short 2

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend          8 trade · PnL   -15.28
  CONTROTREND      11 trade · PnL     5.87
  regime neutro    16 trade · PnL   -19.23

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.
```
