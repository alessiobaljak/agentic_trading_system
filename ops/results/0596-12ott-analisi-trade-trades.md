# 0596-12ott-analisi-trade-trades.req

_eseguito: 2026-10-12 16:51 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 8.2s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 481  (481 con apertura nota)
Giorni coperti:          27
Trade/giorno:            min 1 · media 17.8 · max 40
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 40 · 2026-10-08 39 · 2026-10-09 24 · 2026-10-10 16 · 2026-10-11 25 · 2026-10-12 22
Durata media holding:    3.9h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 14 · media nel tempo 3.0
Coin distinte:           91
Strategie distinte:      159

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      258 136/258    -72.85         0.76R
short     223 127/223    -57.37         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 88 · short 47
  bull_trending      long 46 · short 74
  high_uncertainty   long 39 · short 43
  sideways           long 85 · short 59

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         93 trade · PnL   -13.54
  CONTROTREND     162 trade · PnL   -32.57
  regime neutro   226 trade · PnL   -84.11

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     442  -0.110  -48.50  39 ‖  346  -0.095  -32.74   0
    lordo           442  -0.015   -6.68  39 ‖  346  +0.003   +1.03   0
    costi stimati   442  +0.095  +41.82  39 ‖  346  +0.098  +33.77   0
 direzione
  long              242  -0.161  -38.91  16 ‖  207  -0.141  -29.11   0
  short             200  -0.048   -9.59  23 ‖  139  -0.026   -3.63   0
 regime all'apertura
  bull_trending     105  -0.211  -22.11  15 ‖   64  -0.247  -15.78   0
  bear_trending     129  -0.026   -3.33   6 ‖  118  -0.011   -1.28   0
  sideways          139  -0.132  -18.40   5 ‖  113  -0.098  -11.08   0
  high_uncertainty   69  -0.068   -4.66  13 ‖   51  -0.090   -4.60   0
 rispetto al trend
  in trend           85  -0.024   -2.08   8 ‖   70  +0.048   +3.37   0
  CONTROTREND       149  -0.157  -23.36  13 ‖  112  -0.182  -20.44   0
  regime neutro     208  -0.111  -23.06  18 ‖  164  -0.096  -15.68   0
 direzione x BTC (con = nel verso di BTC)
  long_con          106  -0.156  -16.51   0 ‖   92  -0.126  -11.62   0
  long_contro       122  -0.157  -19.18   0 ‖  115  -0.152  -17.49   0
  short_con          69  -0.089   -6.13   0 ‖   59  -0.103   -6.05   0
  short_contro      100  +0.005   +0.45   0 ‖   80  +0.030   +2.42   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_ceab7f6a       15  -0.221   -3.32   0 ‖   15  -0.221   -3.32   0
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       11  +0.043   +0.48   0 ‖    9  +0.146   +1.31   0
  gen_fa304106        7  -1.068   -7.47   4 ‖    6  -1.064   -6.39   0
  gen_4c6df481       10  -0.015   -0.15   0 ‖    7  +0.052   +0.36   0
  gen_cd5c842f        8  +0.252   +2.02   2 ‖    6  +0.046   +0.28   0
  gen_e59ad90b       10  -0.125   -1.25   0 ‖    9  -0.280   -2.52   0
  gen_4465723e        7  +0.295   +2.07   2 ‖    5  +0.220   +1.10   0
  altre 151         360  -0.103  -37.18  31 ‖  289  -0.082  -23.57   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 442 (193 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x193
  classe uscita            x101
  classe ingresso          x92
  controtrend              x68

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    11     0    11   -15.73     4/  3/   0          0        7           0
  gen_ceab7f6a    15     8     7    -3.60     5/  2/   0          0        7           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_4c6df481    10     5     5     0.48     2/  3/   0          0        5           0
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_18c839a0     8     4     4    -7.07     3/  1/   0          0        4           2
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  ultimi referti in perdita:
   - HYPEUSDT gen_f19b67e8 long -0.85: a favore fino a 0.36R ma sotto il primo gradino (1R) · il lock non si e' mai armato (serviva 0.5R)
   - UBUSDT gen_08664b28 long -1.26: a favore fino a 0.63R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - USELESSUSDT gen_e09c5203 long -1.49: mai andato a favore (mfe 0.12R): direzione sbagliata
   - UBUSDT gen_f3e1ade7 long -1.41: mai andato a favore (mfe 0.00R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - USELESSUSDT gen_e09c5203 long -1.03: mai andato a favore (mfe 0.14R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - BANKUSDT gen_7100bb59 long -1.16: mai andato a favore (mfe 0.21R): direzione sbagliata

PAPER CONTRO IL CASO (K4): il paper (481 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 213)     46/54%  48.5/51.5%
  massimo toccato mediano            0.80R       0.81R
  arrivati al primo target             12%         17%
  vinti                                55%         54%
  R medio (su 442)                  -0.110      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte           58/106 -24.47  65/122 -29.60    39/69 -8.91   62/100 -3.52      84
  gen_ceab7f6a       8/12 -1.56      0/2 -1.47      0/1 -0.58              —       0
  gen_4c6df481        3/4 +3.42      1/3 -2.41              —      1/3 -0.53       0
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/6 +2.68       1
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_cd5c842f                —      2/3 +1.09      2/3 +4.14      1/1 +0.95       3
  gen_4465723e        1/1 +1.88      2/3 -0.08      2/2 +1.55              —       3
  gen_8b91ba18        2/4 -1.48              —      1/1 +0.83      0/1 -1.64       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   11 perdite di fila  (freno spento)
  gen_18c839a0   3 perdite di fila
  gen_96c1ed1b   3 perdite di fila
  gen_bf2be656   3 perdite di fila
  gen_08664b28   2 perdite di fila
  gen_0d7be682   2 perdite di fila
  gen_14e1775b   2 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_4e6e1ae0   2 perdite di fila
  gen_4f890271   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-12 16:47 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_4c6df481: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.79 R) (campione 3)
  - gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3)
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_c5194ce4: ingresso_atr_pct — 4 perdite d'ingresso su 4 con volatilita' alta (ATR > 0.66% del prezzo) (mediana 0.92%), vinti mediana 0.61% (campione 4)
  - gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5)
  - gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4)
  - gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4)
  - gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3)
  - gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - gen_fa304106: solo_short — long 6/6 persi (campione 6)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perd

