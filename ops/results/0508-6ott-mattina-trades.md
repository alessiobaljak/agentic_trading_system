# 0508-6ott-mattina-trades.req

_eseguito: 2026-10-06 06:05 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 4.9s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 297  (297 con apertura nota)
Giorni coperti:          21
Trade/giorno:            min 1 · media 14.1 · max 32
  per giorno (ora italiana): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 29 · 2026-09-26 21 · 2026-09-27 32 · 2026-09-28 21 · 2026-09-29 23 · 2026-09-30 14 · 2026-10-01 15 · 2026-10-02 23 · 2026-10-03 16 · 2026-10-04 20 · 2026-10-05 23 · 2026-10-06 7
Durata media holding:    3.7h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 12 · media nel tempo 2.4
Coin distinte:           71
Strategie distinte:      113

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long      136  73/136    -41.05         0.82R
short     161  92/161    -39.37         0.87R

Regime ALL'APERTURA x direzione:
  bear_trending      long 27 · short 27
  bull_trending      long 32 · short 56
  high_uncertainty   long 21 · short 35
  sideways           long 56 · short 43

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         59 trade · PnL    -6.69
  CONTROTREND      83 trade · PnL     4.61
  regime neutro   155 trade · PnL   -78.34

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

CONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = entrati dal 27 set 19:40 UTC (fine del difetto della sessione)
                   -------- tutto --------- ‖ ------- dal 27/9 -------
                      n R medio   R tot s/R ‖    n R medio   R tot s/R
  TUTTE (netto)     258  -0.097  -24.92  39 ‖  162  -0.057   -9.16   0
    lordo           258  -0.007   -1.77  39 ‖  162  +0.037   +5.94   0
    costi stimati   258  +0.090  +23.15  39 ‖  162  +0.093  +15.10   0
 direzione
  long              120  -0.160  -19.14  16 ‖   85  -0.110   -9.35   0
  short             138  -0.042   -5.77  23 ‖   77  +0.002   +0.19   0
 regime all'apertura
  bull_trending      73  -0.156  -11.42  15 ‖   32  -0.159   -5.09   0
  bear_trending      48  +0.224  +10.77   6 ‖   37  +0.346  +12.82   0
  sideways           94  -0.139  -13.07   5 ‖   68  -0.084   -5.74   0
  high_uncertainty   43  -0.260  -11.20  13 ‖   25  -0.446  -11.14   0
 rispetto al trend
  in trend           51  +0.071   +3.62   8 ‖   36  +0.252   +9.07   0
  CONTROTREND        70  -0.061   -4.27  13 ‖   33  -0.041   -1.35   0
  regime neutro     137  -0.177  -24.27  18 ‖   93  -0.182  -16.89   0
 direzione x BTC (con = nel verso di BTC)
  long_con           65  -0.139   -9.05   0 ‖   51  -0.081   -4.16   0
  long_contro        41  -0.168   -6.88   0 ‖   34  -0.153   -5.19   0
  short_con          43  +0.039   +1.69   0 ‖   33  +0.054   +1.77   0
  short_contro       64  -0.055   -3.55   0 ‖   44  -0.036   -1.59   0
  ignoto             45  -0.158   -7.13  39 ‖    0       —       —   0
 per strategia (le prime 8 per trade)
  gen_fca11c08       14  -0.263   -3.68   0 ‖    0       —       —   0
  gen_bb762669       11  +0.043   +0.48   0 ‖    9  +0.146   +1.31   0
  gen_fa304106        5  -1.051   -5.25   4 ‖    4  -1.042   -4.17   0
  gen_cd5c842f        6  +0.412   +2.47   2 ‖    4  +0.183   +0.73   0
  gen_e59ad90b        8  +0.117   +0.94   0 ‖    7  -0.048   -0.34   0
  gen_2031005e        2  +0.719   +1.44   5 ‖    0       —       —   0
  gen_490a90e5        7  -0.031   -0.22   0 ‖    0       —       —   0
  gen_4c6df481        7  +0.114   +0.80   0 ‖    4  +0.329   +1.31   0
  altre 105         198  -0.111  -21.89  28 ‖  134  -0.060   -8.02   0
  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)

