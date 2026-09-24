# 0191-stato-pomeriggio-trades.req

_eseguito: 2026-09-24 12:18 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.5s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 50  (50 con apertura nota)
Giorni coperti:          9
Trade/giorno:            min 1 · media 5.6 · max 16
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 8
Durata media holding:    5.2h  (min 0.1h · max 24.0h)
Posizioni contemporanee: MAX 7 · media nel tempo 1.4
Coin distinte:           17
Strategie distinte:      20

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       22    7/22    -19.85         0.69R
short      28   12/28    -31.01         0.92R

Regime ALL'APERTURA x direzione:
  bear_trending      long 7 · short 3
  bull_trending      long 7 · short 11
  high_uncertainty   long 4 · short 11
  sideways           long 4 · short 3

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         10 trade · PnL   -22.28
  CONTROTREND      18 trade · PnL    10.73
  regime neutro    22 trade · PnL   -39.31

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 11 (6 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x6
  classe ingresso          x4
  controtrend              x2
  classe uscita            x2

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_ba3a671f     5     0     5   -18.21     1/  0/   0          0        1           1
  gen_fa304106     5     0     5    -9.91     0/  1/   0          0        1           0
  gen_2031005e     5     1     4   -29.90     0/  0/   0          0        0           0
  gen_6d06dca0     5     1     4   -11.38     0/  0/   0          0        0           0
  gen_af734c68     3     1     2    -2.31     0/  0/   0          0        0           0
  gen_b31d8b93     3     1     2    -3.22     1/  0/   0          0        1           0
  gen_b9bf5d01     3     1     2    -7.24     0/  0/   0          0        0           0
  gen_18c839a0     4     3     1    -2.28     0/  1/   0          0        1           0
  ultimi referti in perdita:
   - QUSDT gen_18c839a0 long -5.50: a favore fino a 0.32R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - SPXUSDT gen_ba3a671f long -1.24: mai andato a favore (mfe 0.14R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - DEXEUSDT gen_fa304106 short -1.50: a favore fino a 0.64R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - ZKUSDT gen_98837ec2 long -1.23: mai andato a favore (mfe 0.13R): direzione sbagliata
   - DEXEUSDT gen_b31d8b93 long -1.70: mai andato a favore (mfe 0.00R): direzione sbagliata
   - GPSUSDT gen_bf1e00d4 long -2.35: mai andato a favore (mfe 0.06R): direzione sbagliata · controtrend rispetto al regime all'ingresso

SERIE DI PERDITE in corso per strategia (freno x0.5 da 4 di fila):
  gen_ba3a671f   5 perdite di fila  <- FRENO attivo
  gen_fa304106   5 perdite di fila  <- FRENO attivo

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_ba3a671f: solo_short — long 5/5 persi (campione 5)
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)
```
