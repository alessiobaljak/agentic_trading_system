# 0622-18ott-storia-trades.req

_eseguito: 2026-10-18 09:03 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 9.2s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 668  (668 con apertura nota)
Giorni coperti:          33
Trade/giorno:            min 1 · media 20.2 · max 51
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 40 · 2026-10-08 39 · 2026-10-09 24 · 2026-10-10 16 · 2026-10-11 25 · 2026-10-12 32 · 2026-10-13 51 · 2026-10-14 35 · 2026-10-15 25 · 2026-10-16 31 · 2026-10-17 27 · 2026-10-18 8
Durata media holding:    3.7h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 14 · media nel tempo 3.3
Coin distinte:           99
Strategie distinte:      200

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      392 211/392   -109.71         0.70R
short     276 158/276    -63.30         0.82R

Regime ALL'APERTURA x direzione:
  bear_trending      long 178 · short 63
  bull_trending      long 57 · short 85
  high_uncertainty   long 54 · short 52
  sideways           long 103 · short 76

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend        120 trade · PnL   -12.57
  CONTROTREND     263 trade · PnL   -62.40
  regime neutro   285 trade · PnL   -98.03

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     629  -0.113  -71.28  39 ‖  533  -0.104  -55.52   0
    lordo           629  -0.026  -16.58  39 ‖  533  -0.017   -8.87   0
    costi stimati   629  +0.087  +54.70  39 ‖  533  +0.088  +46.65   0
 direzione
  long              376  -0.153  -57.43  16 ‖  341  -0.140  -47.64   0
  short             253  -0.055  -13.84  23 ‖  192  -0.041   -7.89   0
 regime all'apertura
  bull_trending     127  -0.187  -23.77  15 ‖   86  -0.203  -17.44   0
  bear_trending     235  -0.086  -20.30   6 ‖  224  -0.081  -18.25   0
  sideways          174  -0.157  -27.24   5 ‖  148  -0.135  -19.92   0
  high_uncertainty   93  +0.000   +0.03  13 ‖   75  +0.001   +0.09   0
 rispetto al trend
  in trend          112  -0.025   -2.85   8 ‖   97  +0.027   +2.61   0
  CONTROTREND       250  -0.165  -41.22  13 ‖  213  -0.180  -38.30   0
  regime neutro     267  -0.102  -27.21  18 ‖  223  -0.089  -19.83   0
 direzione x BTC (con = nel verso di BTC)
  long_con          154  -0.155  -23.92   0 ‖  140  -0.136  -19.03   0
  long_contro       208  -0.146  -30.30   0 ‖  201  -0.142  -28.61   0
  short_con          94  -0.071   -6.69   0 ‖   84  -0.079   -6.61   0
  short_contro      128  -0.025   -3.24   0 ‖  108  -0.012   -1.28   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_ceab7f6a       15  -0.221   -3.32   0 ‖   15  -0.221   -3.32   0
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       12  -0.050   -0.61   0 ‖   10  +0.023   +0.23   0
  gen_4c6df481       11  -0.109   -1.20   0 ‖    8  -0.086   -0.69   0
  gen_684d7623       11  -0.183   -2.01   0 ‖   11  -0.183   -2.01   0
  gen_fa304106        7  -1.068   -7.47   4 ‖    6  -1.064   -6.39   0
  gen_01fbe76f       10  -0.020   -0.20   0 ‖   10  -0.020   -0.20   0
  gen_cd5c842f        8  +0.252   +2.02   2 ‖    6  +0.046   +0.28   0
  altre 192         541  -0.101  -54.80  33 ‖  467  -0.093  -43.42   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 629 (274 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x274
  classe uscita            x137
  classe ingresso          x137
  controtrend              x116

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    11     0    11   -15.73     4/  3/   0          0        7           0
  gen_ceab7f6a    15     8     7    -3.60     5/  2/   0          0        7           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_4c6df481    11     5     6     0.36     2/  4/   0          0        6           0
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_bb762669    12     7     5     4.68     3/  2/   0          0        5           0
  gen_18c839a0     8     4     4    -7.07     3/  1/   0          0        4           2
  ultimi referti in perdita:
   - AINUSDT gen_5b847426 long -3.11: a favore fino a 0.45R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - IDOLUSDT gen_5ad54558 long -1.24: mai andato a favore (mfe 0.00R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - SYRUPUSDT gen_f3b97917 long -2.63: a favore fino a 0.92R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - TAUSDT gen_6e8a4220 long -1.43: a favore fino a 0.41R ma sotto il primo gradino (1R) · il lock non si e' mai armato (serviva 0.5R)
   - STXUSDT gen_0aa0d29c short -3.24: mai andato a favore (mfe 0.15R): direzione sbagliata
   - AINUSDT gen_9839aec0 short -1.99: a favore fino a 0.58R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)

PAPER CONTRO IL CASO (K4): il paper (668 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 294)     49/51%  48.5/51.5%
  massimo toccato mediano            0.77R       0.81R
  arrivati al primo target             12%         17%
  vinti                                55%         54%
  R medio (su 629)                  -0.113      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte           85/154 -45.13 113/208 -45.79    55/94 -8.74   77/128 -9.61      84
  gen_ceab7f6a       8/12 -1.56      0/2 -1.47      0/1 -0.58              —       0
  gen_4c6df481        3/4 +3.42      1/3 -2.41              —      1/4 -0.65       0
  gen_684d7623        2/3 +0.00      4/7 -1.04      1/1 +0.99              —       0
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/7 +1.52       1
  gen_01fbe76f        5/5 +1.73      2/5 -2.89              —              —       0
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_c647ead7        1/1 +0.81      4/7 -3.22      0/1 -1.53              —       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   11 perdite di fila  (freno spento)
  gen_f311acf9   4 perdite di fila  (freno spento)
  gen_18c839a0   3 perdite di fila
  gen_7b4a474b   3 perdite di fila
  gen_bb762669   3 perdite di fila
  gen_bf2be656   3 perdite di fila
  gen_ff3e4154   3 perdite di fila
  gen_0d7be682   2 perdite di fila
  gen_14e1775b   2 perdite di fila
  gen_194e2514   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-18 09:02 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_4c6df481: scala_stretta — 4 perdite sotto il primo gradino (mfe mediana 0.59 R) (campione 4)
  - gen_5905e08d: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_5905e08d: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.47 R) (campione 3)
  - gen_5a52c06b: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_684d7623: conferma_trend — 4 perdite controtrend (campione 4)
  - gen_871647b8: conferma_trend — 4 perdite controtrend (campione 4)
  - gen_871647b8: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4)
  - gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3)
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_c5194ce4: ingresso_atr_pct — 4 perdite d'ingresso su 4 con volatilita' alta (ATR > 0.66% del prezzo) (mediana 0.92%), vinti mediana 0.61% (campione 4)
  - gen_c647ead7: conferma_trend — 3 perdite controtrend (campione 3)
  - g