REFERTI (post_mortem) sui trade chiusi: 258 (107 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x107
  classe uscita            x54
  classe ingresso          x53
  controtrend              x28

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fa304106     9     0     9   -14.18     4/  1/   0          0        5           0
  gen_fca11c08    14     7     7   -12.40     6/  1/   0          0        7           6
  gen_ba3a671f     7     1     6   -18.88     1/  1/   0          0        2           1
  gen_6d06dca0     6     1     5   -12.81     1/  0/   0          0        1           0
  gen_2031005e     7     3     4   -24.38     0/  0/   0          0        0           0
  gen_bb762669    11     7     4     5.83     2/  2/   0          0        4           0
  gen_ceab7f6a     7     3     4    -3.09     2/  2/   0          0        4           0
  gen_4c6df481     7     4     3     2.32     1/  2/   0          0        3           0
  ultimi referti in perdita:
   - B2USDT gen_ddb3def9 long -0.95: a favore fino a 0.26R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R) · controtrend rispetto al regime all'ingresso
   - SEIUSDT gen_4f890271 short -0.82: mai andato a favore (mfe 0.15R): direzione sbagliata
   - ORCAUSDT gen_271ab7ec short -0.86: a favore fino a 0.41R ma sotto il primo gradino (1R) · il lock non si e' mai armato (serviva 0.5R) · controtrend rispetto al regime all'ingresso
   - ZORAUSDT gen_ceab7f6a long -0.97: a favore fino a 0.38R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - FLOCKUSDT gen_2350695a long -1.14: a favore fino a 0.55R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - RAYSOLUSDT gen_fa304106 long -1.25: mai andato a favore (mfe 0.15R): direzione sbagliata

PAPER CONTRO IL CASO (K4): il paper (297 trade) accanto a un prezzo CASUALE con le nostre uscite (simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md e backlog K4: costanti, non ricalcolate)
                                     paper        caso
  stop (sulle uscite)                  44%         46%
  stop ingresso/uscita (su 130)     46/53%  48.5/51.5%
  massimo toccato mediano            0.84R       0.81R
  arrivati al primo target             12%         17%
  vinti                                56%         54%
  R medio (su 258)                  -0.097      -0.067
  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma delle uscite, non una diagnosi

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte            37/65 -11.76   23/41 -10.50    27/43 +4.74    39/64 +0.84      84
  gen_bb762669        1/2 +0.89              —      2/2 +4.89      4/6 +2.68       1
  gen_fca11c08                —              —      1/4 -8.58      3/5 -3.14       5
  gen_e59ad90b                —      1/2 -3.25      2/2 +4.33      3/4 +0.51       0
  gen_4c6df481        2/3 +3.30      1/2 -0.70              —      1/2 -0.29       0
  gen_ceab7f6a        3/6 -2.12      0/1 -0.97              —              —       0
  gen_a640dfa5                —              —              —      4/6 +1.26       0
  gen_cd5c842f                —      2/3 +1.09      1/1 +4.48      1/1 +0.95       3
  gen_658b2edb        1/1 +0.17      1/1 +0.62      2/2 +1.52              —       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   9 perdite di fila  (freno spento)
  gen_bf2be656   3 perdite di fila
  gen_c5194ce4   3 perdite di fila
  gen_194e2514   2 perdite di fila
  gen_581d4a68   2 perdite di fila
  gen_771790b1   2 perdite di fila
  gen_85fadf54   2 perdite di fila
  gen_a640dfa5   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_b2f350ff   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-10-06 06:02 UTC): flat — nessun segnale valido sopra soglia
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_bf2be656: scala_stretta — 3 perdite sotto il primo gradino (mfe mediana 0.42 R) (campione 3)
  - gen_bf2be656: solo_short — long 3/3 persi (campione 3)
  - gen_c5194ce4: conferma_trend — 3 perdite mai andate a favore (classe ingresso) e 0 vinti su 3 (campione 3)
  - gen_c5194ce4: solo_long — short 3/3 persi (campione 3)
  - gen_fa304106: conferma_trend — 4 perdite mai andate a favore (classe ingresso) e 0 vinti su 9 (campione 4)
  - gen_fa304106: controtrend_btc — 3/3 persi contro il contesto BTC (campione 3)
  - gen_fa304106: solo_long — short 5/5 persi (campione 5)
  - gen_fa304106: solo_short — long 4/4 persi (campione 4)
  - gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fa304106           4/0               37.26|n/d                1.10|n/d               1.12%|n/d               44.82|n/d
  gen_fca11c08           6/7             45.68|42.58               1.92|1.05             0.86%|0.75%             72.33|72.21

