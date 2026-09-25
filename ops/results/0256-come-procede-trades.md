# 0256-come-procede-trades.req

_eseguito: 2026-09-25 19:38 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.4s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 82  (82 con apertura nota)
Giorni coperti:          10
Trade/giorno:            min 1 · media 8.2 · max 29
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29
Durata media holding:    4.2h  (min 0.1h · max 24.0h)
Posizioni contemporanee: MAX 8 · media nel tempo 1.6
Coin distinte:           28
Strategie distinte:      34

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       29   13/29    -16.53         0.84R
short      53   25/53    -46.92         0.82R

Regime ALL'APERTURA x direzione:
  bear_trending      long 8 · short 3
  bull_trending      long 9 · short 27
  high_uncertainty   long 5 · short 18
  sideways           long 7 · short 5

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         12 trade · PnL   -20.89
  CONTROTREND      35 trade · PnL     5.30
  regime neutro    35 trade · PnL   -47.86

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 43 (19 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x19
  classe ingresso          x11
  controtrend              x8
  classe uscita            x8

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_ba3a671f     5     0     5   -18.21     1/  0/   0          0        1           1
  gen_fa304106     5     0     5    -9.91     0/  1/   0          0        1           0
  gen_2031005e     6     2     4   -28.14     0/  0/   0          0        0           0
  gen_6d06dca0     5     1     4   -11.38     0/  0/   0          0        0           0
  gen_1f7ead60     2     0     2   -10.66     1/  0/   0          0        1           0
  gen_acfd527a     2     0     2    -3.33     1/  1/   0          0        2           0
  gen_af734c68     3     1     2    -2.31     0/  0/   0          0        0           0
  gen_b31d8b93     3     1     2    -3.22     1/  0/   0          0        1           0
  ultimi referti in perdita:
   - ENAUSDT gen_bb762669 short -2.62: a favore fino a 0.66R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - NEIROUSDT gen_f3124a14 short -1.77: a favore fino a 0.41R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - HUMAUSDT gen_fca11c08 short -2.60: mai andato a favore (mfe 0.00R): direzione sbagliata
   - SUIUSDT gen_490a90e5 short -1.93: mai andato a favore (mfe 0.07R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - HUMAUSDT gen_a32bee42 short -3.45: mai andato a favore (mfe 0.00R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - MUBARAKUSDT gen_1f7ead60 short -3.54: mai andato a favore (mfe 0.21R): direzione sbagliata

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_ba3a671f   5 perdite di fila  (freno spento)
  gen_fa304106   5 perdite di fila  (freno spento)
  gen_1f7ead60   2 perdite di fila
  gen_acfd527a   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-09-25 19:32 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_ba3a671f: solo_short — long 5/5 persi (campione 5)
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 10  (vinti 8, persi 2; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.704   p media dei persi: 0.667   (se p predice, la prima e' piu' alta)
  sopra la soglia: 10/10 trade, PnL +1.67 contro +1.67 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.257
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 10
  trade chiusi: 0 · vinti 0 · PnL +0.00
  coppie esplorative poi validate 0 / scartate 0  (il metro: si legge a 100 trade esplorativi)
```
