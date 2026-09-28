# 0321-28set-trades.req

_eseguito: 2026-09-28 05:34 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 1.9s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 142  (142 con apertura nota)
Giorni coperti:          13
Trade/giorno:            min 1 · media 10.9 · max 33
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 30 · 2026-09-26 21 · 2026-09-27 33 · 2026-09-28 5
Durata media holding:    3.7h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 1.9
Coin distinte:           42
Strategie distinte:      58

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       54   26/54    -25.83         0.84R
short      88   48/88    -43.27         0.87R

Regime ALL'APERTURA x direzione:
  bear_trending      long 12 · short 9
  bull_trending      long 17 · short 40
  high_uncertainty   long 8 · short 23
  sideways           long 17 · short 16

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         26 trade · PnL   -22.11
  CONTROTREND      52 trade · PnL     1.32
  regime neutro    64 trade · PnL   -48.32

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 103 (43 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x43
  classe uscita            x22
  classe ingresso          x21
  controtrend              x15

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
   - DEXEUSDT gen_b31d8b93 short -1.88: a favore fino a 0.81R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - ORCAUSDT gen_fca11c08 short -2.60: a favore fino a 0.48R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - HEMIUSDT gen_6bc43e03 long -1.40: a favore fino a 0.74R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - SYRUPUSDT gen_4c6df481 long -1.51: a favore fino a 0.35R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - SOLUSDT gen_f3124a14 long -2.03: a favore fino a 0.58R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - XMRUSDT gen_35632db9 long -2.39: mai andato a favore (mfe 0.21R): direzione sbagliata

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte              9/16 -5.53      4/8 -1.52     7/11 +1.21    15/23 +0.46      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_4c6df481        0/1 -1.51      1/1 +2.54              —      1/2 -0.29       0
  gen_490a90e5                —              —              —      2/3 +0.77       4
  gen_a640dfa5                —              —              —      3/3 +3.58       0
  gen_887d87df        2/2 +0.37              —              —              —       0
  gen_8b91ba18        1/2 -0.70              —              —              —       0
  gen_c0fd1d91                —      0/1 -2.40              —      0/1 -2.39       0
  gen_cd5c842f                —      1/1 +1.61      1/1 +4.48              —       3
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
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-09-28 05:32 UTC): decided — parita' backtest: 1 segnali validi aperti
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
  gen_18c839a0          2     1 (rumore 0)        1        -        0.71
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_a640dfa5          2     2 (rumore 0)        0        -        0.73
  gen_cd5c842f          2     2 (rumore 0)        0        -        0.64
  gen_f238d283          2     0 (rumore 0)        2        -        0.63
  gen_14e1775b          1     0 (rumore 0)        1        -        0.77
  gen_2c248ee9          1     1 (rumore 1)        0        -        0.83
  gen_35632db9          1     1 (rumore 0)        0        -        0.65
  gen_4465723e          1     0 (rumore 0)        1        -        0.64
  gen_49c2f657          1     0 (rumore 0)        1        -        0.74
  gen_4c6df481          1     1 (rumore 1)        0        -        0.61
  gen_4f890271          1     1 (rumore 0)        0        -        0.64
  gen_658b2edb          1     1 (rumore 0)        0        -        0.68
  gen_6d06dca0          1     1 (rumore 0)        0        -        0.47
  gen_8b91ba18          1     0 (rumore 0)        1        -        0.73
  gen_8e475cd9          1     0 (rumore 0)        1        -        0.77
  gen_919c110c          1     1 (rumore 0)        0        -        0.47
  gen_93131ef1          1     1 (rumore 0)        0        -        0.62
  gen_a22411e3          1     0 (rumore 0)        1        -        0.82
  gen_af734c68          1     1 (rumore 0)        0        -        0.77
  gen_b028553e          1     0 (rumore 0)        1        -        0.77
  gen_b9bf5d01          1     0 (rumore 0)        1        -        0.79
  gen_bb762669          1     0 (rumore 0)        1        -        0.82
  gen_bf1e00d4          1     1 (rumore 0)        0        -        0.79
  gen_cde82a91          1     0 (rumore 0)        1        -        0.69
  gen_d53c153b          1     1 (rumore 0)        0        -        0.70
  gen_e50a9211          1     0 (rumore 0)        1        -        0.74
  gen_fb3d971f          1     0 (rumore 0)        1        -        0.47
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 70  (vinti 44, persi 26; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.653   p media dei persi: 0.632   (se p predice, la prima e' piu' alta)
  sopra la soglia: 70/70 trade, PnL -3.99 contro -3.99 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.163
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 142 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.79      47       49%     -0.97%
    0.79-0.91      47       55%     -0.21%
    0.91-1.00      48       52%     -0.57%
  FEAR & GREED all'apertura (142 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         140       52%     -0.61%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  nessun trade chiuso da una declassata (il gate non ne ha ancora scritte, o il bot non le ha ancora operate)
  declassate      0 trade · 0 vinti · PnL +0.00 · R medio n/d
  attive        142 trade · 74 vinti · PnL -69.10 · R medio -0.112R su 103
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 56
  trade chiusi: 2 · vinti 1 · PnL -0.21
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    XRPUSDT|gen_50905b4a                 1 trade · 0 vinti · -0.39
  coppie esplorative poi validate 1 / scartate 122  (il metro: si legge a 100 trade esplorativi)
```