KEEP PER STRATEGIA (proposta dal vissuto: >= 5 verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)
  strategia      verdetti        prematuri protetti proposta  miss medio
  gen_bb762669          5     3 (rumore 0)        2        -        0.75
  gen_e59ad90b          5     2 (rumore 1)        3     0.75        0.79
  gen_490a90e5          4     0 (rumore 0)        4        -        0.77
  gen_4c6df481          4     3 (rumore 3)        1        -        0.69
  gen_cd5c842f          4     2 (rumore 0)        2        -        0.57
  gen_fca11c08          4     1 (rumore 0)        3        -        0.83
  gen_18c839a0          3     2 (rumore 0)        1        -        0.69
  gen_2031005e          3     2 (rumore 1)        1        -        0.64
  gen_4465723e          3     2 (rumore 0)        1        -        0.63
  gen_658b2edb          3     2 (rumore 0)        1        -        0.64
  gen_8981d5f2          3     1 (rumore 1)        2        -        0.66
  gen_a640dfa5          3     3 (rumore 0)        0        -        0.70
  gen_f3661202          3     1 (rumore 1)        2        -        0.80
  gen_14e1775b          2     0 (rumore 0)        2        -        0.79
  gen_1f7ead60          2     2 (rumore 1)        0        -        0.78
  gen_2053cba6          2     0 (rumore 0)        2        -        0.75
  gen_4810faab          2     0 (rumore 0)        2        -        0.77
  gen_4f890271          2     2 (rumore 0)        0        -        0.55
  gen_771790b1          2     1 (rumore 0)        1        -        0.59
  gen_7ac562e3          2     1 (rumore 0)        1        -        0.70
  + altre 50 strategie con meno verdetti: 61 verdetti, prematuri 30, protetti 31
  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita (0 = al TP, 1 = all'entrata): misura, non regola

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 225  (vinti 135, persi 90; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.646   p media dei persi: 0.642   (se p predice, la prima e' piu' alta)
  sopra la soglia: 225/225 trade, PnL -15.31 contro -15.31 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.041
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 297 trade): verdetto piatta (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.76      99       57%     -0.36%
    0.76-0.89      99       58%     -0.22%
    0.89-1.00      99       52%     -0.52%
  FEAR & GREED all'apertura (296 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         294       55%     -0.38%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  declassate    114 trade · 65 vinti · PnL -12.02 · R medio -0.119R su 114
  attive        183 trade · 100 vinti · PnL -68.40 · R medio -0.079R su 144
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio
  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra quello per giornata e quello trade per trade; almeno 2 giornate.
  dal 27 set 19:40 UTC: declassate 114 trade R -0.119 · attive 48 trade R +0.092 · differenza -0.211R, margine ±0.353R (esclusi perche' senza R: declassate 0, attive 0) -> NON SI DECIDE

SOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. Si conta e basta, nessuna soglia cambia qui
  soglia di oggi 0.3966 · prima 0.45 · «allentata» = ultimo win rate del gate fra le due: con la soglia di prima sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)
                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio
  win rate >= 0,45                   108  ‖             85   -0.081 ‖          57   -0.074
  ALLENTATA                            7  ‖             14   +0.339 ‖           9   +0.311
  sotto la soglia di oggi              0  ‖              0        — ‖           0        —
  win rate non salvato               142  ‖            112   -0.119 ‖          93   -0.100
  trade di coppie non piu' validate       ‖             47   -0.202 ‖           3   +0.514
  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero

COSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia
  scenario                                                  PnL    diff  max dd saltati ridotti gg fermi  09-23 09-25 09-26
  com'e' andato davvero                                  -80.42   +0.00   8.35%       0       0        0  -17.66 -15.87 -14.10
  stop giornaliero 2%                                    -75.33   +5.09   7.84%      11       0        2  -17.66 -22.03 -13.82
  stop giornaliero 3%                                    -78.42   +2.00   8.15%       2       0        1  -17.66 -15.87 -14.10
  freno di serie: 4 perdite della strategia -> meta'     -79.07   +1.35   8.30%       0       8        0  -18.72 -15.87 -14.10
  freno di serie: 3 perdite della strategia -> meta'     -78.20   +2.22   8.09%       0      14        0  -16.51 -15.87 -14.23
  freno di serie: 4 perdite del bot -> meta'             -74.47   +5.95   7.53%       0      20        0  -17.66 -15.87 -14.10
  freno di serie: 3 perdite del bot -> meta'             -67.92  +12.50   6.94%       0      45        0  -14.90 -13.81 -15.37
  equity di partenza 1000; le ultime colonne sono i 3 giorni peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), non il paper

AFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui
  insieme    trade  vinti      PnL  R medio
  1-2          169     92   -39.20   -0.095
  3-5          113     62   -44.03   -0.133
  6+            15     11    +2.81   +0.161
  ondate (>= 6 aperture nello stesso verso entro 5 minuti, ora italiana):
    2026-10-02 20:47  long   10 aperture  PnL +7.92

LE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; regola in bot/learning/contributi.py, scritta prima dei numeri)
  freno globale da deriva: dimezza circa la size quando il paper rende meno del promesso
    toccati 209 a -0.079R · altri 49 a -0.173R · diff +0.094 ±0.271 -> NON SI VEDE ANCORA
    a size piena sugli stessi 108 trade: +14.28 USDT risparmiati (negativo = guadagni tolti)
    nota: in R una riduzione di size non cambia l'esito: conta in USDT
  panchina dei pesi: size ridotta alle strategia x regime che perdono nel paper
    toccati 2 a -0.304R · altri 256 a -0.095R -> CAMPIONE PICCOLO
    a size piena sugli stessi 2 trade: -0.07 USDT risparmiati (negativo = guadagni tolti)
  pesi alti (size e leva in su): peso > 0,8: piu' size e leva a chi ha vinto di recente
    toccati 54 a -0.161R · altri 22 a -0.070R · diff -0.091 ±0.519 -> NON SI VEDE ANCORA
  leva sopra 1x: trade aperti con leva > 1 (pesi e convinzione)
    toccati 63 a -0.121R · altri 195 a -0.089R · diff -0.032 ±0.264 -> NON SI VEDE ANCORA
  tilt di trend e sentiment: size ridotta ai trade contro il trend o col sentiment sfavorevole
    toccati 58 a -0.080R · altri 151 a -0.078R · diff -0.002 ±0.278 -> NON SI VEDE ANCORA
    a size piena sugli stessi 38 trade: +0.79 USDT risparmiati (negativo = guadagni tolti)
  declassate a un quarto: validate bocciate due notti di fila, operate a size ridotta
    toccati 114 a -0.119R · altri 144 a -0.079R · diff -0.040 ±0.224 -> NON SI VEDE ANCORA
    a size piena sugli stessi 99 trade: +24.73 USDT risparmiati (negativo = guadagni tolti)
    rischio effettivo medio: declassate 0.12% · attive 0.22% del capitale (K5: il quarto agisce davvero?)
  paper esplorativo: quasi-passaggi operati a un quarto: rendono come le validate?
    toccati 12 a +0.247R · altri 258 a -0.097R · diff +0.344 ±0.436 -> NON SI VEDE ANCORA
    nota: «contribuisce» qui vuol dire: i quasi-passaggi rendono piu' delle validate
  ombra AI (spenta): i trade che l'AI avrebbe evitato rendono meno di quelli che approvava?
    toccati 85 a -0.100R · altri 27 a +0.226R · diff -0.326 ±0.360 -> NON SI VEDE ANCORA
  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): ai 1 trade +0.094R · casuali 254 trade -0.091R · intorno 3 trade -0.669R
  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 36
  trade chiusi: 12 · vinti 10 · PnL +3.00
    BANKUSDT|gen_87fce2d2                1 trade · 1 vinti · +0.63
    BANKUSDT|gen_8e475cd9                1 trade · 1 vinti · +0.18
    BTRUSDT|gen_8aec28c6                 1 trade · 0 vinti · -0.99
    BTRUSDT|gen_9a383fff                 1 trade · 1 vinti · +0.45
    BULLAUSDT|gen_902fb1fd               1 trade · 1 vinti · +0.30
  coppie esplorative poi validate 4 / scartate 405  (il metro: si legge a 100 trade esplorativi)
```
