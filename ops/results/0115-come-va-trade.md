# 0115-come-va-trade.req

_eseguito: 2026-09-20 13:00 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 18  (18 con apertura nota)
Giorni coperti:          5
Trade/giorno:            min 1 · media 3.6 · max 6
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 5
Durata media holding:    5.8h  (min 0.7h · max 13.3h)
Posizioni contemporanee: MAX 4 · media nel tempo 1.1
Coin distinte:           11
Strategie distinte:      11

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long        9     3/9     -7.83         0.74R
short       9     2/9     -8.05         0.85R

Regime ALL'APERTURA x direzione:
  bear_trending      long 2
  bull_trending      long 4 · short 5
  high_uncertainty   long 1 · short 2
  sideways           long 2 · short 2

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend          4 trade · PnL    -6.47
  CONTROTREND       7 trade · PnL   -17.35
  regime neutro     7 trade · PnL     7.94

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.
```
