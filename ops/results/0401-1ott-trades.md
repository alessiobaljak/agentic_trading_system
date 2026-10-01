# 0401-1ott-trades.req

_eseguito: 2026-10-01 09:11 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 2.8s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 201  (201 con apertura nota)
Giorni coperti:          16
Trade/giorno:            min 1 · media 12.6 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 8
Durata media holding:    3.5h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 2.0
Coin distinte:           54
Strategie distinte:      81

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       87   45/87    -36.61         0.81R
short     114  64/114    -43.74         0.89R

Regime ALL'APERTURA x direzione:
  bear_trending      long 18 · short 19
  bull_trending      long 25 · short 45
  high_uncertainty   long 17 · short 28
  sideways           long 27 · short 22

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         44 trade · PnL   -11.71
  CONTROTREND      63 trade · PnL    -0.25
  regime neutro    94 trade · PnL   -68.39

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     162  -0.115  -18.64  39 ‖   66  -0.044   -2.89   0
    lordo           162  -0.034   -5.50  39 ‖   66  +0.033   +2.20   0
    costi stimati   162  +0.081  +13.14  39 ‖   66  +0.077   +5.09   0
 direzione
  long               71  -0.211  -14.96  16 ‖   36  -0.144   -5.17   0
  short              91  -0.040   -3.68  23 ‖   30  +0.076   +2.28   0
 regime all'apertura
  bull_trending      55  -0.175   -9.60  15 ‖   14  -0.234   -3.28   0
  bear_trending      31  +0.259   +8.04   6 ‖   20  +0.504  +10.09   0
  sideways           44  -0.225   -9.90   5 ‖   18  -0.143   -2.57   0
  high_uncertainty   32  -0.225   -7.18  13 ‖   14  -0.509   -7.13   0
 rispetto al trend
  in trend           36  +0.080   +2.88   8 ‖   21  +0.397   +8.34   0
  CONTROTREND        50  -0.089   -4.45  13 ‖   13  -0.117   -1.53   0
  regime neutro      76  -0.225  -17.08  18 ‖   32  -0.303   -9.70   0
 direzione x BTC (con = nel verso di BTC)
  long_con           29  -0.320   -9.28   0 ‖   15  -0.293   -4.39   0
  long_contro        28  -0.088   -2.46   0 ‖   21  -0.037   -0.78   0
  short_con          31  +0.016   +0.49   0 ‖   21  +0.027   +0.57   0
  short_contro       29  -0.009   -0.26   0 ‖    9  +0.190   +1.71   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  gen_490a90e5        7  -0.031   -0.22   0 ‖    0       —       —   0
  gen_cd5c842f        5  +0.330   +1.65   2 ‖    3  -0.030   -0.09   0
  gen_fa304106        3  -1.052   -3.16   4 ‖    2  -1.035   -2.07   0
  gen_4465723e        4  +0.489   +1.95   2 ‖    2  +0.495   +0.99   0
  gen_6d06dca0        2  -0.186   -0.37   4 ‖    0       —       —   0
  gen_ba3a671f        2  -0.219   -0.44   4 ‖    0       —       —   0
  altre 73          123  -0.129  -15.82  18 ‖   59  -0.029   -1.72   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 162 (67 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x67
  classe ingresso          x36
  classe uscita            x31
  controtrend              x20

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106     7     0     7   -12.46     2/  1/   0          0        3           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_ba3a671f     6     1     5   -17.27     1/  0/   0          0        1           1
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_b31d8b93     4     1     3    -5.10     1/  1/   0          0        2           0
  gen_c0fd1d91     3     0     3    -6.10     2/  1/   0          0        3           1
  gen_1f7ead60     2     0     2   -10.66     1/  0/   0          0        1           0
  ultimi referti in perdita:
   - PHAUSDT gen_fa304106 long -1.31: mai andato a favore (mfe 0.08R): direzione sbagliata
   - MITOUSDT gen_8b91ba18 short -1.64: a favore fino a 0.62R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - ORCAUSDT gen_cb8176f2 short -0.93: a favore fino a 0.41R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - ZORAUSDT gen_ceab7f6a long -1.32: mai andato a favore (mfe 0.00R): direzione sbagliata
   - JASMYUSDT gen_b2f350ff short -1.36: mai andato a favore (mfe 0.17R): direzione sbagliata
   - USELESSUSDT gen_c0fd1d91 long -1.32: a favore fino a 0.40R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)

