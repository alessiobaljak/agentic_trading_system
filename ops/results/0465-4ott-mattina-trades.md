# 0465-4ott-mattina-trades.req

_eseguito: 2026-10-04 06:04 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 4.3s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 254  (254 con apertura nota)
Giorni coperti:          19
Trade/giorno:            min 1 · media 13.4 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 7
Durata media holding:    3.9h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 12 · media nel tempo 2.4
Coin distinte:           66
Strategie distinte:      100

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      120  64/120    -36.37         0.83R
short     134  78/134    -30.07         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 26 · short 23
  bull_trending      long 29 · short 50
  high_uncertainty   long 20 · short 31
  sideways           long 45 · short 30

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         52 trade · PnL    -9.88
  CONTROTREND      76 trade · PnL     5.25
  regime neutro   126 trade · PnL   -61.81

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     215  -0.065  -13.96  39 ‖  119  +0.015   +1.80   0
    lordo           215  +0.018   +3.85  39 ‖  119  +0.097  +11.56   0
    costi stimati   215  +0.083  +17.81  39 ‖  119  +0.082   +9.76   0
 direzione
  long              104  -0.143  -14.85  16 ‖   69  -0.073   -5.05   0
  short             111  +0.008   +0.89  23 ‖   50  +0.137   +6.85   0
 regime all'apertura
  bull_trending      64  -0.145   -9.26  15 ‖   23  -0.128   -2.94   0
  bear_trending      43  +0.224   +9.63   6 ‖   32  +0.365  +11.68   0
  sideways           70  -0.101   -7.05   5 ‖   44  +0.006   +0.27   0
  high_uncertainty   38  -0.191   -7.27  13 ‖   20  -0.361   -7.22   0
 rispetto al trend
  in trend           44  +0.071   +3.12   8 ‖   29  +0.296   +8.57   0
  CONTROTREND        63  -0.044   -2.75  13 ‖   26  +0.007   +0.17   0
  regime neutro     108  -0.133  -14.32  18 ‖   64  -0.108   -6.94   0
 direzione x BTC (con = nel verso di BTC)
  long_con           55  -0.160   -8.78   0 ‖   41  -0.095   -3.88   0
  long_contro        35  -0.082   -2.85   0 ‖   28  -0.042   -1.17   0
  short_con          37  +0.108   +4.00   0 ‖   27  +0.151   +4.08   0
  short_contro       43  +0.019   +0.80   0 ‖   23  +0.120   +2.76   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669        9  +0.288   +2.59   0 ‖    7  +0.490   +3.43   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  gen_490a90e5        7  -0.031   -0.22   0 ‖    0       —       —   0
  gen_ba3a671f        3  -0.508   -1.52   4 ‖    1  -1.086   -1.09   0
  gen_cd5c842f        5  +0.330   +1.65   2 ‖    3  -0.030   -0.09   0
  gen_fa304106        3  -1.052   -3.16   4 ‖    2  -1.035   -2.07   0
  gen_4465723e        4  +0.489   +1.95   2 ‖    2  +0.495   +0.99   0
  altre 92          168  -0.077  -13.01  22 ‖  104  +0.006   +0.63   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 215 (87 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x87
  classe ingresso          x45
  classe uscita            x42
  controtrend              x25

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106     7     0     7   -12.46     2/  1/   0          0        3           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_b31d8b93     4     1     3    -5.10     1/  1/   0          0        2           0
  gen_bf2be656     3     0     3    -4.05     0/  3/   0          0        3           1
  gen_c0fd1d91     3     0     3    -6.10     2/  1/   0          0        3           1
  ultimi referti in perdita:
   - USELESSUSDT gen_194e2514 long -1.22: a favore fino a 0.40R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - QUSDT gen_bf2be656 long -0.12: a favore fino a 0.42R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - HEMIUSDT gen_f695fd53 long -0.89: a favore fino a 0.48R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - ZORAUSDT gen_ceab7f6a long -1.69: a favore fino a 0.37R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - STXUSDT gen_14e1775b long -1.62: a favore fino a 0.32R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - SOPHUSDT gen_42acf37e short -1.08: mai andato a favore (mfe 0.23R): direzione sbagliata

PAPER CONTRO IL CASO (K4): il paper (254 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  43%         46%
  stop ingresso/uscita (su 110)     47/52%  48.5/51.5%
  massimo toccato mediano            0.84R       0.81R
  arrivati al primo target             14%         17%
  vinti                                56%         54%
  R medio (su 215)                  -0.065      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            30/55 -13.18    21/35 -4.41    24/37 +6.15    28/43 +8.73      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/4 +5.69       1
  gen_4c6df481        2/3 +3.30      1/1 +2.54              —      1/2 -0.29       0
  gen_e59ad90b                —      1/2 -3.25      1/1 +3.89      2/3 +0.06       0
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
  gen_a640dfa5                —              —              —      4/4 +4.60       0
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48              —       3
  gen_ceab7f6a        2/4 -0.94              —              —              —       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   7 perdite di fila  (freno spento)
  gen_bf2be656   3 perdite di fila
  gen_c0fd1d91   3 perdite di fila
  gen_c5194ce4   3 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_1f7ead60   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_acfd527a   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-04 06:02 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
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
  gen_902fb1fd          2     1 (rumore 0)        1        -        0.74
  + altre 42 strategie con meno verdetti: 49 verdetti, prematuri 22, protetti 27
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 182  (vinti 112, persi 70; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.647   p media dei persi: 0.647   (se p predice, la prima e' piu' alta)
  sopra la soglia: 182/182 trade, PnL -1.33 contro -1.33 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.002
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 254 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.74      84       56%     -0.52%
    0.76-0.89      84       58%     +0.03%
    0.89-1.00      86       54%     -0.46%
  FEAR & GREED all'apertura (254 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         252       56%     -0.33%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     84 trade · 50 vinti · PnL -3.94 · R medio -0.058R su 84
  attive        170 trade · 92 vinti · PnL -62.50 · R medio -0.070R su 131
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 84 trade R -0.058 · attive 35 trade R +0.190 · differenza -0.247R, margine ±0.480R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                    85  ‖             67   +0.013 ‖          39   +0.090
  ALLENTATA                            7  ‖             11   +0.244 ‖           6   +0.121
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               131  ‖             91   -0.082 ‖          72   -0.047
  trade di coppie non piu' validate       ‖             46   -0.219 ‖           2   +0.472
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -66.44   +0.00   8.35%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -61.35   +5.09   7.84%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -64.43   +2.01   8.15%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -65.95   +0.49   8.30%       0       6        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -63.83   +2.61   8.09%       0      11        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -60.49   +5.95   7.42%       0      20        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -55.02  +11.42   6.81%       0      42        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          142     78   -33.54   -0.057
  3-5           97     53   -35.71   -0.111
  6+            15     11    +2.81   +0.161
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 166 a -0.033R · altri 49 a -0.173R · diff +0.140 ±0.278 -> NON SI VEDE ANCORA
    a size piena sugli stessi 85 trade: +3.16 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 1 a +0.435R · altri 214 a -0.067R -> CAMPIONE PICCOLO
    a size piena sugli stessi 1 trade: -0.64 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 38 a +0.004R · altri 18 a -0.084R · diff +0.088 ±0.568 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 47 a +0.026R · altri 168 a -0.090R · diff +0.116 ±0.303 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 48 a -0.032R · altri 118 a -0.033R · diff +0.001 ±0.311 -> NON SI VEDE ANCORA
    a size piena sugli stessi 32 trade: -1.53 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 84 a -0.058R · altri 131 a -0.070R · diff +0.012 ±0.250 -> NON SI VEDE ANCORA
    a size piena sugli stessi 77 trade: +5.99 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 10 a +0.385R · altri 215 a -0.065R · diff +0.450 ±0.419 -> CONTRIBUISCE
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): casuali 214 trade -0.067R · intorno 1 trade +0.292R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 48
  trade chiusi: 10 · vinti 9 · PnL +3.85
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    DEXEUSDT|gen_10f540ba                1 trade · 1 vinti · +0.25
  coppie esplorative poi validate 3 / scartate 327  (il metro: si legge a 100 trade esplorativi)
```
