# 0291-controllo-27set-trades.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `trades`
**eseguito:** `.venv/bin/python -m scripts.trade_stats`
**esito:** codice 0 in 3.8s

```
[firebase] connesso (Firestore + RTDB)

Trade totali analizzati: 110  (110 con apertura nota)
Giorni coperti:          12
Trade/giorno:            min 1 · media 9.2 · max 30
  per giorno (UTC): 2026-09-16 1 · 2026-09-17 2 · 2026-09-18 6 · 2026-09-19 4 · 2026-09-20 6 · 2026-09-21 16 · 2026-09-22 2 · 2026-09-23 5 · 2026-09-24 11 · 2026-09-25 30 · 2026-09-26 21 · 2026-09-27 6
Durata media holding:    4.0h  (min 0.0h · max 24.0h)
Posizioni contemporanee: MAX 9 · media nel tempo 1.7
Coin distinte:           36
Strategie distinte:      49

Lettura: se MAX contemporanee << 10 (il tetto da margine), il numero di
trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.

DIREZIONE — long vs short
        trade   vinti       PnL   mfe mediana
long       44   20/44    -22.40         0.84R
short      66   33/66    -51.00         0.82R

Regime ALL'APERTURA x direzione:
  bear_trending      long 10 · short 5
  bull_trending      long 14 · short 33
  high_uncertainty   long 8 · short 21
  sideways           long 12 · short 7

Rispetto al trend (stesso criterio dell'orchestratore):
  in trend         19 trade · PnL   -23.69
  CONTROTREND      43 trade · PnL    -9.94
  regime neutro    48 trade · PnL   -39.76

Lettura: il controtrend NON e' un errore — il trend modula la size, non
mette il veto, e le strategie di ritorno alla media vendono la forza per
costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.

REFERTI (post_mortem) sui trade chiusi: 71 (32 in perdita; esclusi gli esiti manual/kill_switch/circuit_breaker)
  lock mai armato          x32
  classe uscita            x16
  classe ingresso          x16
  controtrend              x14

  PER STRATEGIA (trade in perdita con referto):
  strategia        n vinti persi      PnL  ingr/usc/prot stop largo lock mai controtrend
  gen_fca11c08    10     4     6   -13.25     6/  0/   0          0        6           5
  gen_ba3a671f     6     1     5   -17.27     1/  0/   0          0        1           1
  gen_fa304106     5     0     5    -9.91     0/  1/   0          0        1           0
  gen_2031005e     6     2     4   -28.14     0/  0/   0          0        0           0
  gen_6d06dca0     5     1     4   -11.38     0/  0/   0          0        0           0
  gen_1f7ead60     2     0     2   -10.66     1/  0/   0          0        1           0
  gen_acfd527a     2     0     2    -3.33     1/  1/   0          0        2           0
  gen_af734c68     3     1     2    -2.31     0/  0/   0          0        0           0
  ultimi referti in perdita:
   - DOTUSDT gen_fca11c08 short -1.95: mai andato a favore (mfe 0.04R): direzione sbagliata · controtrend rispetto al regime all'ingresso
   - TAUSDT gen_bf2be656 long -1.67: a favore fino a 0.33R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)
   - MITOUSDT gen_8b91ba18 long -1.12: a favore fino a 0.85R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - CROSSUSDT gen_d606fde3 long -1.78: a favore fino a 0.29R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - VETUSDT gen_b2f350ff long -1.58: a favore fino a 0.72R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
   - AVAAIUSDT gen_e50a9211 long -0.95: a favore fino a 0.45R ma sotto il primo gradino (1.5R) · il lock non si e' mai armato (serviva 0.75R)

DIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; «con» = nel verso di BTC, «contro» = opposto)
                       long_con    long_contro      short_con   short_contro  ignoti
  tutte               4/7 -0.49      3/7 -3.13      5/9 -3.55      2/3 -2.50      84
  gen_fca11c08                —              —      1/4 -8.58      0/1 -3.99       5
  gen_8b91ba18        1/2 -0.70              —              —              —       0
  gen_14e1775b        1/1 +0.84              —              —              —       0
  gen_4465723e        1/1 +1.88              —              —              —       3
  gen_4c6df481                —      1/1 +2.54              —              —       0
  gen_4f890271                —              —      1/1 +1.04              —       0
  gen_658b2edb                —              —      1/1 +0.57              —       0
  gen_887d87df        1/1 +0.22              —              —              —       0
  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= 3 perdite contro il contesto e 0 vinti contro, per strategia)

SERIE DI PERDITE in corso per strategia (freno spento: STREAK_BRAKE_ENABLED=false, solo misura; soglia 4 di fila):
  gen_fa304106   5 perdite di fila  (freno spento)
  gen_1f7ead60   2 perdite di fila
  gen_acfd527a   2 perdite di fila
  gen_bf2be656   2 perdite di fila

RIFIUTI D'INGRESSO
  ultimo esito (RTDB /decision_status, solo l'ultimo, 2026-09-27 06:02 UTC): decided — parita' backtest: 1 segnali validi aperti
  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, righe [rifiuto] (ops: `log-bot`)

IPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, non il paper):
  - gen_fa304106: solo_long — short 4/4 persi (campione 4)
  - gen_fca11c08: conferma_trend — 5 perdite controtrend (campione 5)
  - gen_fca11c08: ingresso_atr_pct — 5 perdite d'ingresso su 6 con volatilita' alta (ATR > 0.78% del prezzo) (mediana 0.88%), vinti mediana 0.72% (campione 6)

CONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con >= 4 perdite d'ingresso):
  strategia      persi/vinti         adx persi|vinti   vol_ratio persi|vinti     atr_pct persi|vinti         rsi persi|vinti
  gen_fca11c08           6/4             45.68|26.28               1.92|2.08             0.86%|0.72%             72.33|71.76

SELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)
  trade con p: 38  (vinti 23, persi 15; ne servono 40 per leggere la calibrazione)
  p media dei vinti: 0.654   p media dei persi: 0.627   (se p predice, la prima e' piu' alta)
  sopra la soglia: 38/38 trade, PnL -8.28 contro -8.28 di tutti (a size uguale: e' cio' che il selettore avrebbe tenuto)
  correlazione p/esito: +0.211
  regola: il selettore entra solo se batte «apri tutto» su 2/3 finestre (report `selettore`) E la calibrazione sul paper non e' piatta (>= 40 trade con p, p media dei vinti > dei persi, correlazione p/esito > 0)

CALIBRAZIONE (regime, F&G) — misure, non toccano la size
  confidenza del REGIME (terzili, 110 trade): verdetto cresce (< 10 per fascia = campione insufficiente)
    fascia          n  win rate  pnl medio
    0.32-0.79      36       44%     -1.26%
    0.80-0.91      36       53%     -0.27%
    0.92-1.00      38       47%     -0.94%
  FEAR & GREED all'apertura (110 trade)
    fascia          n  win rate  pnl medio
    <=25            0         —          —
    26-74         108       48%     -0.86%
    >=75            2       50%     +1.10%

DECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE
  nessun trade chiuso da una declassata (il gate non ne ha ancora scritte, o il bot non le ha ancora operate)
  declassate      0 trade · 0 vinti · PnL +0.00 · R medio n/d
  attive        110 trade · 53 vinti · PnL -73.39 · R medio -0.170R su 71
  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio

PAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai numeri qui sopra e dai pesi)
  coppie attive adesso: 55
  trade chiusi: 1 · vinti 0 · PnL -0.39
    XRPUSDT|gen_50905b4a                 1 trade · 0 vinti · -0.39
  coppie esplorative poi validate 1 / scartate 64  (il metro: si legge a 100 trade esplorativi)
```
