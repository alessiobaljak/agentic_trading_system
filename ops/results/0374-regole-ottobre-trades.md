# 0374-regole-ottobre-trades.req

_eseguito: 2026-09-30 11:21 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 2.7s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 185  (185 con apertura nota)
Giorni coperti:          15
Trade/giorno:            min 1 · media 12.3 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 6
Durata media holding:    3.5h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 2.0
Coin distinte:           52
Strategie distinte:      76

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       78   41/78    -30.27         0.84R
short     107  61/107    -41.15         0.90R

Regime ALL'APERTURA x direzione:
  bear_trending      long 17 · short 18
  bull_trending      long 23 · short 42
  high_uncertainty   long 14 · short 28
  sideways           long 24 · short 19

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         41 trade · PnL   -14.23
  CONTROTREND      59 trade · PnL     1.22
  regime neutro    85 trade · PnL   -58.40

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 146 (58 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x58
  classe ingresso          x32
  classe uscita            x26
  controtrend              x18

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_fa304106     6     0     6   -11.15     1/  1/   0          0        2           0
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_ba3a671f     6     1     5   -17.27     1/  0/   0          0        1           1
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_b31d8b93     4     1     3    -5.10     1/  1/   0          0        2           0
  gen_1f7ead60     2     0     2   -10.66     1/  0/   0          0        1           0
  gen_490a90e5     7     5     2     1.21     2/  0/   0          0        2           1
  ultimi referti in perdita:
   - FLOCKUSDT gen_c5194ce4 short -1.37: mai andato a favore (mfe 0.00R): direzione sbagliata
   - UBUSDT gen_f3661202 long -1.66: mai andato a favore (mfe 0.02R): direzione sbagliata
   - GALAUSDT gen_b9aa9989 long -2.66: mai andato a favore (mfe 0.01R): direzione sbagliata
   - RAYSOLUSDT gen_fa304106 long -1.24: mai andato a favore (mfe 0.06R): direzione sbagliata
   - AIOUSDT gen_581d4a68 long -1.32: mai andato a favore (mfe 0.13R): direzione sbagliata
   - STXUSDT gen_a5b0e4de short -1.59: a favore fino a 0.89R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte             13/23 -7.63    15/25 -3.86    18/28 +2.44    17/25 +1.36      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_4c6df481        0/1 -1.51      1/1 +2.54              —      1/2 -0.29       0
  gen_bb762669        1/1 +2.10              —      2/2 +4.89      1/1 +0.28       1
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48              —       3
  gen_e50a9211        0/1 -0.95              —      1/2 -1.28      1/1 +0.23       0
  gen_e59ad90b                —      1/2 -3.25      1/1 +3.89      1/1 +0.47       0
  gen_490a90e5                —              —              —      2/3 +0.77       4
  gen_658b2edb                —      1/1 +0.62      2/2 +1.52              —       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   6 perdite di fila  (freno spento)
  gen_1f7ead60   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b31d8b93   2 perdite di fila
  gen_bf2be656   2 perdite di fila
  gen_c0fd1d91   2 perdite di fila
  gen_c5194ce4   2 perdite di fila
  gen_f3124a14   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-09-30 11:17 UTC): flat — nessun segnale valido sopra soglia
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
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_bb762669          3     2 (rumore 0)        1        -        0.73
  gen_cd5c842f          3     2 (rumore 0)        1        -        0.63
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_18c839a0          2     1 (rumore 0)        1        -        0.71
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4465723e          2     1 (rumore 0)        1        -        0.60
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_a640dfa5          2     2 (rumore 0)        0        -        0.73
  gen_e59ad90b          2     2 (rumore 1)        0        -        0.78
  gen_f238d283          2     0 (rumore 0)        2        -        0.63
  gen_f3661202          2     0 (rumore 0)        2        -        0.81
  gen_2c248ee9          1     1 (rumore 1)        0        -        0.83
  gen_35632db9          1     1 (rumore 0)        0        -        0.65
  gen_4508a416          1     1 (rumore 0)        0        -        0.47
  gen_4810faab          1     0 (rumore 0)        1        -        0.81
  gen_49c2f657          1     0 (rumore 0)        1        -        0.74
  gen_4c6df481          1     1 (rumore 1)        0        -        0.61
  gen_4f890271          1     1 (rumore 0)        0        -        0.64
  gen_6191df86          1     1 (rumore 1)        0        -        0.75
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
  gen_b922252e          1     0 (rumore 0)        1        -        0.79
  gen_b9bf5d01          1     0 (rumore 0)        1        -        0.79
  gen_bf1e00d4          1     1 (rumore 0)        0        -        0.79
  gen_c5194ce4          1     0 (rumore 0)        1        -        0.71
  gen_cde82a91          1     0 (rumore 0)        1        -        0.69
  gen_cf6a181e          1     1 (rumore 0)        0        -        0.70
  gen_d53c153b          1     1 (rumore 0)        0        -        0.70
  gen_dfb554f7          1     0 (rumore 0)        1        -        0.68
  gen_e50a9211          1     0 (rumore 0)        1        -        0.74
  gen_e933160c          1     0 (rumore 0)        1        -        0.87
  gen_fb3d971f          1     0 (rumore 0)        1        -        0.47
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 113  (vinti 72, persi 41; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.651   p media dei persi: 0.643   (se p predice, la prima e' piu' alta)
  sopra la soglia: 113/113 trade, PnL -6.30 contro -6.30 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.065
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 185 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.76      61       56%     -0.66%
    0.78-0.89      61       54%     -0.28%
    0.89-1.00      63       56%     -0.42%
  FEAR & GREED all'apertura (185 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         183       55%     -0.47%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     28 trade · 20 vinti · PnL +2.92 · R medio +0.080R su 28
  attive        157 trade · 82 vinti · PnL -74.34 · R medio -0.122R su 118
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard per giornata.
  dal 27 set 19:40 UTC: declassate 28 trade R +0.080 · attive 22 trade R +0.064 · differenza +0.015R, margine ±0.452R -> NON SI DECIDE

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 25
  trade chiusi: 7 · vinti 6 · PnL +2.67
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    MUBARAKUSDT|gen_cf6a181e             1 trade · 1 vinti · +0.59
    PHAUSDT|gen_2b41880d                 1 trade · 1 vinti · +0.89
  coppie esplorative poi validate 0 / scartate 200  (il metro: si legge a 100 trade esplorativi)
```
