# 0553-9ott-mattina-trades.req

_eseguito: 2026-10-09 03:47 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 5.5s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 399  (399 con apertura nota)
Giorni coperti:          24
Trade/giorno:            min 1 · media 16.6 · max 40
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 40 · 2026-10-08 39 · 2026-10-09 5
Durata media holding:    3.7h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 14 · media nel tempo 2.7
Coin distinte:           83
Strategie distinte:      137

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      211 108/211    -71.41         0.72R
short     188 108/188    -43.46         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 75 · short 42
  bull_trending      long 37 · short 60
  high_uncertainty   long 28 · short 37
  sideways           long 71 · short 49

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         79 trade · PnL   -15.83
  CONTROTREND     135 trade · PnL   -17.94
  regime neutro   185 trade · PnL   -81.10

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     360  -0.124  -44.47  39 ‖  264  -0.109  -28.72   0
    lordo           360  -0.032  -11.68  39 ‖  264  -0.015   -3.97   0
    costi stimati   360  +0.091  +32.80  39 ‖  264  +0.094  +24.75   0
 direzione
  long              195  -0.213  -41.55  16 ‖  160  -0.198  -31.75   0
  short             165  -0.018   -2.92  23 ‖  104  +0.029   +3.04   0
 regime all'apertura
  bull_trending      82  -0.202  -16.59  15 ‖   41  -0.250  -10.27   0
  bear_trending     111  -0.038   -4.18   6 ‖  100  -0.021   -2.13   0
  sideways          115  -0.133  -15.25   5 ‖   89  -0.089   -7.93   0
  high_uncertainty   52  -0.162   -8.45  13 ‖   34  -0.247   -8.39   0
 rispetto al trend
  in trend           71  -0.039   -2.79   8 ‖   56  +0.048   +2.67   0
  CONTROTREND       122  -0.147  -17.99  13 ‖   85  -0.177  -15.06   0
  regime neutro     167  -0.142  -23.70  18 ‖  123  -0.133  -16.32   0
 direzione x BTC (con = nel verso di BTC)
  long_con           69  -0.177  -12.20   0 ‖   55  -0.133   -7.31   0
  long_contro       112  -0.233  -26.13   0 ‖  105  -0.233  -24.45   0
  short_con          66  -0.053   -3.50   0 ‖   56  -0.061   -3.42   0
  short_contro       68  +0.066   +4.49   0 ‖   48  +0.134   +6.45   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       11  +0.043   +0.48   0 ‖    9  +0.146   +1.31   0
  gen_fa304106        7  -1.068   -7.47   4 ‖    6  -1.064   -6.39   0
  gen_cd5c842f        8  +0.252   +2.02   2 ‖    6  +0.046   +0.28   0
  gen_e59ad90b       10  -0.125   -1.25   0 ‖    9  -0.280   -2.52   0
  gen_4465723e        7  +0.295   +2.07   2 ‖    5  +0.220   +1.10   0
  gen_ceab7f6a        9  -0.563   -5.07   0 ‖    9  -0.563   -5.07   0
  gen_4c6df481        8  -0.037   -0.29   0 ‖    5  +0.045   +0.22   0
  altre 129         286  -0.109  -31.27  31 ‖  215  -0.082  -17.66   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 360 (158 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x158
  classe uscita            x84
  classe ingresso          x74
  controtrend              x54

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    11     0    11   -15.73     4/  3/   0          0        7           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_ceab7f6a     9     3     6    -4.71     4/  2/   0          0        6           0
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_4c6df481     8     4     4     0.60     2/  2/   0          0        4           0
  gen_bb762669    11     7     4     5.83     2/  2/   0          0        4           0
  ultimi referti in perdita:
   - CVCUSDT gen_cb4d9121 long -0.85: a favore fino a 0.28R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - CROSSUSDT gen_4e6e1ae0 long -2.55: a favore fino a 0.33R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - QUSDT gen_18c839a0 short -4.13: mai andato a favore (mfe 0.24R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - XPINUSDT gen_2e0818c8 short -2.47: mai andato a favore (mfe 0.00R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - HEMIUSDT gen_acea368d short -1.61: mai andato a favore (mfe 0.00R): direzione sbagliata
   - OPENUSDT gen_46f0717f short -1.20: a favore fino a 0.86R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)

PAPER CONTRO IL CASO (K4): il paper (399 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  45%         46%
  stop ingresso/uscita (su 179)     45/54%  48.5/51.5%
  massimo toccato mediano            0.80R       0.81R
  arrivati al primo target             12%         17%
  vinti                                54%         54%
  R medio (su 360)                  -0.124      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            38/69 -15.45  57/112 -37.18    39/66 -5.60    43/68 +7.09      84
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/6 +2.68       1
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_ceab7f6a        3/7 -3.25      0/2 -1.47              —              —       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_4c6df481        2/3 +3.30      1/3 -2.41              —      1/2 -0.29       0
  gen_cd5c842f                —      2/3 +1.09      2/3 +4.14      1/1 +0.95       3
  gen_4465723e        1/1 +1.88      2/3 -0.08      2/2 +1.55              —       3
  gen_8b91ba18        2/4 -1.48              —      1/1 +0.83      0/1 -1.64       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   11 perdite di fila  (freno spento)
  gen_ceab7f6a   4 perdite di fila  (freno spento)
  gen_bf2be656   3 perdite di fila
  gen_14e1775b   2 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_4c6df481   2 perdite di fila
  gen_4e6e1ae0   2 perdite di fila
  gen_4f890271   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_60c9259a   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-09 03:33 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3)
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 11 (campione 4)
  - gen_fa304106: controtrend_btc — 4/4 persi contro il contesto BTC (campione 4)
  - gen_fa304106: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.60 R) (campione 3)
  - gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - gen_fa304106: solo_short — long 6/6 persi (campione 6)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_ceab7f6a           4/3             49.19|33.89               0.86|0.92             0.50%|0.56%             47.49|44.76
  gen_fa304106           4/0               37.26|n/d  

[... 260 caratteri omessi (testa e coda conservate) ...]

g sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_cd5c842f          5     3 (rumore 0)        2        -        0.57
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_4465723e          4     2 (rumore 0)        2        -        0.61
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_4c6df481          4     3 (rumore 3)        1        -        0.69
  gen_902fb1fd          4     2 (rumore 0)        2        -        0.80
  gen_c647ead7          4     3 (rumore 0)        1        -        0.73
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_725cb5f4          3     0 (rumore 0)        3        -        0.91
  gen_8981d5f2          3     1 (rumore 1)        2        -        0.66
  gen_8b91ba18          3     1 (rumore 0)        2        -        0.72
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  gen_c5194ce4          3     1 (rumore 0)        2        -        0.85
  gen_dfb554f7          3     1 (rumore 0)        2        -        0.72
  gen_f3661202          3     1 (rumore 1)        2        -        0.80
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  + altre 64 strategie con meno verdetti: 88 verdetti, prematuri 43, protetti 45
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 327  (vinti 186, persi 141; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.650   p media dei persi: 0.637   (se p predice, la prima e' piu' alta)
  sopra la soglia: 327/327 trade, PnL -49.76 contro -49.76 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.106
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 399 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.70     133       50%     -0.92%
    0.71-0.87     133       58%     +0.15%
    0.87-1.00     133       55%     -0.37%
  FEAR & GREED all'apertura (398 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         396       54%     -0.39%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    177 trade · 98 vinti · PnL -16.10 · R medio -0.101R su 177
  attive        222 trade · 118 vinti · PnL -98.78 · R medio -0.146R su 183
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 177 trade R -0.101 · attive 87 trade R -0.125 · differenza +0.024R, margine ±0.261R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   138  ‖            113   -0.070 ‖          93   -0.100
  ALLENTATA                            4  ‖              7   +0.477 ‖           4   +0.782
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato                96  ‖            104   -0.184 ‖          96   -0.163
  trade di coppie non piu' validate       ‖            136   -0.153 ‖          71   -0.097
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 10-08
  com'e' andato davvero                                 -114.88   +0.00  11.64%       0       0        0  -17.66 -15.87 -15.36
  stop giornaliero 2%                                   -109.78   +5.10  11.13%      11       0        2  -17.66 -22.03 -15.36
  stop giornaliero 3%                                   -112.87   +2.01  11.43%       2       0        1  -17.66 -15.87 -15.36
  freno di serie: 4 perdite della strategia -> meta'    -112.75   +2.13  11.42%       0      10        0  -18.72 -15.87 -15.25
  freno di serie: 3 perdite della strategia -> meta'    -111.70   +3.18  11.32%       0      18        0  -16.51 -15.87 -15.06
  freno di serie: 4 perdite del bot -> meta'            -108.24   +6.64  10.97%       0      23        0  -17.66 -15.87 -15.36
  freno di serie: 3 perdite del bot -> meta'             -98.30  +16.58   9.98%       0      62        0  -14.90 -13.81 -13.85
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          203    114   -38.20   -0.061
  3-5          161     85   -64.37   -0.156
  6+            35     17   -12.30   -0.303
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92
    2026-10-07 04:18  long   12 aperture  PnL -5.15

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 311 a -0.116R · altri 49 a -0.173R · diff +0.057 ±0.263 -> NON SI VEDE ANCORA
    a size piena sugli stessi 175 trade: +24.72 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 8 a +0.057R · altri 352 a -0.128R -> CAMPIONE PICCOLO
    a size piena sugli stessi 6 trade: -1.46 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 89 a -0.150R · altri 36 a -0.111R · diff -0.039 ±0.446 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 95 a -0.126R · altri 265 a -0.123R · diff -0.003 ±0.222 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 115 a -0.169R · altri 196 a -0.085R · diff -0.084 ±0.222 -> NON SI VEDE ANCORA
    a size piena sugli stessi 78 trade: +3.34 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 177 a -0.101R · altri 183 a -0.146R · diff +0.045 ±0.197 -> NON SI VEDE ANCORA
    a size piena sugli stessi 158 trade: +39.24 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 18 a +0.149R · altri 360 a -0.124R · diff +0.273 ±0.449 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 6 trade -0.232R · casuali 349 trade -0.112R · intorno 5 trade -0.831R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 42
  trade chiusi: 18 · vinti 13 · PnL +3.60
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_8aec28c6                 1 trade · 0 vinti · -0.99
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
  coppie esplorative poi validate 4 / scartate 502  (il metro: si legge a 100 trade esplorativi)
```
