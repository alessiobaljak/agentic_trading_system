# 0489-5ott-mattina-trades.req

_eseguito: 2026-10-05 06:04 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 5.0s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 280  (280 con apertura nota)
Giorni coperti:          20
Trade/giorno:            min 1 · media 14.0 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 13
Durata media holding:    3.8h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 12 · media nel tempo 2.4
Coin distinte:           68
Strategie distinte:      107

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      130  71/130    -37.24         0.84R
short     150  85/150    -41.70         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 26 · short 23
  bull_trending      long 30 · short 53
  high_uncertainty   long 21 · short 34
  sideways           long 53 · short 40

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         53 trade · PnL    -8.27
  CONTROTREND      79 trade · PnL     4.82
  regime neutro   148 trade · PnL   -75.50

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     241  -0.089  -21.44  39 ‖  145  -0.039   -5.68   0
    lordo           241  -0.001   -0.19  39 ‖  145  +0.052   +7.52   0
    costi stimati   241  +0.088  +21.25  39 ‖  145  +0.091  +13.20   0
 direzione
  long              114  -0.132  -15.07  16 ‖   79  -0.067   -5.27   0
  short             127  -0.050   -6.37  23 ‖   66  -0.006   -0.41   0
 regime all'apertura
  bull_trending      68  -0.133   -9.07  15 ‖   27  -0.102   -2.74   0
  bear_trending      43  +0.224   +9.63   6 ‖   32  +0.365  +11.68   0
  sideways           88  -0.118  -10.35   5 ‖   62  -0.049   -3.02   0
  high_uncertainty   42  -0.277  -11.65  13 ‖   24  -0.483  -11.59   0
 rispetto al trend
  in trend           45  +0.078   +3.53   8 ‖   30  +0.299   +8.98   0
  CONTROTREND        66  -0.045   -2.97  13 ‖   29  -0.002   -0.05   0
  regime neutro     130  -0.169  -21.99  18 ‖   86  -0.170  -14.61   0
 direzione x BTC (con = nel verso di BTC)
  long_con           64  -0.123   -7.89   0 ‖   50  -0.060   -3.00   0
  long_contro        36  -0.110   -3.96   0 ‖   29  -0.078   -2.27   0
  short_con          39  +0.079   +3.08   0 ‖   29  +0.109   +3.16   0
  short_contro       57  -0.097   -5.53   0 ‖   37  -0.096   -3.57   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       10  +0.152   +1.52   0 ‖    8  +0.295   +2.36   0
  gen_e59ad90b        8  +0.117   +0.94   0 ‖    7  -0.048   -0.34   0
  gen_fa304106        4  -1.050   -4.20   4 ‖    3  -1.038   -3.11   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  gen_490a90e5        7  -0.031   -0.22   0 ‖    0       —       —   0
  gen_4c6df481        7  +0.114   +0.80   0 ‖    4  +0.329   +1.31   0
  gen_ba3a671f        3  -0.508   -1.52   4 ‖    1  -1.086   -1.09   0
  altre 99          186  -0.089  -16.51  26 ‖  122  -0.040   -4.82   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 241 (99 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x99
  classe ingresso          x50
  classe uscita            x49
  controtrend              x26

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106     8     0     8   -12.94     3/  1/   0          0        4           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_4c6df481     7     4     3     2.32     1/  2/   0          0        3           0
  gen_b31d8b93     4     1     3    -5.10     1/  1/   0          0        2           0
  gen_bb762669    10     7     3     7.26     1/  2/   0          0        3           0
  ultimi referti in perdita:
   - ENAUSDT gen_bb762669 short -1.59: mai andato a favore (mfe 0.16R): direzione sbagliata
   - THEUSDT gen_a640dfa5 short -1.78: a favore fino a 0.87R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - HUMAUSDT gen_a32bee42 short -0.87: a favore fino a 0.39R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - HEMIUSDT gen_f001d778 short -1.71: a favore fino a 0.98R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - MUBARAKUSDT gen_e933160c short -4.87: mai andato a favore (mfe 0.17R): direzione sbagliata
   - ZORAUSDT gen_ceab7f6a long -1.55: mai andato a favore (mfe 0.03R): direzione sbagliata

PAPER CONTRO IL CASO (K4): il paper (280 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 122)     47/52%  48.5/51.5%
  massimo toccato mediano            0.85R       0.81R
  arrivati al primo target             13%         17%
  vinti                                56%         54%
  R medio (su 241)                  -0.089      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            37/64 -10.81    21/36 -7.65    25/39 +4.89    34/57 -1.65      84
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/5 +4.10       1
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_e59ad90b                —      1/2 -3.25      2/2 +4.33      3/4 +0.51       0
  gen_4c6df481        2/3 +3.30      1/2 -0.70              —      1/2 -0.29       0
  gen_ceab7f6a        3/6 -2.12              —              —              —       0
  gen_a640dfa5                —              —              —      4/5 +2.82       0
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
  gen_8b91ba18        2/3 -0.09              —              —      0/1 -1.64       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   8 perdite di fila  (freno spento)
  gen_bf2be656   3 perdite di fila
  gen_c0fd1d91   3 perdite di fila
  gen_c5194ce4   3 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b2f350ff   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-05 06:02 UTC): decided — parita' backtest: 1 segnali validi aperti
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_c5194ce4: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3)
  - gen_c5194ce4: solo_long — short 3/3 persi (campione 3)
  - gen_fa304106: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 8 (campione 3)
  - gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - gen_fa304106: solo_short — long 3/3 persi (campione 3)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fca11c08           6/7             45.68|42.58               1.92|1.05             0.86%|0.75%             72.33|72.21

