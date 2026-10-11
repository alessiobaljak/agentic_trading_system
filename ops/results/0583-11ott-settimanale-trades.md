# 0583-11ott-settimanale-trades.req

_eseguito: 2026-10-11 03:47 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 6.7s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 437  (437 con apertura nota)
Giorni coperti:          26
Trade/giorno:            min 1 · media 16.8 · max 40
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 40 · 2026-10-08 39 · 2026-10-09 24 · 2026-10-10 16 · 2026-10-11 3
Durata media holding:    3.9h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 14 · media nel tempo 2.9
Coin distinte:           88
Strategie distinte:      146

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      234 126/234    -63.83         0.77R
short     203 116/203    -48.11         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 80 · short 45
  bull_trending      long 42 · short 64
  high_uncertainty   long 36 · short 41
  sideways           long 76 · short 53

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         87 trade · PnL   -18.24
  CONTROTREND     144 trade · PnL   -14.53
  regime neutro   206 trade · PnL   -79.17

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     398  -0.097  -38.57  39 ‖  302  -0.076  -22.81   0
    lordo           398  -0.004   -1.46  39 ‖  302  +0.021   +6.24   0
    costi stimati   398  +0.093  +37.11  39 ‖  302  +0.096  +29.06   0
 direzione
  long              218  -0.144  -31.47  16 ‖  183  -0.118  -21.67   0
  short             180  -0.039   -7.10  23 ‖  119  -0.010   -1.14   0
 regime all'apertura
  bull_trending      91  -0.188  -17.08  15 ‖   50  -0.215  -10.75   0
  bear_trending     119  -0.015   -1.76   6 ‖  108  +0.003   +0.29   0
  sideways          124  -0.109  -13.46   5 ‖   98  -0.063   -6.14   0
  high_uncertainty   64  -0.098   -6.27  13 ‖   46  -0.135   -6.21   0
 rispetto al trend
  in trend           79  -0.055   -4.35   8 ‖   64  +0.017   +1.11   0
  CONTROTREND       131  -0.111  -14.49  13 ‖   94  -0.123  -11.57   0
  regime neutro     188  -0.105  -19.73  18 ‖  144  -0.086  -12.35   0
 direzione x BTC (con = nel verso di BTC)
  long_con           84  -0.116   -9.73   0 ‖   70  -0.069   -4.83   0
  long_contro       120  -0.154  -18.53   0 ‖  113  -0.149  -16.84   0
  short_con          69  -0.089   -6.13   0 ‖   59  -0.103   -6.05   0
  short_contro       80  +0.037   +2.94   0 ‖   60  +0.082   +4.91   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_ceab7f6a       13  -0.343   -4.46   0 ‖   13  -0.343   -4.46   0
  gen_bb762669       11  +0.043   +0.48   0 ‖    9  +0.146   +1.31   0
  gen_fa304106        7  -1.068   -7.47   4 ‖    6  -1.064   -6.39   0
  gen_cd5c842f        8  +0.252   +2.02   2 ‖    6  +0.046   +0.28   0
  gen_e59ad90b       10  -0.125   -1.25   0 ‖    9  -0.280   -2.52   0
  gen_4465723e        7  +0.295   +2.07   2 ‖    5  +0.220   +1.10   0
  gen_4c6df481        9  +0.110   +0.99   0 ‖    6  +0.252   +1.51   0
  altre 138         319  -0.085  -27.26  31 ‖  248  -0.055  -13.65   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 398 (170 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x170
  classe uscita            x90
  classe ingresso          x80
  controtrend              x57

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    11     0    11   -15.73     4/  3/   0          0        7           0
  gen_ceab7f6a    13     6     7    -4.39     5/  2/   0          0        7           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_4c6df481     9     5     4     0.73     2/  2/   0          0        4           0
  gen_bb762669    11     7     4     5.83     2/  2/   0          0        4           0
  ultimi referti in perdita:
   - PUNDIXUSDT gen_96c1ed1b short -1.63: mai andato a favore (mfe 0.00R): direzione sbagliata
   - CATIUSDT gen_b3e46005 long -2.19: mai andato a favore (mfe 0.04R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - BULLAUSDT gen_7ac562e3 short -1.09: a favore fino a 0.60R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R) · controtrend rispetto al regime all'ingresso
   - UBUSDT gen_0d7be682 long -1.27: mai andato a favore (mfe 0.04R): direzione sbagliata
   - SAHARAUSDT gen_6b94025f short -0.89: a favore fino a 0.91R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - QUSDT gen_18c839a0 short -1.53: mai andato a favore (mfe 0.00R): direzione sbagliata

PAPER CONTRO IL CASO (K4): il paper (437 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 190)     45/54%  48.5/51.5%
  massimo toccato mediano            0.81R       0.81R
  arrivati al primo target             12%         17%
  vinti                                55%         54%
  R medio (su 398)                  -0.097      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            49/84 -16.09  64/120 -28.96    39/69 -8.91    51/80 +5.74      84
  gen_ceab7f6a       6/10 -2.34      0/2 -1.47      0/1 -0.58              —       0
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/6 +2.68       1
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_4c6df481        3/4 +3.42      1/3 -2.41              —      1/2 -0.29       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_cd5c842f                —      2/3 +1.09      2/3 +4.14      1/1 +0.95       3
  gen_4465723e        1/1 +1.88      2/3 -0.08      2/2 +1.55              —       3
  gen_8b91ba18        2/4 -1.48              —      1/1 +0.83      0/1 -1.64       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   11 perdite di fila  (freno spento)
  gen_96c1ed1b   3 perdite di fila
  gen_bf2be656   3 perdite di fila
  gen_14e1775b   2 perdite di fila
  gen_18c839a0   2 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_4e6e1ae0   2 perdite di fila
  gen_4f890271   2 perdite di fila
  gen_60c9259a   2 perdite di fila
  gen_7ac562e3   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-11 03:32 UTC): decided — parita' backtest: 1 segnali validi aperti
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
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

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi

