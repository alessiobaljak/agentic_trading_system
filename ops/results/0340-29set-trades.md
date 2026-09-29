# 0340-29set-trades.req

_eseguito: 2026-09-29 06:12 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 2.2s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 168  (168 con apertura nota)
Giorni coperti:          14
Trade/giorno:            min 1 · media 12.0 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 12
Durata media holding:    3.5h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 2.0
Coin distinte:           48
Strategie distinte:      70

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       66   33/66    -29.38         0.83R
short     102  58/102    -39.74         0.90R

Regime ALL'APERTURA x direzione:
  bear_trending      long 17 · short 17
  bull_trending      long 18 · short 41
  high_uncertainty   long 11 · short 27
  sideways           long 20 · short 17

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         35 trade · PnL   -10.49
  CONTROTREND      58 trade · PnL     0.78
  regime neutro    75 trade · PnL   -59.42

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 129 (52 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x52
  classe ingresso          x27
  classe uscita            x25
  controtrend              x18

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_ba3a671f     6     1     5   -17.27     1/  0/   0          0        1           1
  gen_fa304106     5     0     5    -9.91     0/  1/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_b31d8b93     4     1     3    -5.10     1/  1/   0          0        2           0
  gen_1f7ead60     2     0     2   -10.66     1/  0/   0          0        1           0
  gen_490a90e5     7     5     2     1.21     2/  0/   0          0        2           1
  ultimi referti in perdita:
   - AVAAIUSDT gen_e50a9211 short -2.11: a favore fino a 0.32R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - FLOCKUSDT gen_c5194ce4 short -1.25: mai andato a favore (mfe 0.05R): direzione sbagliata
   - SYRUPUSDT gen_98d56766 short -0.87: a favore fino a 0.49R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - SPXUSDT gen_725cb5f4 long -1.26: mai andato a favore (mfe 0.17R): direzione sbagliata
   - PROMUSDT gen_cd5c842f long -1.30: mai andato a favore (mfe 0.20R): direzione sbagliata
   - GPSUSDT gen_8a66a70b long -0.89: mai andato a favore (mfe 0.07R): direzione sbagliata · controtrend rispetto al regime all'ingresso

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte              9/16 -5.53    11/20 -5.07    17/25 +4.74    15/23 +0.46      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_4c6df481        0/1 -1.51      1/1 +2.54              —      1/2 -0.29       0
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48              —       3
  gen_e50a9211        0/1 -0.95              —      1/2 -1.28      1/1 +0.23       0
  gen_490a90e5                —              —              —      2/3 +0.77       4
  gen_658b2edb                —      1/1 +0.62      2/2 +1.52              —       0
  gen_a640dfa5                —              —              —      3/3 +3.58       0
  gen_bb762669                —              —      2/2 +4.89      1/1 +0.28       1
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   5 perdite di fila  (freno spento)
  gen_1f7ead60   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b31d8b93   2 perdite di fila
  gen_bf2be656   2 perdite di fila
  gen_c0fd1d91   2 perdite di fila
  gen_f3124a14   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-09-29 06:02 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fca11c08           6/7             45.68|42.58               1.92|1.05             0.86%|0.75%             72.33|72.21

KEEP PER STRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_cd5c842f          3     2 (rumore 0)        1        -        0.63
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_18c839a0          2     1 (rumore 0)        1        -        0.71
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4465723e          2     1 (rumore 0)        1        -        0.60
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_a640dfa5          2     2 (rumore 0)        0        -        0.73
  gen_bb762669          2     1 (rumore 0)        1        -        0.78
  gen_f238d283          2     0 (rumore 0)        2        -        0.63
  gen_2c248ee9          1     1 (rumore 1)        0        -        0.83
  gen_35632db9          1     1 (rumore 0)        0        -        0.65
  gen_4508a416          1     1 (rumore 0)        0        -        0.47
  gen_49c2f657          1     0 (rumore 0)        1        -        0.74
  gen_4c6df481          1     1 (rumore 1)        0        -        0.61
  gen_4f890271          1     1 (rumore 0)        0        -        0.64
  gen_6191df86          1     1 (rumore 1)        0        -        0.75
  gen_658b2edb          1     1 (rumore 0)        0        -        0.68
  gen_6d06dca0          1     1 (rumore 0)        0        -        0.47
  gen_725cb5f4          1     0 (rumore 0)        1        -        0.90
  gen_8931b93c          1     0 (rumore 0)        1        -        0.76
  gen_8b91ba18          1     0 (rumore 0)        1        -        0.73
  gen_8e475cd9          1     0 (rumore 0)        1        -        0.77
  gen_902fb1fd          1     0 (rumore 0)        1        -        0.78
  gen_919c110c          1     1 (rumore 0)        0        -        0.47
  gen_93131ef1          1     1 (rumore 0)        0        -        0.62
  gen_a22411e3          1     0 (rumore 0)        1        -        0.82
  gen_af734c68          1     1 (rumore 0)        0        -        0.77
  gen_b028553e          1     0 (rumore 0)        1        -        0.77
  gen_b9bf5d01          1     0 (rumore 0)        1        -        0.79
  gen_bf1e00d4          1     1 (rumore 0)        0        -        0.79
  gen_c5194ce4          1     0 (rumore 0)        1        -        0.71
  gen_cde82a91          1     0 (rumore 0)        1        -        0.69
  gen_d53c153b          1     1 (rumore 0)        0        -        0.70
  gen_dfb554f7          1     0 (rumore 0)        1        -        0.68
  gen_e50a9211          1     0 (rumore 0)        1        -        0.74
  gen_e933160c          1     0 (rumore 0)        1        -        0.87
  gen_fb3d971f          1     0 (rumore 0)        1        -        0.47
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 96  (vinti 61, persi 35; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.653   p media dei persi: 0.644   (se p predice, la prima e' piu' alta)
  sopra la soglia: 96/96 trade, PnL -4.01 contro -4.01 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.077
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 168 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.78      56       55%     -0.70%
    0.78-0.90      56       52%     -0.36%
    0.90-1.00      56       55%     -0.44%
  FEAR & GREED all'apertura (168 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         166       54%     -0.52%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     18 trade · 12 vinti · PnL +1.91 · R medio +0.045R su 18
  attive        150 trade · 79 vinti · PnL -71.03 · R medio -0.102R su 111
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 56
  trade chiusi: 6 · vinti 5 · PnL +1.78
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    MUBARAKUSDT|gen_cf6a181e             1 trade · 1 vinti · +0.59
    PHAUSDT|gen_c5194ce4                 1 trade · 1 vinti · +0.65
  coppie esplorative poi validate 1 / scartate 168  (il metro: si legge a 100 trade esplorativi)
```