KEEP PER STRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4465723e          3     2 (rumore 0)        1        -        0.63
  gen_4c6df481          3     3 (rumore 3)        0        -        0.64
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  gen_cd5c842f          3     2 (rumore 0)        1        -        0.63
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4810faab          2     0 (rumore 0)        2        -        0.77
  gen_4f890271          2     2 (rumore 0)        0        -        0.55
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_8981d5f2          2     0 (rumore 0)        2        -        0.65
  gen_8b91ba18          2     0 (rumore 0)        2        -        0.75
  + altre 46 strategie con meno verdetti: 56 verdetti, prematuri 27, protetti 29
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 208  (vinti 126, persi 82; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.646   p media dei persi: 0.643   (se p predice, la prima e' piu' alta)
  sopra la soglia: 208/208 trade, PnL -13.83 contro -13.83 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.025
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 280 trade): verdetto piatta (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.76      93       57%     -0.34%
    0.76-0.89      93       56%     -0.30%
    0.89-1.00      94       54%     -0.44%
  FEAR & GREED all'apertura (280 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         278       56%     -0.37%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    100 trade · 59 vinti · PnL -8.18 · R medio -0.091R su 100
  attive        180 trade · 97 vinti · PnL -70.76 · R medio -0.088R su 141
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 100 trade R -0.091 · attive 45 trade R +0.076 · differenza -0.166R, margine ±0.383R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                    91  ‖             80   -0.070 ‖          52   -0.056
  ALLENTATA                            7  ‖             12   +0.278 ‖           7   +0.198
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               137  ‖            103   -0.089 ‖          84   -0.061
  trade di coppie non piu' validate       ‖             46   -0.219 ‖           2   +0.472
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -78.94   +0.00   8.35%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -73.85   +5.09   7.84%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -76.94   +2.00   8.15%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -78.22   +0.72   8.30%       0       7        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -76.09   +2.85   8.09%       0      12        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -72.99   +5.95   7.42%       0      20        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -67.07  +11.87   6.81%       0      44        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          153     84   -37.29   -0.077
  3-5          112     61   -44.47   -0.138
  6+            15     11    +2.81   +0.161
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 192 a -0.068R · altri 49 a -0.173R · diff +0.105 ±0.273 -> NON SI VEDE ANCORA
    a size piena sugli stessi 98 trade: +11.51 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 2 a -0.304R · altri 239 a -0.087R -> CAMPIONE PICCOLO
    a size piena sugli stessi 2 trade: -0.07 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 50 a -0.120R · altri 20 a -0.116R · diff -0.004 ±0.511 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 59 a -0.083R · altri 182 a -0.091R · diff +0.008 ±0.272 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 53 a -0.042R · altri 139 a -0.077R · diff +0.035 ±0.290 -> NON SI VEDE ANCORA
    a size piena sugli stessi 34 trade: -0.55 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 100 a -0.091R · altri 141 a -0.088R · diff -0.003 ±0.232 -> NON SI VEDE ANCORA
    a size piena sugli stessi 89 trade: +16.42 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 11 a +0.242R · altri 241 a -0.089R · diff +0.331 ±0.475 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): casuali 238 trade -0.082R · intorno 3 trade -0.669R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 37
  trade chiusi: 11 · vinti 9 · PnL +2.87
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_8aec28c6                 1 trade · 0 vinti · -0.99
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
  coppie esplorative poi validate 3 / scartate 367  (il metro: si legge a 100 trade esplorativi)
```
