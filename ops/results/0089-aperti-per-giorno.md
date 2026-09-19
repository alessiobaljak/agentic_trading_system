# 0089-aperti-per-giorno.req

_eseguito: 2026-09-19 12:02 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 12  (12 con apertura nota)
Giorni coperti:          4
Trade/giorno:            min 1 · media 3.0 · max 6
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 3
Durata media holding:    5.3h  (min 0.7h · max 13.3h)
Posizioni contemporanee: MAX 4 · media nel tempo 1.0
Coin distinte:           9
Strategie distinte:      9

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long        6     2/6     -0.36         0.99R
short       6     0/6    -17.68         0.69R

Regime ALL'APERTURA x direzione:
  bull_trending      long 4 · short 4
  high_uncertainty   long 1 · short 1
  sideways           long 1 · short 1

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend          4 trade · PnL    -6.47
  CONTROTREND       4 trade · PnL   -10.16
  regime neutro     4 trade · PnL    -1.42

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.
```
