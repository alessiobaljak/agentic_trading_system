# 0620-16ott-lettura14-trades.req

_eseguito: 2026-10-16 05:40 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 9.0s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 612  (612 con apertura nota)
Giorni coperti:          31
Trade/giorno:            min 1 · media 19.7 · max 51
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 40 · 2026-10-08 39 · 2026-10-09 24 · 2026-10-10 16 · 2026-10-11 25 · 2026-10-12 32 · 2026-10-13 51 · 2026-10-14 35 · 2026-10-15 25 · 2026-10-16 10
Durata media holding:    3.7h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 14 · media nel tempo 3.2
Coin distinte:           98
Strategie distinte:      192

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      353 187/353   -102.83         0.69R
short     259 149/259    -59.34         0.83R

Regime ALL'APERTURA x direzione:
  bear_trending      long 153 · short 59
  bull_trending      long 54 · short 82
  high_uncertainty   long 51 · short 50
  sideways           long 95 · short 68

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend        113 trade · PnL    -7.67
  CONTROTREND     235 trade · PnL   -61.22
  regime neutro   264 trade · PnL   -93.29

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     573  -0.116  -66.72  39 ‖  477  -0.107  -50.97   0
    lordo           573  -0.028  -15.91  39 ‖  477  -0.017   -8.21   0
    costi stimati   573  +0.089  +50.81  39 ‖  477  +0.090  +42.76   0
 direzione
  long              337  -0.167  -56.22  16 ‖  302  -0.154  -46.42   0
  short             236  -0.045  -10.50  23 ‖  175  -0.026   -4.55   0
 regime all'apertura
  bull_trending     121  -0.174  -21.01  15 ‖   80  -0.184  -14.68   0
  bear_trending     206  -0.098  -20.11   6 ‖  195  -0.093  -18.06   0
  sideways          158  -0.168  -26.56   5 ‖  132  -0.146  -19.23   0
  high_uncertainty   88  +0.011   +0.95  13 ‖   70  +0.014   +1.00   0
 rispetto al trend
  in trend          105  -0.007   -0.77   8 ‖   90  +0.052   +4.68   0
  CONTROTREND       222  -0.182  -40.34  13 ‖  185  -0.202  -37.42   0
  regime neutro     246  -0.104  -25.61  18 ‖  202  -0.090  -18.23   0
 direzione x BTC (con = nel verso di BTC)
  long_con          142  -0.165  -23.50   0 ‖  128  -0.145  -18.61   0
  long_contro       181  -0.163  -29.51   0 ‖  174  -0.160  -27.82   0
  short_con          86  -0.056   -4.81   0 ‖   76  -0.062   -4.72   0
  short_contro      119  -0.015   -1.78   0 ‖   99  +0.002   +0.18   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_ceab7f6a       15  -0.221   -3.32   0 ‖   15  -0.221   -3.32   0
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       12  -0.050   -0.61   0 ‖   10  +0.023   +0.23   0
  gen_684d7623       11  -0.183   -2.01   0 ‖   11  -0.183   -2.01   0
  gen_fa304106        7  -1.068   -7.47   4 ‖    6  -1.064   -6.39   0
  gen_4c6df481       10  -0.015   -0.15   0 ‖    7  +0.052   +0.36   0
  gen_cd5c842f        8  +0.252   +2.02   2 ‖    6  +0.046   +0.28   0
  gen_e59ad90b       10  -0.125   -1.25   0 ‖    9  -0.280   -2.52   0
  altre 184         486  -0.103  -50.25  33 ‖  413  -0.091  -37.60   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 573 (251 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x251
  classe uscita            x126
  classe ingresso          x125
  controtrend              x105

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    11     0    11   -15.73     4/  3/   0          0        7           0
  gen_ceab7f6a    15     8     7    -3.60     5/  2/   0          0        7           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_4c6df481    10     5     5     0.48     2/  3/   0          0        5           0
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_bb762669    12     7     5     4.68     3/  2/   0          0        5           0
  gen_18c839a0     8     4     4    -7.07     3/  1/   0          0        4           2
  ultimi referti in perdita:
   - TRUMPUSDT gen_d16d1d02 short -2.92: a favore fino a 0.60R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - MAVIAUSDT gen_608b892e short -2.12: mai andato a favore (mfe 0.13R): direzione sbagliata
   - HEMIUSDT gen_acea368d short -2.33: mai andato a favore (mfe 0.05R): direzione sbagliata
   - PARTIUSDT gen_b50fc231 short -1.68: mai andato a favore (mfe 0.04R): direzione sbagliata
   - OPENUSDT gen_46f0717f long -1.06: a favore fino a 0.30R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - STXUSDT gen_a5b0e4de long -1.04: mai andato a favore (mfe 0.00R): direzione sbagliata

PAPER CONTRO IL CASO (K4): il paper (612 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 271)     48/51%  48.5/51.5%
  massimo toccato mediano            0.77R       0.81R
  arrivati al primo target             11%         17%
  vinti                                55%         54%
  R medio (su 573)                  -0.116      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte           78/142 -39.24  96/181 -44.81    51/86 -6.20   72/119 -8.20      84
  gen_ceab7f6a       8/12 -1.56      0/2 -1.47      0/1 -0.58              —       0
  gen_684d7623        2/3 +0.00      4/7 -1.04      1/1 +0.99              —       0
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/7 +1.52       1
  gen_4c6df481        3/4 +3.42      1/3 -2.41              —      1/3 -0.53       0
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_c647ead7        1/1 +0.81      4/7 -3.22      0/1 -1.53              —       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_5905e08d                —              —      2/2 +2.03      2/5 -3.80       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   11 perdite di fila  (freno spento)
  gen_18c839a0   3 perdite di fila
  gen_7b4a474b   3 perdite di fila
  gen_871647b8   3 perdite di fila
  gen_96c1ed1b   3 perdite di fila
  gen_bb762669   3 perdite di fila
  gen_bf2be656   3 perdite di fila
  gen_e6ddc613   3 perdite di fila
  gen_08664b28   2 perdite di fila
  gen_0d7be682   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-16 05:33 UTC): decided — parita' backtest: 1 segnali validi aperti
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_01fbe76f: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)
  - gen_4c6df481: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.79 R) (campione 3)
  - gen_5905e08d: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_5905e08d: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.47 R) (campione 3)
  - gen_684d7623: conferma_trend — 4 perdite controtrend (campione 4)
  - gen_871647b8: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_871647b8: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)
  - gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3)
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_c5194ce4: ingresso_atr_pct — 4 perdite d'ingresso su 4 con volatilita' alta (ATR > 0.66% del prezzo) (mediana 0.92%), vinti mediana 0.61% (campione 4)
  - gen_c647ead7: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_c647ead7: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.74 R) (campione 3)
  - gen_ceab7f6a: ingresso_vol_ratio — 4 perdite d'ingresso su 5 con volume sotto la media (vol_ratio < 1) (mediana 0.71), vinti mediana 1.03 (campione 5)
  - g