[... 671 caratteri omessi (testa e coda conservate) ...]

5 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_4465723e          5     2 (rumore 0)        3     0.75        0.60
  gen_4c6df481          5     4 (rumore 3)        1     0.25        0.63
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_cd5c842f          5     3 (rumore 0)        2        -        0.57
  gen_ceab7f6a          5     1 (rumore 0)        4     0.75        0.82
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
  gen_725cb5f4          3     0 (rumore 0)        3        -        0.91
  gen_771790b1          3     2 (rumore 0)        1        -        0.62
  gen_8981d5f2          3     1 (rumore 1)        2        -        0.66
  gen_8b91ba18          3     1 (rumore 0)        2        -        0.72
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  + altre 75 strategie con meno verdetti: 104 verdetti, prematuri 49, protetti 55
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 365  (vinti 212, persi 153; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.650   p media dei persi: 0.638   (se p predice, la prima e' piu' alta)
  sopra la soglia: 365/365 trade, PnL -46.82 contro -46.82 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.102
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 437 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.71     145       53%     -0.62%
    0.72-0.87     145       59%     +0.09%
    0.87-1.00     147       54%     -0.41%
  FEAR & GREED all'apertura (436 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         434       55%     -0.32%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    204 trade · 116 vinti · PnL -15.52 · R medio -0.069R su 204
  attive        233 trade · 126 vinti · PnL -96.42 · R medio -0.126R su 194
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 204 trade R -0.069 · attive 98 trade R -0.089 · differenza +0.020R, margine ±0.240R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   162  ‖            103   +0.009 ‖          89   -0.010
  ALLENTATA                            3  ‖              5   +0.410 ‖           3   +0.864
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato                74  ‖             78   -0.157 ‖          78   -0.157
  trade di coppie non piu' validate       ‖            212   -0.138 ‖         132   -0.093
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 10-08
  com'e' andato davvero                                 -111.94   +0.00  11.64%       0       0        0  -17.66 -15.87 -15.36
  stop giornaliero 2%                                   -106.27   +5.67  11.13%      12       0        3  -17.66 -22.03 -15.36
  stop giornaliero 3%                                   -109.93   +2.01  11.43%       2       0        1  -17.66 -15.87 -15.36
  freno di serie: 4 perdite della strategia -> meta'    -109.57   +2.37  11.42%       0      12        0  -18.72 -15.87 -15.25
  freno di serie: 3 perdite della strategia -> meta'    -108.51   +3.43  11.32%       0      20        0  -16.51 -15.87 -15.06
  freno di serie: 4 perdite del bot -> meta'            -105.30   +6.64  10.97%       0      23        0  -17.66 -15.87 -15.36
  freno di serie: 3 perdite del bot -> meta'             -96.04  +15.90   9.98%       0      63        0  -14.90 -13.81 -13.85
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          218    124   -38.90   -0.049
  3-5          174     93   -64.65   -0.132
  6+            45     25    -8.38   -0.172
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92
    2026-10-07 04:18  long   12 aperture  PnL -5.15

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 349 a -0.086R · altri 49 a -0.173R · diff +0.087 ±0.261 -> NON SI VEDE ANCORA
    a size piena sugli stessi 195 trade: +23.65 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 10 a +0.203R · altri 388 a -0.105R · diff +0.308 ±0.987 -> NON SI VEDE ANCORA
    a size piena sugli stessi 8 trade: -1.98 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 100 a -0.171R · altri 40 a -0.025R · diff -0.146 ±0.415 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 106 a -0.148R · altri 292 a -0.078R · diff -0.070 ±0.210 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 124 a -0.129R · altri 225 a -0.063R · diff -0.066 ±0.215 -> NON SI VEDE ANCORA
    a size piena sugli stessi 81 trade: +1.97 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 204 a -0.069R · altri 194 a -0.126R · diff +0.057 ±0.186 -> NON SI VEDE ANCORA
    a size piena sugli stessi 178 trade: +36.76 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 21 a +0.110R · altri 398 a -0.097R · diff +0.207 ±0.405 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 6 trade -0.232R · casuali 383 trade -0.087R · intorno 9 trade -0.431R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 36
  trade chiusi: 21 · vinti 15 · PnL +2.75
    AINUSDT|gen_b6546b33                 1 trade · 1 vinti · +0.57
    ASTERUSDT|gen_b0e86c70               1 trade · 1 vinti · +0.12
    AVAAIUSDT|gen_8b91ba18               1 trade · 0 vinti · -1.54
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
  coppie esplorative poi validate 4 / scartate 587  (il metro: si legge a 100 trade esplorativi)
```
