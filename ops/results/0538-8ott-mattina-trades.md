# 0538-8ott-mattina-trades.req

_eseguito: 2026-10-08 03:47 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 6.1s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 362  (362 con apertura nota)
Giorni coperti:          23
Trade/giorno:            min 1 · media 15.7 · max 40
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 25 · 2026-10-07 40 · 2026-10-08 7
Durata media holding:    3.8h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 14 · media nel tempo 2.6
Coin distinte:           76
Strategie distinte:      125

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      185  95/185    -57.49         0.76R
short     177 101/177    -41.00         0.86R

Regime ALL'APERTURA x direzione:
  bear_trending      long 60 · short 36
  bull_trending      long 35 · short 58
  high_uncertainty   long 25 · short 35
  sideways           long 65 · short 48

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         71 trade · PnL   -15.14
  CONTROTREND     118 trade · PnL    -7.86
  regime neutro   173 trade · PnL   -75.48

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     323  -0.120  -38.65  39 ‖  227  -0.101  -22.89   0
    lordo           323  -0.027   -8.57  39 ‖  227  -0.004   -0.87   0
    costi stimati   323  +0.093  +30.07  39 ‖  227  +0.097  +22.02   0
 direzione
  long              169  -0.208  -35.19  16 ‖  134  -0.190  -25.40   0
  short             154  -0.022   -3.45  23 ‖   93  +0.027   +2.50   0
 regime all'apertura
  bull_trending      78  -0.178  -13.89  15 ‖   37  -0.204   -7.56   0
  bear_trending      90  -0.057   -5.12   6 ‖   79  -0.039   -3.07   0
  sideways          108  -0.109  -11.76   5 ‖   82  -0.054   -4.44   0
  high_uncertainty   47  -0.168   -7.88  13 ‖   29  -0.270   -7.82   0
 rispetto al trend
  in trend           63  -0.033   -2.07   8 ‖   48  +0.071   +3.39   0
  CONTROTREND       105  -0.161  -16.94  13 ‖   68  -0.206  -14.02   0
  regime neutro     155  -0.127  -19.64  18 ‖  111  -0.110  -12.26   0
 direzione x BTC (con = nel verso di BTC)
  long_con           69  -0.177  -12.20   0 ‖   55  -0.133   -7.31   0
  long_contro        86  -0.230  -19.78   0 ‖   79  -0.229  -18.09   0
  short_con          55  -0.073   -4.03   0 ‖   45  -0.088   -3.95   0
  short_contro       68  +0.066   +4.49   0 ‖   48  +0.134   +6.45   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       11  +0.043   +0.48   0 ‖    9  +0.146   +1.31   0
  gen_cd5c842f        8  +0.252   +2.02   2 ‖    6  +0.046   +0.28   0
  gen_e59ad90b       10  -0.125   -1.25   0 ‖    9  -0.280   -2.52   0
  gen_fa304106        6  -1.049   -6.30   4 ‖    5  -1.042   -5.21   0
  gen_4465723e        6  +0.246   +1.48   2 ‖    4  +0.129   +0.51   0
  gen_ceab7f6a        8  -0.493   -3.95   0 ‖    8  -0.493   -3.95   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  altre 117         258  -0.112  -28.89  26 ‖  186  -0.072  -13.32   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 323 (141 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x141
  classe uscita            x74
  classe ingresso          x67
  controtrend              x47

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106    10     0    10   -15.50     4/  2/   0          0        6           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_ceab7f6a     8     3     5    -4.22     3/  2/   0          0        5           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_bb762669    11     7     4     5.83     2/  2/   0          0        4           0
  gen_e59ad90b    10     6     4    -0.27     3/  1/   0          0        4           3
  ultimi referti in perdita:
   - XPINUSDT gen_9a383fff long -3.14: a favore fino a 0.45R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - SPXUSDT gen_d03ff6d4 long -0.61: mai andato a favore (mfe 0.20R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - UBUSDT gen_2a2898b0 short -1.30: mai andato a favore (mfe 0.04R): direzione sbagliata
   - AXSUSDT gen_b922252e long -1.62: mai andato a favore (mfe 0.01R): direzione sbagliata
   - JASMYUSDT gen_b2f350ff long -0.41: a favore fino a 0.94R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - ASTERUSDT gen_96efce1b long -0.57: a favore fino a 0.79R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)

PAPER CONTRO IL CASO (K4): il paper (362 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  45%         46%
  stop ingresso/uscita (su 162)     46/54%  48.5/51.5%
  massimo toccato mediano            0.81R       0.81R
  arrivati al primo target             12%         17%
  vinti                                54%         54%
  R medio (su 323)                  -0.120      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            38/69 -15.45   44/86 -23.25    32/55 -3.14    43/68 +7.09      84
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/6 +2.68       1
  gen_e59ad90b                —      1/4 -5.12      2/2 +4.33      3/4 +0.51       0
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_ceab7f6a        3/7 -3.25      0/1 -0.97              —              —       0
  gen_4c6df481        2/3 +3.30      1/2 -0.70              —      1/2 -0.29       0
  gen_cd5c842f                —      2/3 +1.09      2/3 +4.14      1/1 +0.95       3
  gen_a640dfa5                —              —              —      4/6 +1.26       0
  gen_c647ead7                —      4/5 -1.03      0/1 -1.53              —       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   10 perdite di fila  (freno spento)
  gen_bf2be656   3 perdite di fila
  gen_ceab7f6a   3 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_4f890271   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_60c9259a   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_96c1ed1b   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-08 03:33 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_8b91ba18: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.62 R) (campione 3)
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_e59ad90b: conferma_trend — 3 perdite controtrend (campione 3)
  - gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 10 (campione 4)
  - gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)
  - gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - gen_fa304106: solo_short — long 5/5 persi (campione 5)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fa304106           4/0               37.26|n/d                1.10|n/d               1.12%|n/d               44.82|n/d
  gen_fca11c08           6/7             45.68|42.58               1.92|1.05             0.86%|0.75%             72.33|72.21

