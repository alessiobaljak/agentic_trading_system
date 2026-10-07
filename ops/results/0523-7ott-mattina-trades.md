# 0523-7ott-mattina-trades.req

_eseguito: 2026-10-07 06:05 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 5.8s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 332  (332 con apertura nota)
Giorni coperti:          22
Trade/giorno:            min 1 · media 15.1 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 17
Durata media holding:    3.6h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 12 · media nel tempo 2.4
Coin distinte:           73
Strategie distinte:      118

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      163  87/163    -49.37         0.77R
short     169  96/169    -40.41         0.87R

Regime ALL'APERTURA x direzione:
  bear_trending      long 45 · short 31
  bull_trending      long 34 · short 58
  high_uncertainty   long 22 · short 35
  sideways           long 62 · short 45

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         65 trade · PnL   -14.01
  CONTROTREND     103 trade · PnL    -0.16
  regime neutro   164 trade · PnL   -75.61

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     293  -0.115  -33.66  39 ‖  197  -0.091  -17.91   0
    lordo           293  -0.021   -6.26  39 ‖  197  +0.007   +1.45   0
    costi stimati   293  +0.094  +27.41  39 ‖  197  +0.098  +19.36   0
 direzione
  long              147  -0.191  -28.07  16 ‖  112  -0.163  -18.28   0
  short             146  -0.038   -5.59  23 ‖   85  +0.004   +0.37   0
 regime all'apertura
  bull_trending      77  -0.166  -12.77  15 ‖   36  -0.179   -6.44   0
  bear_trending      70  +0.023   +1.63   6 ‖   59  +0.062   +3.68   0
  sideways          102  -0.122  -12.44   5 ‖   76  -0.067   -5.12   0
  high_uncertainty   44  -0.229  -10.09  13 ‖   26  -0.386  -10.04   0
 rispetto al trend
  in trend           57  -0.024   -1.39   8 ‖   42  +0.097   +4.06   0
  CONTROTREND        90  -0.108   -9.74  13 ‖   53  -0.129   -6.82   0
  regime neutro     146  -0.154  -22.53  18 ‖  102  -0.149  -15.15   0
 direzione x BTC (con = nel verso di BTC)
  long_con           69  -0.177  -12.20   0 ‖   55  -0.133   -7.31   0
  long_contro        64  -0.198  -12.66   0 ‖   57  -0.192  -10.97   0
  short_con          48  -0.048   -2.31   0 ‖   38  -0.058   -2.22   0
  short_contro       67  +0.009   +0.62   0 ‖   47  +0.055   +2.59   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       11  +0.043   +0.48   0 ‖    9  +0.146   +1.31   0
  gen_e59ad90b       10  -0.125   -1.25   0 ‖    9  -0.280   -2.52   0
  gen_fa304106        6  -1.049   -6.30   4 ‖    5  -1.042   -5.21   0
  gen_cd5c842f        7  +0.206   +1.44   2 ‖    5  -0.060   -0.30   0
  gen_4465723e        6  +0.246   +1.48   2 ‖    4  +0.129   +0.51   0
  gen_ceab7f6a        8  -0.493   -3.95   0 ‖    8  -0.493   -3.95   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  altre 110         229  -0.102  -23.33  26 ‖  157  -0.049   -7.76   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 293 (124 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x124
  classe uscita            x62
  classe ingresso          x62
  controtrend              x37

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    10     0    10   -15.50     4/  2/   0          0        6           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_ceab7f6a     8     3     5    -4.22     3/  2/   0          0        5           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_bb762669    11     7     4     5.83     2/  2/   0          0        4           0
  gen_e59ad90b    10     6     4    -0.27     3/  1/   0          0        4           3
  ultimi referti in perdita:
   - PTBUSDT gen_684d7623 long -1.77: mai andato a favore (mfe 0.00R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - DOTUSDT gen_60c9259a long -0.88: mai andato a favore (mfe 0.00R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - KERNELUSDT gen_c647ead7 long -1.89: a favore fino a 0.75R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - CVCUSDT gen_4c4dac5f long -0.91: a favore fino a 0.30R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - PROMUSDT gen_cd5c842f short -0.76: a favore fino a 0.46R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - BMTUSDT gen_571cdda2 long -1.62: a favore fino a 0.55R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)

PAPER CONTRO IL CASO (K4): il paper (332 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 147)     47/52%  48.5/51.5%
  massimo toccato mediano            0.82R       0.81R
  arrivati al primo target             12%         17%
  vinti                                55%         54%
  R medio (su 293)                  -0.115      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            38/69 -15.45   36/64 -15.13    28/48 -0.80    42/67 +5.34      84
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/6 +2.68       1
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_ceab7f6a        3/7 -3.25      0/1 -0.97              —              —       0
  gen_4c6df481        2/3 +3.30      1/2 -0.70              —      1/2 -0.29       0
  gen_a640dfa5                —              —              —      4/6 +1.26       0
  gen_cd5c842f                —      2/3 +1.09      1/2 +3.72      1/1 +0.95       3
  gen_4465723e        1/1 +1.88      2/3 -0.08      1/1 +0.78              —       3
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   10 perdite di fila  (freno spento)
  gen_bf2be656   3 perdite di fila
  gen_c5194ce4   3 perdite di fila
  gen_ceab7f6a   3 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_4f890271   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_a640dfa5   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-07 06:03 UTC): decided — parita' backtest: 2 segnali validi aperti
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3)
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_c5194ce4: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3)
  - gen_c5194ce4: solo_long — short 3/3 persi (campione 3)
  - gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4)
  - gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)
  - gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - gen_fa304106: solo_short — long 5/5 persi (campione 5)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fa304106           4/0               37.26|n/d                1.10|n/d               1.12%|n/d

