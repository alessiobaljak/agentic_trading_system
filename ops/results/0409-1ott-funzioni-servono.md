# 0409-1ott-funzioni-servono.req

_eseguito: 2026-10-01 14:07 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 4.1s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 203  (203 con apertura nota)
Giorni coperti:          16
Trade/giorno:            min 1 · media 12.7 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 10
Durata media holding:    3.5h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 2.0
Coin distinte:           55
Strategie distinte:      82

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       89   46/89    -37.37         0.81R
short     114  64/114    -43.74         0.89R

Regime ALL'APERTURA x direzione:
  bear_trending      long 18 · short 19
  bull_trending      long 26 · short 45
  high_uncertainty   long 18 · short 28
  sideways           long 27 · short 22

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         45 trade · PnL   -12.93
  CONTROTREND      63 trade · PnL    -0.25
  regime neutro    95 trade · PnL   -67.93

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     164  -0.117  -19.18  39 ‖   68  -0.050   -3.43   0
    lordo           164  -0.036   -5.85  39 ‖   68  +0.027   +1.86   0
    costi stimati   164  +0.081  +13.34  39 ‖   68  +0.078   +5.29   0
 direzione
  long               73  -0.212  -15.50  16 ‖   38  -0.150   -5.71   0
  short              91  -0.040   -3.68  23 ‖   30  +0.076   +2.28   0
 regime all'apertura
  bull_trending      56  -0.190  -10.63  15 ‖   15  -0.287   -4.30   0
  bear_trending      31  +0.259   +8.04   6 ‖   20  +0.504  +10.09   0
  sideways           44  -0.225   -9.90   5 ‖   18  -0.143   -2.57   0
  high_uncertainty   33  -0.203   -6.70  13 ‖   15  -0.443   -6.64   0
 rispetto al trend
  in trend           37  +0.050   +1.86   8 ‖   22  +0.332   +7.31   0
  CONTROTREND        50  -0.089   -4.45  13 ‖   13  -0.117   -1.53   0
  regime neutro      77  -0.216  -16.60  18 ‖   33  -0.279   -9.22   0
 direzione x BTC (con = nel verso di BTC)
  long_con           31  -0.317   -9.82   0 ‖   17  -0.290   -4.93   0
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
  altre 74          125  -0.131  -16.36  18 ‖   61  -0.037   -2.26   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 164 (68 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x68
  classe ingresso          x36
  classe uscita            x32
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
   - MITOUSDT gen_8b91ba18 short -1.64: a favore fino a 0.62R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - ORCAUSDT gen_cb8176f2 short -0.93: a favore fino a 0.41R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - ZORAUSDT gen_ceab7f6a long -1.32: mai andato a favore (mfe 0.00R): direzione sbagliata
   - JASMYUSDT gen_b2f350ff short -1.36: mai andato a favore (mfe 0.17R): direzione sbagliata
   - USELESSUSDT gen_c0fd1d91 long -1.32: a favore fino a 0.40R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - ENAUSDT gen_bb762669 long -1.22: a favore fino a 0.44R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)

PAPER CONTRO IL CASO (K4): il paper (203 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  46%         46%
  stop ingresso/uscita (su 93)      46/53%  48.5/51.5%
  massimo toccato mediano            0.84R       0.81R
  arrivati al primo target             13%         17%
  vinti                                54%         54%
  R medio (su 164)                  -0.117      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            16/31 -14.68    17/28 -3.90    19/31 +0.40    19/29 +0.80      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      1/1 +0.28       1
  gen_4c6df481        0/1 -1.51      1/1 +2.54              —      1/2 -0.29       0
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
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
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-01 14:02 UTC): flat — nessun segnale valido sopra soglia
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
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4465723e          3     2 (rumore 0)        1        -        0.63
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_bb762669          3     2 (rumore 0)        1        -        0.73
  gen_cd5c842f          3     2 (rumore 0)        1        -        0.63
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4f890271          2     2 (rumore 0)        0        -        0.55
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  gen_887d87df          2     0 (rumore 0)        2        -        0.81
  gen_919c110c          2     2 (rumore 0)        0        -        0.54
  gen_a640dfa5          2     2 (rumore 0)        0        -        0.73
  gen_e59ad90b          2     2 (rumore 1)        0        -        0.78
  gen_f238d283          2     0 (rumore 0)        2        -        0.63
  gen_f3661202          2     0 (rumore 0)        2        -        0.81
  + altre 34 strategie con meno verdetti: 34 verdetti, prematuri 14, protetti 20
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 131  (vinti 80, persi 51; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.651   p media dei persi: 0.644   (se p predice, la prima e' piu' alta)
  sopra la soglia: 131/131 trade, PnL -16.00 contro -16.00 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.058
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 203 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.78      67       54%     -0.74%
    0.78-0.90      67       57%     -0.18%
    0.90-1.00      69       52%     -0.66%
  FEAR & GREED all'apertura (203 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         201       54%     -0.54%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     44 trade · 27 vinti · PnL -5.85 · R medio -0.101R su 44
  attive        159 trade · 83 vinti · PnL -75.26 · R medio -0.123R su 120
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 44 trade R -0.101 · attive 24 trade R +0.042 · differenza -0.143R, margine ±0.412R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                    72  ‖             50   -0.054 ‖          22   -0.001
  ALLENTATA                            7  ‖             11   +0.244 ‖           6   +0.121
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               129  ‖             58   -0.152 ‖          39   -0.123
  trade di coppie non piu' validate       ‖             45   -0.230 ‖           1   +0.666
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -81.11   +0.00   8.11%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -76.02   +5.09   7.60%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -79.11   +2.00   7.91%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -80.62   +0.49   8.06%       0       6        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -78.50   +2.61   7.85%       0      11        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -71.83   +9.28   7.18%       0       9        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -65.49  +15.62   6.56%       0      28        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 115 a -0.093R · altri 49 a -0.173R · diff +0.080 ±0.287 -> NON SI VEDE ANCORA
    a size piena sugli stessi 48 trade: +12.90 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 1 a +0.435R · altri 163 a -0.120R -> CAMPIONE PICCOLO
    a size piena sugli stessi 1 trade: -0.64 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 20 a -0.083R · altri 15 a -0.326R · diff +0.243 ±0.585 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 29 a -0.020R · altri 135 a -0.138R · diff +0.118 ±0.338 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 32 a -0.094R · altri 83 a -0.093R · diff -0.001 ±0.351 -> NON SI VEDE ANCORA
    a size piena sugli stessi 19 trade: -0.50 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 44 a -0.101R · altri 120 a -0.123R · diff +0.022 ±0.287 -> NON SI VEDE ANCORA
    a size piena sugli stessi 41 trade: +20.24 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.0012% · attive 0.0021% (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 8 a +0.346R · altri 164 a -0.117R -> CAMPIONE PICCOLO
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): casuali 164 trade -0.117R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 63
  trade chiusi: 8 · vinti 7 · PnL +2.97
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    HEMIUSDT|gen_f4c1300a                1 trade · 1 vinti · +0.30
    MUBARAKUSDT|gen_cf6a181e             1 trade · 1 vinti · +0.59
  coppie esplorative poi validate 0 / scartate 200  (il metro: si legge a 100 trade esplorativi)
```
