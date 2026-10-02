# 0420-2ott-mattina-trades.req

_eseguito: 2026-10-02 06:04 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 4.1s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 216  (216 con apertura nota)
Giorni coperti:          17
Trade/giorno:            min 1 · media 12.7 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 8
Durata media holding:    3.5h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 2.0
Coin distinte:           57
Strategie distinte:      85

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       94   48/94    -41.37         0.81R
short     122  69/122    -38.82         0.87R

Regime ALL'APERTURA x direzione:
  bear_trending      long 19 · short 21
  bull_trending      long 27 · short 48
  high_uncertainty   long 18 · short 30
  sideways           long 30 · short 23

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         48 trade · PnL    -9.31
  CONTROTREND      67 trade · PnL     1.78
  regime neutro   101 trade · PnL   -72.67

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     177  -0.119  -21.00  39 ‖   81  -0.065   -5.25   0
    lordo           177  -0.038   -6.65  39 ‖   81  +0.013   +1.06   0
    costi stimati   177  +0.081  +14.36  39 ‖   81  +0.078   +6.31   0
 direzione
  long               78  -0.220  -17.16  16 ‖   43  -0.171   -7.36   0
  short              99  -0.039   -3.85  23 ‖   38  +0.056   +2.11   0
 regime all'apertura
  bull_trending      60  -0.153   -9.20  15 ‖   19  -0.151   -2.87   0
  bear_trending      34  +0.233   +7.93   6 ‖   23  +0.434   +9.97   0
  sideways           48  -0.256  -12.26   5 ‖   22  -0.225   -4.94   0
  high_uncertainty   35  -0.213   -7.47  13 ‖   17  -0.436   -7.41   0
 rispetto al trend
  in trend           40  +0.087   +3.48   8 ‖   25  +0.357   +8.93   0
  CONTROTREND        54  -0.088   -4.75  13 ‖   17  -0.107   -1.83   0
  regime neutro      83  -0.238  -19.73  18 ‖   39  -0.317  -12.35   0
 direzione x BTC (con = nel verso di BTC)
  long_con           36  -0.319  -11.48   0 ‖   22  -0.299   -6.58   0
  long_contro        28  -0.088   -2.46   0 ‖   21  -0.037   -0.78   0
  short_con          31  +0.016   +0.49   0 ‖   21  +0.027   +0.57   0
  short_contro       37  -0.011   -0.42   0 ‖   17  +0.091   +1.54   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  gen_490a90e5        7  -0.031   -0.22   0 ‖    0       —       —   0
  gen_bb762669        7  +0.009   +0.06   0 ‖    5  +0.180   +0.90   0
  gen_cd5c842f        5  +0.330   +1.65   2 ‖    3  -0.030   -0.09   0
  gen_fa304106        3  -1.052   -3.16   4 ‖    2  -1.035   -2.07   0
  gen_4465723e        4  +0.489   +1.95   2 ‖    2  +0.495   +0.99   0
  gen_6d06dca0        2  -0.186   -0.37   4 ‖    0       —       —   0
  altre 77          133  -0.140  -18.68  22 ‖   69  -0.072   -4.98   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 177 (74 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x74
  classe ingresso          x39
  classe uscita            x35
  controtrend              x22

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
   - SUPERUSDT gen_0eb999b7 short -1.28: a favore fino a 0.49R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - TAUSDT gen_4e6e1ae0 long -2.92: mai andato a favore (mfe 0.00R): direzione sbagliata
   - QUSDT gen_85fadf54 long -2.50: a favore fino a 0.38R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - BULLAUSDT gen_7ac562e3 short -0.83: mai andato a favore (mfe 0.11R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - AIOUSDT gen_581d4a68 long -1.13: mai andato a favore (mfe 0.13R): direzione sbagliata
   - HUMAUSDT gen_771790b1 short -1.00: a favore fino a 0.73R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)

PAPER CONTRO IL CASO (K4): il paper (216 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  46%         46%
  stop ingresso/uscita (su 99)      46/52%  48.5/51.5%
  massimo toccato mediano            0.84R       0.81R
  arrivati al primo target             13%         17%
  vinti                                54%         54%
  R medio (su 177)                  -0.119      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            18/36 -18.69    17/28 -3.90    19/31 +0.40    24/37 +5.72      84
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      2/2 +1.52       1
  gen_4c6df481        1/2 -0.14      1/1 +2.54              —      1/2 -0.29       0
  gen_e59ad90b                —      1/2 -3.25      1/1 +3.89      2/2 +0.83       0
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
  gen_a640dfa5                —              —              —      4/4 +4.60       0
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48              —       3
  gen_e50a9211        0/1 -0.95              —      1/2 -1.28      1/1 +0.23       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   7 perdite di fila  (freno spento)
  gen_c0fd1d91   3 perdite di fila
  gen_1f7ead60   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b2f350ff   2 perdite di fila
  gen_b31d8b93   2 perdite di fila
  gen_bf2be656   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-02 06:02 UTC): flat — nessun segnale valido sopra soglia
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
  gen_bb762669          4     2 (rumore 0)        2        -        0.75
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4465723e          3     2 (rumore 0)        1        -        0.63
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
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
  gen_a640dfa5          2     2 (rumore 0)        0        -        0.73
  gen_f238d283          2     0 (rumore 0)        2        -        0.63
  + altre 34 strategie con meno verdetti: 35 verdetti, prematuri 15, protetti 20
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 144  (vinti 87, persi 57; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.650   p media dei persi: 0.643   (se p predice, la prima e' piu' alta)
  sopra la soglia: 144/144 trade, PnL -15.08 contro -15.08 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.062
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 216 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.76      72       53%     -0.69%
    0.76-0.90      72       57%     -0.17%
    0.90-1.00      72       53%     -0.62%
  FEAR & GREED all'apertura (216 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         214       54%     -0.51%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate     52 trade · 31 vinti · PnL -7.11 · R medio -0.127R su 52
  attive        164 trade · 86 vinti · PnL -73.08 · R medio -0.115R su 125
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 52 trade R -0.127 · attive 29 trade R +0.047 · differenza -0.174R, margine ±0.389R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                    76  ‖             57   -0.022 ‖          29   +0.049
  ALLENTATA                            7  ‖             11   +0.244 ‖           6   +0.121
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               129  ‖             64   -0.189 ‖          45   -0.179
  trade di coppie non piu' validate       ‖             45   -0.230 ‖           1   +0.666
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -80.19   +0.00   8.35%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -75.10   +5.09   7.84%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -78.19   +2.00   8.15%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -79.70   +0.49   8.30%       0       6        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -77.58   +2.61   8.09%       0      11        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -70.91   +9.28   7.42%       0       9        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -64.76  +15.43   6.81%       0      29        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 128 a -0.098R · altri 49 a -0.173R · diff +0.075 ±0.284 -> NON SI VEDE ANCORA
    a size piena sugli stessi 56 trade: +8.04 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 1 a +0.435R · altri 176 a -0.122R -> CAMPIONE PICCOLO
    a size piena sugli stessi 1 trade: -0.64 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 25 a -0.048R · altri 16 a -0.248R · diff +0.200 ±0.548 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 34 a -0.003R · altri 143 a -0.146R · diff +0.143 ±0.308 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 37 a -0.118R · altri 91 a -0.090R · diff -0.028 ±0.339 -> NON SI VEDE ANCORA
    a size piena sugli stessi 23 trade: -1.72 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 52 a -0.127R · altri 125 a -0.115R · diff -0.012 ±0.273 -> NON SI VEDE ANCORA
    a size piena sugli stessi 48 trade: +20.64 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 8 a +0.346R · altri 177 a -0.119R -> CAMPIONE PICCOLO
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): casuali 177 trade -0.119R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 48
  trade chiusi: 8 · vinti 7 · PnL +2.97
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
    HEMIUSDT|gen_f4c1300a                1 trade · 1 vinti · +0.30
    MUBARAKUSDT|gen_cf6a181e             1 trade · 1 vinti · +0.59
  coppie esplorative poi validate 0 / scartate 242  (il metro: si legge a 100 trade esplorativi)
```