[... 161 caratteri omessi (testa e coda conservate) ...]

TRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_4465723e          4     2 (rumore 0)        2        -        0.61
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_4c6df481          4     3 (rumore 3)        1        -        0.69
  gen_cd5c842f          4     2 (rumore 0)        2        -        0.57
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_8981d5f2          3     1 (rumore 1)        2        -        0.66
  gen_902fb1fd          3     1 (rumore 0)        2        -        0.77
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  gen_c647ead7          3     2 (rumore 0)        1        -        0.70
  gen_dfb554f7          3     1 (rumore 0)        2        -        0.72
  gen_f3661202          3     1 (rumore 1)        2        -        0.80
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_1f7ead60          2     2 (rumore 1)        0        -        0.78
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_2c248ee9          2     1 (rumore 1)        1        -        0.78
  + altre 54 strategie con meno verdetti: 71 verdetti, prematuri 33, protetti 38
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 260  (vinti 153, persi 107; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.650   p media dei persi: 0.641   (se p predice, la prima e' piu' alta)
  sopra la soglia: 260/260 trade, PnL -24.67 contro -24.67 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.076
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 332 trade): verdetto piatta (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.76     110       56%     -0.40%
    0.76-0.89     110       55%     -0.26%
    0.89-1.00     112       55%     -0.42%
  FEAR & GREED all'apertura (331 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         329       55%     -0.37%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    139 trade · 78 vinti · PnL -15.53 · R medio -0.129R su 139
  attive        193 trade · 105 vinti · PnL -74.25 · R medio -0.103R su 154
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 139 trade R -0.129 · attive 58 trade R -0.001 · differenza -0.128R, margine ±0.305R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   127  ‖            100   -0.100 ‖          72   -0.102
  ALLENTATA                            7  ‖             15   +0.248 ‖          10   +0.176
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               145  ‖            130   -0.129 ‖         111   -0.114
  trade di coppie non piu' validate       ‖             48   -0.222 ‖           4   +0.088
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -89.78   +0.00   8.98%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -84.69   +5.09   8.47%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -87.77   +2.01   8.78%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -87.77   +2.01   8.78%       0       9        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -86.90   +2.88   8.69%       0      15        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -84.21   +5.57   8.42%       0      21        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -76.08  +13.70   7.61%       0      51        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          185    102   -39.81   -0.089
  3-5          131     70   -51.16   -0.172
  6+            16     11    +1.19   +0.076
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 244 a -0.103R · altri 49 a -0.173R · diff +0.070 ±0.267 -> NON SI VEDE ANCORA
    a size piena sugli stessi 130 trade: +19.38 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 2 a -0.304R · altri 291 a -0.114R -> CAMPIONE PICCOLO
    a size piena sugli stessi 2 trade: -0.07 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 68 a -0.131R · altri 27 a -0.196R · diff +0.065 ±0.459 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 76 a -0.089R · altri 217 a -0.124R · diff +0.035 ±0.244 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 78 a -0.129R · altri 166 a -0.091R · diff -0.038 ±0.247 -> NON SI VEDE ANCORA
    a size piena sugli stessi 51 trade: +0.51 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 139 a -0.129R · altri 154 a -0.103R · diff -0.026 ±0.210 -> NON SI VEDE ANCORA
    a size piena sugli stessi 120 trade: +37.52 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 13 a +0.146R · altri 293 a -0.115R · diff +0.261 ±0.449 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 5 trade -0.068R · casuali 285 trade -0.110R · intorno 3 trade -0.669R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 36
  trade chiusi: 13 · vinti 10 · PnL +1.75
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_8aec28c6                 1 trade · 0 vinti · -0.99
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
  coppie esplorative poi validate 4 / scartate 442  (il metro: si legge a 100 trade esplorativi)
```