PAPER CONTRO IL CASO (K4): il paper (201 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  46%         46%
  stop ingresso/uscita (su 92)      47/52%  48.5/51.5%
  massimo toccato mediano            0.84R       0.81R
  arrivati al primo target             13%         17%
  vinti                                54%         54%
  R medio (su 162)                  -0.115      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            15/29 -13.92    17/28 -3.90    19/31 +0.40    19/29 +0.80      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_4c6df481        0/1 -1.51      1/1 +2.54              —      1/2 -0.29       0
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
  gen_bb762669        1/1 +2.10              —      2/2 +4.89      1/1 +0.28       1
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48              —       3
  gen_e50a9211        0/1 -0.95              —      1/2 -1.28      1/1 +0.23       0
  gen_e59ad90b                —      1/2 -3.25      1/1 +3.89      1/1 +0.47       0
  gen_4465723e        1/1 +1.88      1/1 +0.43      1/1 +0.78              —       3
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   7 perdite di fila  (freno spento)
  gen_c0fd1d91   3 perdite di fila
  gen_1f7ead60   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b2f350ff   2 perdite di fila
  gen_b31d8b93   2 perdite di fila
  gen_bf2be656   2 perdite di fila
  gen_c5194ce4   2 perdite di fila
  gen_f3124a14   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-01 09:02 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)
  - gen_fa304106: solo_short — long 3/3 persi (campione 3)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fca11c08           6/7             45.68|42.58               1.92|1.05             0.86%|0.75%             72.33|72.21

KEEP PER STRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4465723e          3     2 (rumore 0)        1        -        0.63
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_bb762669          3     2 (rumore 0)        1        -        0.73
  gen_cd5c842f          3     2 (rumore 0)        1        -        0.63
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_18c839a0          2     1 (rumore 0)        1        -        0.71
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4f890271          2     2 (rumore 0)        0        -        0.55
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_a640dfa5          2     2 (rumore 0)        0        -        0.73
  gen_e59ad90b          2     2 (rumore 1)        0        -        0.78
  gen_f238d283          2     0 (rumore 0)        2        -        0.63
  gen_f3661202          2     0 (rumore 0)        2        -        0.81
  + altre 33 strategie con meno verdetti: 33 verdetti, prematuri 15, protetti 18
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 129  (vinti 79, persi 50; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.651   p media dei persi: 0.643   (se p predice, la prima e' piu' alta)
  sopra la soglia: 129/129 trade, PnL -15.24 contro -15.24 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.066
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 201 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.78      67       54%     -0.74%
    0.78-0.90      67       57%     -0.24%
    0.90-1.00      67       52%     -0.58%
  FEAR & GREED all'apertura (201 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         199       54%     -0.53%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     42 trade · 26 vinti · PnL -5.09 · R medio -0.093R su 42
  attive        159 trade · 83 vinti · PnL -75.26 · R medio -0.123R su 120
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 42 trade R -0.093 · attive 24 trade R +0.042 · differenza -0.135R, margine ±0.416R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 54
  trade chiusi: 8 · vinti 7 · PnL +2.97
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    HEMIUSDT|gen_f4c1300a                1 trade · 1 vinti · +0.30
    MUBARAKUSDT|gen_cf6a181e             1 trade · 1 vinti · +0.59
  coppie esplorative poi validate 0 / scartate 200  (il metro: si legge a 100 trade esplorativi)
```
