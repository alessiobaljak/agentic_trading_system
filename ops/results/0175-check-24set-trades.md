# 0175-check-24set-trades.req

_eseguito: 2026-09-24 06:13 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.7s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 44  (44 con apertura nota)
Giorni coperti:          9
Trade/giorno:            min 1 · media 4.9 · max 16
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 2
Durata media holding:    5.4h  (min 0.1h · max 24.0h)
Posizioni contemporanee: MAX 7 · media nel tempo 1.3
Coin distinte:           14
Strategie distinte:      17

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       18    6/18    -16.28         0.72R
short      26   10/26    -32.87         0.87R

Regime ALL'APERTURA x direzione:
  bear_trending      long 5 · short 3
  bull_trending      long 7 · short 11
  high_uncertainty   long 3 · short 10
  sideways           long 3 · short 2

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         10 trade · PnL   -22.28
  CONTROTREND      16 trade · PnL    11.38
  regime neutro    18 trade · PnL   -38.25

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 5 (3 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x3
  classe uscita            x2
  classe ingresso          x1
  controtrend              x1

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_ba3a671f     5     0     5   -18.21     1/  0/   0          0        1           1
  gen_fa304106     5     0     5    -9.91     0/  1/   0          0        1           0
  gen_2031005e     5     1     4   -29.90     0/  0/   0          0        0           0
  gen_6d06dca0     5     1     4   -11.38     0/  0/   0          0        0           0
  gen_af734c68     3     1     2    -2.31     0/  0/   0          0        0           0
  gen_b9bf5d01     3     1     2    -7.24     0/  0/   0          0        0           0
  gen_18c839a0     3     2     1    -3.34     0/  1/   0          0        1           0
  gen_1f7ead60     1     0     1    -7.11     0/  0/   0          0        0           0
  ultimi referti in perdita:
   - QUSDT gen_18c839a0 long -5.50: a favore fino a 0.32R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - SPXUSDT gen_ba3a671f long -1.24: mai andato a favore (mfe 0.14R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - DEXEUSDT gen_fa304106 short -1.50: a favore fino a 0.64R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)

SERIE DI PERDITE in corso per strategia (freno x0.5 da 4 di fila):
  gen_ba3a671f   5 perdite di fila  <- FRENO attivo
  gen_fa304106   5 perdite di fila  <- FRENO attivo

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_ba3a671f: solo_short — long 5/5 persi (campione 5)
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)
```
