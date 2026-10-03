# 0445-3ott-mattina-trades.req

_eseguito: 2026-10-03 06:04 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 4.3s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 238  (238 con apertura nota)
Giorni coperti:          18
Trade/giorno:            min 1 · media 13.2 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 7
Durata media holding:    3.7h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 2.2
Coin distinte:           61
Strategie distinte:      91

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      110  58/110    -37.83         0.82R
short     128  73/128    -38.82         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 24 · short 23
  bull_trending      long 27 · short 49
  high_uncertainty   long 20 · short 31
  sideways           long 39 · short 25

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         50 trade · PnL    -8.14
  CONTROTREND      73 trade · PnL     0.66
  regime neutro   115 trade · PnL   -69.17

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     199  -0.104  -20.71  39 ‖  103  -0.048   -4.96   0
    lordo           199  -0.023   -4.63  39 ‖  103  +0.030   +3.07   0
    costi stimati   199  +0.081  +16.08  39 ‖  103  +0.078   +8.03   0
 direzione
  long               94  -0.174  -16.38  16 ‖   59  -0.112   -6.58   0
  short             105  -0.041   -4.33  23 ‖   44  +0.037   +1.62   0
 regime all'apertura
  bull_trending      61  -0.168  -10.24  15 ‖   20  -0.196   -3.92   0
  bear_trending      41  +0.208   +8.53   6 ‖   30  +0.353  +10.58   0
  sideways           59  -0.199  -11.72   5 ‖   33  -0.133   -4.40   0
  high_uncertainty   38  -0.191   -7.27  13 ‖   20  -0.361   -7.22   0
 rispetto al trend
  in trend           42  +0.102   +4.29   8 ‖   27  +0.361   +9.75   0
  CONTROTREND        60  -0.100   -6.01  13 ‖   23  -0.134   -3.09   0
  regime neutro      97  -0.196  -19.00  18 ‖   53  -0.219  -11.62   0
 direzione x BTC (con = nel verso di BTC)
  long_con           52  -0.206  -10.70   0 ‖   38  -0.153   -5.80   0
  long_contro        28  -0.088   -2.46   0 ‖   21  -0.037   -0.78   0
  short_con          32  +0.029   +0.94   0 ‖   22  +0.046   +1.02   0
  short_contro       42  -0.032   -1.36   0 ‖   22  +0.027   +0.60   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669        8  +0.054   +0.43   0 ‖    6  +0.211   +1.27   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  gen_490a90e5        7  -0.031   -0.22   0 ‖    0       —       —   0
  gen_ba3a671f        3  -0.508   -1.52   4 ‖    1  -1.086   -1.09   0
  gen_cd5c842f        5  +0.330   +1.65   2 ‖    3  -0.030   -0.09   0
  gen_fa304106        3  -1.052   -3.16   4 ‖    2  -1.035   -2.07   0
  gen_4465723e        4  +0.489   +1.95   2 ‖    2  +0.495   +0.99   0
  altre 83          153  -0.115  -17.60  22 ‖   89  -0.045   -3.97   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 199 (82 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x82
  classe ingresso          x44
  classe uscita            x38
  controtrend              x25

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106     7     0     7   -12.46     2/  1/   0          0        3           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_b31d8b93     4     1     3    -5.10     1/  1/   0          0        2           0
  gen_c0fd1d91     3     0     3    -6.10     2/  1/   0          0        3           1
  gen_c5194ce4     3     0     3    -3.89     3/  0/   0          0        3           0
  ultimi referti in perdita:
   - CROSSUSDT gen_d606fde3 long -0.34: a favore fino a 0.44R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - SPXUSDT gen_ba3a671f long -1.61: a favore fino a 0.37R ma sotto il primo gradino (0.75R) · il lock non si e' mai armato (serviva 0.38R)
   - BANKUSDT gen_fb3d971f long -1.15: mai andato a favore (mfe 0.14R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - VETUSDT gen_b9c251a1 long -1.26: mai andato a favore (mfe 0.00R): direzione sbagliata
   - FLOCKUSDT gen_c5194ce4 short -1.26: mai andato a favore (mfe 0.20R): direzione sbagliata
   - USELESSUSDT gen_194e2514 long -1.22: a favore fino a 0.40R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)

PAPER CONTRO IL CASO (K4): il paper (238 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 106)     48/51%  48.5/51.5%
  massimo toccato mediano            0.84R       0.81R
  arrivati al primo target             13%         17%
  vinti                                55%         54%
  R medio (su 199)                  -0.104      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            28/52 -15.15    17/28 -3.90    20/32 +1.07    27/42 +5.05      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      3/3 +2.01       1
  gen_4c6df481        2/3 +3.30      1/1 +2.54              —      1/2 -0.29       0
  gen_e59ad90b                —      1/2 -3.25      1/1 +3.89      2/3 +0.06       0
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
  gen_a640dfa5                —              —              —      4/4 +4.60       0
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48              —       3
  gen_e50a9211        0/1 -0.95              —      1/2 -1.28      1/1 +0.23       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   7 perdite di fila  (freno spento)
  gen_c0fd1d91   3 perdite di fila
  gen_c5194ce4   3 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_1f7ead60   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b2f350ff   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-03 06:02 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_c5194ce4: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3)
  - gen_c5194ce4: solo_long — short 3/3 persi (campione 3)
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)
  - gen_fa304106: solo_short — long 3/3 persi (campione 3)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fca11c08           6/7             45.68|42.58               1.92|1.05             0.86%|0.75%             72.33|72.21