[... 738 caratteri omessi (testa e coda conservate) ...]

 prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_ceab7f6a          6     1 (rumore 0)        5     0.75        0.83
  gen_4465723e          5     2 (rumore 0)        3     0.75        0.60
  gen_4c6df481          5     4 (rumore 3)        1     0.25        0.63
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_cd5c842f          5     3 (rumore 0)        2        -        0.57
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_658b2edb          4     3 (rumore 0)        1        -        0.64
  gen_8c9b332f          4     3 (rumore 1)        1        -        0.73
  gen_902fb1fd          4     2 (rumore 0)        2        -        0.80
  gen_c647ead7          4     3 (rumore 0)        1        -        0.73
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_1eec02f5          3     2 (rumore 1)        1        -        0.81
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4810faab          3     1 (rumore 0)        2        -        0.79
  gen_725cb5f4          3     0 (rumore 0)        3        -        0.91
  gen_771790b1          3     2 (rumore 0)        1        -        0.62
  gen_8981d5f2          3     1 (rumore 1)        2        -        0.66
  gen_8b91ba18          3     1 (rumore 0)        2        -        0.72
  + altre 86 strategie con meno verdetti: 119 verdetti, prematuri 62, protetti 57
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 409  (vinti 233, persi 176; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.651   p media dei persi: 0.639   (se p predice, la prima e' piu' alta)
  sopra la soglia: 409/409 trade, PnL -65.11 contro -65.11 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.098
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 481 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.72     160       54%     -0.60%
    0.72-0.88     160       60%     +0.12%
    0.88-1.00     161       50%     -0.58%
  FEAR & GREED all'apertura (480 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         478       55%     -0.36%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    226 trade · 127 vinti · PnL -17.90 · R medio -0.078R su 226
  attive        255 trade · 136 vinti · PnL -112.32 · R medio -0.143R su 216
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 226 trade R -0.078 · attive 120 trade R -0.125 · differenza +0.047R, margine ±0.210R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   192  ‖            136   -0.045 ‖         123   -0.073
  ALLENTATA                            0  ‖              0        — ‖           0        —
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato                37  ‖             23   -0.141 ‖          23   -0.141
  trade di coppie non piu' validate       ‖            283   -0.138 ‖         200   -0.102
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 10-08
  com'e' andato davvero                                 -130.22   +0.00  13.06%       0       0        0  -17.66 -15.87 -15.36
  stop giornaliero 2%                                   -129.38   +0.84  12.98%      23       0        4  -17.66 -22.03 -15.36
  stop giornaliero 3%                                   -128.22   +2.00  12.86%       2       0        1  -17.66 -15.87 -15.36
  freno di serie: 4 perdite della strategia -> meta'    -127.85   +2.37  12.82%       0      12        0  -18.72 -15.87 -15.25
  freno di serie: 3 perdite della strategia -> meta'    -126.80   +3.42  12.72%       0      20        0  -16.51 -15.87 -15.06
  freno di serie: 4 perdite del bot -> meta'            -122.06   +8.16  12.23%       0      32        0  -17.66 -15.87 -15.36
  freno di serie: 3 perdite del bot -> meta'            -109.59  +20.63  10.98%       0      76        0  -14.90 -13.81 -13.85
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          236    129   -49.34   -0.083
  3-5          199    108   -72.60   -0.126
  6+            46     26    -8.28   -0.162
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92
    2026-10-07 04:18  long   12 aperture  PnL -5.15

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 393 a -0.102R · altri 49 a -0.173R · diff +0.071 ±0.259 -> NON SI VEDE ANCORA
    a size piena sugli stessi 215 trade: +32.49 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 12 a +0.094R · altri 430 a -0.115R · diff +0.209 ±0.847 -> NON SI VEDE ANCORA
    a size piena sugli stessi 10 trade: -1.81 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 109 a -0.177R · altri 46 a +0.099R · diff -0.276 ±0.403 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 115 a -0.156R · altri 327 a -0.093R · diff -0.063 ±0.202 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 142 a -0.175R · altri 251 a -0.061R · diff -0.114 ±0.200 -> NON SI VEDE ANCORA
    a size piena sugli stessi 90 trade: +6.65 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 226 a -0.078R · altri 216 a -0.143R · diff +0.065 ±0.178 -> NON SI VEDE ANCORA
    a size piena sugli stessi 196 trade: +39.40 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.11% · attive 0.21% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 25 a +0.076R · altri 442 a -0.110R · diff +0.186 ±0.386 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 6 trade -0.232R · casuali 423 trade -0.103R · intorno 13 trade -0.281R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 24
  trade chiusi: 25 · vinti 17 · PnL +2.26
    AINUSDT|gen_b6546b33                 1 trade · 1 vinti · +0.57
    ASTERUSDT|gen_b0e86c70               1 trade · 1 vinti · +0.12
    AVAAIUSDT|gen_8b91ba18               1 trade · 0 vinti · -1.54
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
  coppie esplorative poi validate 4 / scartate 654  (il metro: si legge a 100 trade esplorativi)
```