KEEP PER STRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_cd5c842f          5     3 (rumore 0)        2        -        0.57
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_4465723e          4     2 (rumore 0)        2        -        0.61
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_4c6df481          4     3 (rumore 3)        1        -        0.69
  gen_c647ead7          4     3 (rumore 0)        1        -        0.73
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_725cb5f4          3     0 (rumore 0)        3        -        0.91
  gen_8981d5f2          3     1 (rumore 1)        2        -        0.66
  gen_902fb1fd          3     1 (rumore 0)        2        -        0.77
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  gen_dfb554f7          3     1 (rumore 0)        2        -        0.72
  gen_f3661202          3     1 (rumore 1)        2        -        0.80
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_1eec02f5          2     2 (rumore 1)        0        -        0.80
  gen_1f7ead60          2     2 (rumore 1)        0        -        0.78
  + altre 57 strategie con meno verdetti: 78 verdetti, prematuri 34, protetti 44
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 290  (vinti 166, persi 124; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.649   p media dei persi: 0.636   (se p predice, la prima e' piu' alta)
  sopra la soglia: 290/290 trade, PnL -33.37 contro -33.37 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.110
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 362 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.73     120       51%     -0.77%
    0.73-0.88     120       57%     +0.04%
    0.88-1.00     122       55%     -0.37%
  FEAR & GREED all'apertura (361 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         359       54%     -0.38%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    158 trade · 85 vinti · PnL -20.08 · R medio -0.129R su 158
  attive        204 trade · 111 vinti · PnL -78.41 · R medio -0.110R su 165
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 158 trade R -0.129 · attive 69 trade R -0.036 · differenza -0.094R, margine ±0.281R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   129  ‖            111   -0.099 ‖          83   -0.101
  ALLENTATA                            7  ‖             17   +0.223 ‖          12   +0.153
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               143  ‖            147   -0.141 ‖         128   -0.130
  trade di coppie non piu' validate       ‖             48   -0.222 ‖           4   +0.088
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -98.49   +0.00   9.93%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -93.39   +5.10   9.42%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -96.48   +2.01   9.73%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -96.48   +2.01   9.73%       0       9        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -95.67   +2.82   9.64%       0      16        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -91.85   +6.64   9.26%       0      23        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -83.41  +15.08   8.42%       0      55        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          190    105   -40.20   -0.078
  3-5          142     75   -51.61   -0.152
  6+            30     16    -6.67   -0.205
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92
    2026-10-07 04:18  long   12 aperture  PnL -5.15

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 274 a -0.110R · altri 49 a -0.173R · diff +0.063 ±0.267 -> NON SI VEDE ANCORA
    a size piena sugli stessi 151 trade: +24.30 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 4 a +0.822R · altri 319 a -0.131R -> CAMPIONE PICCOLO
    a size piena sugli stessi 3 trade: -2.14 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 79 a -0.178R · altri 29 a -0.048R · diff -0.130 ±0.510 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 86 a -0.146R · altri 237 a -0.110R · diff -0.036 ±0.234 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 96 a -0.170R · altri 178 a -0.078R · diff -0.092 ±0.241 -> NON SI VEDE ANCORA
    a size piena sugli stessi 65 trade: +4.32 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 158 a -0.129R · altri 165 a -0.110R · diff -0.019 ±0.208 -> NON SI VEDE ANCORA
    a size piena sugli stessi 139 trade: +51.17 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 15 a -0.023R · altri 323 a -0.120R · diff +0.097 ±0.454 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 6 trade -0.232R · casuali 313 trade -0.109R · intorno 4 trade -0.774R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 38
  trade chiusi: 15 · vinti 10 · PnL +0.44
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_8aec28c6                 1 trade · 0 vinti · -0.99
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
  coppie esplorative poi validate 4 / scartate 468  (il metro: si legge a 100 trade esplorativi)
```