[... 1533 caratteri omessi (testa e coda conservate) ...]

egia      verdetti        prematuri protetti proposta  miss medio
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
  gen_01fbe76f          3     1 (rumore 1)        2        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_1eec02f5          3     2 (rumore 1)        1        -        0.81
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_35632db9          3     1 (rumore 0)        2        -        0.65
  gen_4810faab          3     1 (rumore 0)        2        -        0.79
  + altre 109 strategie con meno verdetti: 161 verdetti, prematuri 78, protetti 83
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 540  (vinti 306, persi 234; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.658   p media dei persi: 0.645   (se p predice, la prima e' piu' alta)
  sopra la soglia: 540/540 trade, PnL -97.06 contro -97.06 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.102
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 612 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.68     204       52%     -0.49%
    0.68-0.87     204       60%     -0.10%
    0.87-1.00     204       52%     -0.49%
  FEAR & GREED all'apertura (611 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         609       55%     -0.37%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    283 trade · 158 vinti · PnL -25.78 · R medio -0.098R su 283
  attive        329 trade · 178 vinti · PnL -136.40 · R medio -0.134R su 290
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 283 trade R -0.098 · attive 194 trade R -0.119 · differenza +0.021R, margine ±0.174R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   207  ‖            230   -0.082 ‖         219   -0.094
  ALLENTATA                            0  ‖              0        — ‖           0        —
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato                42  ‖             53   -0.148 ‖          53   -0.148
  trade di coppie non piu' validate       ‖            290   -0.138 ‖         205   -0.110
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  10-13 10-15 09-23
  com'e' andato davvero                                 -162.17   +0.00  17.51%       0       0        0  -24.45 -19.81 -17.66
  stop giornaliero 2%                                   -162.48   -0.31  17.42%      61       0        6  -26.73 -20.43 -17.66
  stop giornaliero 3%                                   -160.02   +2.15  17.30%      37       0        2  -26.73 -19.81 -17.66
  freno di serie: 4 perdite della strategia -> meta'    -160.21   +1.96  17.28%       0      13        0  -24.45 -19.81 -18.72
  freno di serie: 3 perdite della strategia -> meta'    -159.72   +2.45  17.23%       0      23        0  -24.78 -19.81 -16.51
  freno di serie: 4 perdite del bot -> meta'            -160.87   +1.30  17.35%       0      47        0  -28.20 -20.12 -17.66
  freno di serie: 3 perdite del bot -> meta'            -148.41  +13.76  16.11%       0      91        0  -28.20 -20.12 -14.90
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          272    151   -48.57   -0.089
  3-5          270    147   -94.55   -0.122
  6+            70     38   -19.05   -0.193
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92
    2026-10-07 04:18  long   12 aperture  PnL -5.15
    2026-10-13 02:17  long    8 aperture  PnL -12.39
    2026-10-13 03:03  long    9 aperture  PnL +9.98

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 524 a -0.111R · altri 49 a -0.173R · diff +0.062 ±0.254 -> NON SI VEDE ANCORA
    a size piena sugli stessi 281 trade: +51.60 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 12 a +0.094R · altri 561 a -0.121R · diff +0.215 ±0.846 -> NON SI VEDE ANCORA
    a size piena sugli stessi 10 trade: -1.81 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 150 a -0.179R · altri 59 a -0.022R · diff -0.157 ±0.341 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 154 a -0.152R · altri 419 a -0.103R · diff -0.049 ±0.175 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 220 a -0.187R · altri 304 a -0.056R · diff -0.131 ±0.166 -> NON SI VEDE ANCORA
    a size piena sugli stessi 142 trade: +8.77 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 283 a -0.098R · altri 290 a -0.134R · diff +0.036 ±0.156 -> NON SI VEDE ANCORA
    a size piena sugli stessi 248 trade: +70.35 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.11% · attive 0.23% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 35 a -0.081R · altri 573 a -0.116R · diff +0.035 ±0.327 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 13 trade -0.339R · casuali 542 trade -0.104R · intorno 18 trade -0.344R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 25
  trade chiusi: 35 · vinti 21 · PnL -2.30
    AVAAIUSDT|gen_8b91ba18               2 trade · 0 vinti · -2.56
    DEXEUSDT|gen_e50a9211                2 trade · 0 vinti · -2.70
    MITOUSDT|gen_0919b67a                2 trade · 1 vinti · -0.39
    AINUSDT|gen_b6546b33                 1 trade · 1 vinti · +0.57
    AIOUSDT|gen_7027edb8                 1 trade · 0 vinti · -0.82
  coppie esplorative poi validate 4 / scartate 694  (il metro: si legge a 100 trade esplorativi)
```