[... 1916 caratteri omessi (testa e coda conservate) ...]

ia      verdetti        prematuri protetti proposta  miss medio
  gen_01fbe76f          7     1 (rumore 1)        6     0.75        0.80
  gen_ceab7f6a          6     1 (rumore 0)        5     0.75        0.83
  gen_4465723e          5     2 (rumore 0)        3     0.75        0.60
  gen_4c6df481          5     4 (rumore 3)        1     0.25        0.63
  gen_684d7623          5     3 (rumore 1)        2        -        0.87
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_c647ead7          5     4 (rumore 0)        1        -        0.68
  gen_cd5c842f          5     3 (rumore 0)        2        -        0.57
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_658b2edb          4     3 (rumore 0)        1        -        0.64
  gen_8981d5f2          4     2 (rumore 2)        2        -        0.58
  gen_8c9b332f          4     3 (rumore 1)        1        -        0.73
  gen_902fb1fd          4     2 (rumore 0)        2        -        0.82
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_1eec02f5          3     2 (rumore 1)        1        -        0.81
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_35632db9          3     1 (rumore 0)        2        -        0.65
  gen_4810faab          3     1 (rumore 0)        2        -        0.79
  + altre 119 strategie con meno verdetti: 176 verdetti, prematuri 82, protetti 94
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 596  (vinti 339, persi 257; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.658   p media dei persi: 0.647   (se p predice, la prima e' piu' alta)
  sopra la soglia: 596/596 trade, PnL -107.89 contro -107.89 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.089
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 663 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.69     221       53%     -0.58%
    0.69-0.88     221       62%     +0.10%
    0.88-1.00     221       52%     -0.51%
  FEAR & GREED all'apertura (662 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         660       56%     -0.34%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    299 trade · 170 vinti · PnL -23.60 · R medio -0.088R su 299
  attive        369 trade · 199 vinti · PnL -149.40 · R medio -0.136R su 330
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 299 trade R -0.088 · attive 234 trade R -0.124 · differenza +0.036R, margine ±0.163R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                     0  ‖              0        — ‖           0        —
  ALLENTATA                            0  ‖              0        — ‖           0        —
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato                 0  ‖              0        — ‖           0        —
  trade di coppie non piu' validate       ‖            629   -0.113 ‖         533   -0.104
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  10-13 10-15 09-23
  com'e' andato davvero                                 -173.00   +0.00  17.51%       0       0        0  -24.45 -19.81 -17.66
  stop giornaliero 2%                                   -171.73   +1.27  17.42%      62       0        6  -26.73 -20.43 -17.66
  stop giornaliero 3%                                   -170.85   +2.15  17.30%      37       0        2  -26.73 -19.81 -17.66
  freno di serie: 4 perdite della strategia -> meta'    -171.04   +1.96  17.28%       0      13        0  -24.45 -19.81 -18.72
  freno di serie: 3 perdite della strategia -> meta'    -172.16   +0.84  17.23%       0      27        0  -24.78 -19.81 -16.51
  freno di serie: 4 perdite del bot -> meta'            -171.70   +1.30  17.35%       0      47        0  -28.20 -20.12 -17.66
  freno di serie: 3 perdite del bot -> meta'            -161.45  +11.55  16.15%       0     100        0  -28.20 -20.12 -14.90
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          286    159   -49.22   -0.092
  3-5          298    163  -103.26   -0.119
  6+            84     47   -20.52   -0.160
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92
    2026-10-07 04:18  long   12 aperture  PnL -5.15
    2026-10-13 02:17  long    8 aperture  PnL -12.39
    2026-10-13 03:03  long    9 aperture  PnL +9.98

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 580 a -0.108R · altri 49 a -0.173R · diff +0.065 ±0.253 -> NON SI VEDE ANCORA
    a size piena sugli stessi 297 trade: +47.38 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 16 a -0.007R · altri 613 a -0.116R · diff +0.109 ±0.667 -> NON SI VEDE ANCORA
    a size piena sugli stessi 12 trade: -1.57 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 167 a -0.167R · altri 68 a -0.005R · diff -0.162 ±0.312 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 169 a -0.151R · altri 460 a -0.100R · diff -0.051 ±0.166 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 248 a -0.169R · altri 332 a -0.063R · diff -0.106 ±0.156 -> NON SI VEDE ANCORA
    a size piena sugli stessi 152 trade: +7.30 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 299 a -0.088R · altri 330 a -0.136R · diff +0.048 ±0.148 -> NON SI VEDE ANCORA
    a size piena sugli stessi 263 trade: +64.49 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.11% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 39 a -0.068R · altri 629 a -0.113R · diff +0.045 ±0.302 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 18 trade -0.173R · casuali 592 trade -0.105R · intorno 19 trade -0.314R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 25
  trade chiusi: 39 · vinti 24 · PnL -1.40
    AIOUSDT|gen_7027edb8                 4 trade · 3 vinti · +0.31
    AVAAIUSDT|gen_8b91ba18               2 trade · 0 vinti · -2.56
    DEXEUSDT|gen_e50a9211                2 trade · 0 vinti · -2.70
    HEMIUSDT|gen_4c6df481                2 trade · 1 vinti · -0.10
    MITOUSDT|gen_0919b67a                2 trade · 1 vinti · -0.39
  coppie esplorative poi validate 4 / scartate 694  (il metro: si legge a 100 trade esplorativi)
```