KEEP PER STRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4465723e          3     2 (rumore 0)        1        -        0.63
  gen_4c6df481          3     3 (rumore 3)        0        -        0.64
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  gen_cd5c842f          3     2 (rumore 0)        1        -        0.63
  gen_e59ad90b          3     2 (rumore 1)        1        -        0.79
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4810faab          2     0 (rumore 0)        2        -        0.77
  gen_4f890271          2     2 (rumore 0)        0        -        0.55
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_8981d5f2          2     0 (rumore 0)        2        -        0.65
  gen_919c110c          2     2 (rumore 0)        0        -        0.54
  + altre 36 strategie con meno verdetti: 40 verdetti, prematuri 16, protetti 24
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 166  (vinti 101, persi 65; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.649   p media dei persi: 0.648   (se p predice, la prima e' piu' alta)
  sopra la soglia: 166/166 trade, PnL -11.54 contro -11.54 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.003
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 238 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.74      79       54%     -0.63%
    0.76-0.89      79       56%     -0.33%
    0.89-1.00      80       55%     -0.41%
  FEAR & GREED all'apertura (238 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         236       55%     -0.47%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     70 trade · 41 vinti · PnL -9.91 · R medio -0.131R su 70
  attive        168 trade · 90 vinti · PnL -66.74 · R medio -0.090R su 129
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 70 trade R -0.131 · attive 33 trade R +0.127 · differenza -0.258R, margine ±0.458R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                    79  ‖             63   -0.008 ‖          35   +0.061
  ALLENTATA                            7  ‖             11   +0.244 ‖           6   +0.121
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               130  ‖             80   -0.157 ‖          61   -0.139
  trade di coppie non piu' validate       ‖             45   -0.230 ‖           1   +0.666
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -76.65   +0.00   8.35%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -71.56   +5.09   7.84%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -74.65   +2.00   8.15%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -76.16   +0.49   8.30%       0       6        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -74.04   +2.61   8.09%       0      11        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -68.87   +7.78   7.42%       0      18        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -63.41  +13.24   6.81%       0      40        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          137     74   -39.66   -0.100
  3-5           90     49   -37.38   -0.125
  6+            11      8    +0.39   +0.026
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 18:47  long    8 aperture  PnL +4.27

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 150 a -0.082R · altri 49 a -0.173R · diff +0.091 ±0.277 -> NON SI VEDE ANCORA
    a size piena sugli stessi 74 trade: +10.84 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 1 a +0.435R · altri 198 a -0.107R -> CAMPIONE PICCOLO
    a size piena sugli stessi 1 trade: -0.64 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 34 a -0.040R · altri 16 a -0.248R · diff +0.208 ±0.516 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 43 a -0.006R · altri 156 a -0.131R · diff +0.125 ±0.277 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 45 a -0.107R · altri 105 a -0.071R · diff -0.036 ±0.306 -> NON SI VEDE ANCORA
    a size piena sugli stessi 30 trade: -1.14 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 70 a -0.131R · altri 129 a -0.090R · diff -0.041 ±0.245 -> NON SI VEDE ANCORA
    a size piena sugli stessi 66 trade: +29.04 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 8 a +0.346R · altri 199 a -0.104R -> CAMPIONE PICCOLO
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): casuali 198 trade -0.106R · intorno 1 trade +0.292R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 47
  trade chiusi: 8 · vinti 7 · PnL +2.97
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    HEMIUSDT|gen_f4c1300a                1 trade · 1 vinti · +0.30
    MUBARAKUSDT|gen_cf6a181e             1 trade · 1 vinti · +0.59
  coppie esplorative poi validate 2 / scartate 294  (il metro: si legge a 100 trade esplorativi)
```
