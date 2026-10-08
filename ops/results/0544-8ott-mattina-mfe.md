# 0544-8ott-mattina-mfe.req

_eseguito: 2026-10-08 03:49 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 95.0s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 377 · con mfe_r registrato: 377
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 110 trade su 377 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             377     0.82    66%    38%    14%     7%     3%     2%     1%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_bb762669                        11     0.79    73%    27%    18%     9%     9%     9%     0%
gen_cd5c842f                        10     1.17    80%    70%    30%    20%    10%    10%    10%
gen_e59ad90b                        10     0.82    60%    10%    10%    10%     0%     0%     0%
gen_fa304106                        10     0.15    40%     0%     0%     0%     0%     0%     0%
gen_ceab7f6a                         8     0.38    38%    25%    12%     0%     0%     0%     0%
gen_4465723e                         8     1.36    88%    50%    12%     0%     0%     0%     0%
gen_4c6df481                         8     1.01    75%    50%    12%    12%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_c5194ce4                         6     0.43    33%    17%     0%     0%     0%     0%     0%
gen_bf1e00d4                         6     0.90    83%    33%    33%    33%    17%    17%     0%
gen_c647ead7                         6     0.74    83%    17%     0%     0%     0%     0%     0%
gen_a640dfa5                         6     1.09    83%    67%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_9a383fff                         5     1.14    80%    60%     0%     0%     0%     0%     0%
gen_96c1ed1b                         5     0.80    60%    40%    20%    20%    20%     0%     0%
gen_fb7d035a                         5     0.84    60%    20%    20%    20%    20%     0%     0%
gen_8b91ba18                         5     0.85   100%    40%     0%     0%     0%     0%     0%
gen_18c839a0                         5     0.91    80%    40%    20%    20%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_dfb554f7                         4     1.28   100%    75%    25%     0%     0%     0%     0%
gen_b2f350ff                         4     0.94    75%    25%    25%    25%    25%    25%    25%
gen_f001d778                         4     1.07    75%    50%     0%     0%     0%     0%     0%
gen_684d7623                         4     0.53    75%     0%     0%     0%     0%     0%     0%
gen_725cb5f4                         4     0.47    25%     0%     0%     0%     0%     0%     0%
gen_4f890271                         4     1.09    50%    50%    25%     0%     0%     0%     0%
gen_c0fd1d91                         4     0.40    25%    25%    25%    25%    25%     0%     0%
gen_1f7ead60                         4     1.25    50%    50%     0%     0%     0%     0%     0%
gen_f3661202                         4     1.03    75%    50%     0%     0%     0%     0%     0%
gen_a32bee42                         4     1.11    50%    50%     0%     0%     0%     0%     0%
gen_771790b1                         4     1.32    75%    50%    25%     0%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%
gen_1eec02f5                         3     0.89   100%    33%     0%     0%     0%     0%     0%
gen_93131ef1                         3     1.88   100%   100%    67%    33%     0%     0%     0%
gen_98837ec2                         3     0.13    33%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (167 su 377 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  75   45%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  91   54%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.49R, massima 1.23R; con un primo gradino a 0.49R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6   0.8/1.6/2.4
------------------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             377      -0.408        -0.427        -0.763        -0.859        -0.261 *
gen_fca11c08                        14      -0.689        -0.679        -0.896        -0.886        -0.346 *
gen_bb762669                        11      -0.473        -0.482        -0.655        -0.745        -0.262 *
gen_cd5c842f                        10      +0.145        +0.150 *      -0.275        -0.560        +0.108  
gen_e59ad90b                        10      -0.825        -0.810        -0.855        -0.840        -0.236 *
gen_fa304106                        10      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_ceab7f6a                         8      -0.619        -0.675        -0.819        -1.000        -0.475 *
gen_4465723e                         8      -0.294        -0.350        -0.819        -1.000        -0.010 *
gen_4c6df481                         8      -0.294        -0.275        -0.819        -0.800        -0.010 *
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000        -0.400  
gen_490a90e5                         7      -0.814        -0.814        -1.000        -1.000        -0.646 *
gen_c5194ce4                         6      -0.783 *      -0.783        -1.000        -1.000        -0.793  
gen_bf1e00d4                         6      -0.250        -0.167        -0.367        -0.267        +0.147 *
gen_c647ead7                         6      -0.783 *      -0.783        -1.000        -1.000        -0.793  
gen_a640dfa5                         6      -0.058        -0.133        -0.758        -1.000        +0.033 *
gen_6d06dca0                         6      -0.200        -0.350        -0.517        -1.000        -0.173 *
gen_9a383fff                         5      -0.220        -0.220        -1.000        -1.000        -0.008 *
gen_96c1ed1b                         5      -0.190        -0.120        -0.530        -0.680        +0.032 *
gen_fb7d035a                         5      -0.450        -0.380        -0.530        -0.680        +0.032 *
gen_8b91ba18                         5      -0.480        -0.480        -1.000        -1.000        -0.256 *
gen_18c839a0                         5      -0.390        -0.360        -0.710        -0.680        +0.088 *
gen_f238d283                         5      -0.040        +0.020        -0.420        -0.360        +0.184 *
gen_dfb554f7                         4      +0.087        -0.025        -0.637        -1.000        +0.360 *
gen_b2f350ff                         4      -0.312        -0.225        +0.087 *      -0.300        -0.020  
gen_f001d778                         4      -0.350        -0.350        -1.000        -1.000        -0.070 *
gen_684d7623                         4      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_725cb5f4                         4      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_4f890271                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_c0fd1d91                         4      -0.312        -0.225 *      -0.413        -0.600        -0.330  
gen_1f7ead60                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_f3661202                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_a32bee42                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_771790b1                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000        +0.050  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_b31d8b93                         4      -0.237        -0.200        -0.637        -0.600        +0.050 *
gen_1eec02f5                         3      -0.567        -0.567        -1.000        -1.000        -0.173 *
gen_93131ef1                         3      +0.600 *      +0.500        -0.033        -0.467        +0.560  
gen_98837ec2                         3      -0.567 *      -0.567        -1.000        -1.000        -0.587  

    0.8/1.6/2.4 = SOLO MISURA (4 ott 2026): il gate non la prova, il bot non la opera.
(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misu

[... 5505 caratteri omessi (testa e coda conservate) ...]

.79   no    no    no 
SPXUSDT     gen_725cb5f4            long    0.75   5.90   0.47   no    no    no 
GPSUSDT     gen_ec2b5fda            long    2.00   3.47   1.07   no    no    no 
XPINUSDT    gen_c60cc1b9            long    2.00   3.62   0.97   no    no    no 
BMTUSDT     gen_571cdda2            long    1.50   3.65   0.55   no    no    no 
VETUSDT     gen_b9c251a1            long    1.00   3.98   0.39   no    no    no 
HEIUSDT     gen_9a383fff            long    2.00   2.50   1.20   no    no    no 
PROMUSDT    gen_cd5c842f            short   2.00   2.22   0.46   no    no    no 
DOTUSDT     gen_60c9259a            long    2.00   5.25   0.72   no    no    no 
PUNDIXUSDT  gen_96c1ed1b            long    2.00   5.52   0.42   no    no    no 
PTBUSDT     gen_684d7623            long    1.00   5.24   0.53   no    no    no 
BULLAUSDT   gen_5a52c06b            long    1.50  20.17   0.52   no    no    no 
SYRUPUSDT   gen_f3b97917            long    2.00   3.72   1.16   no    no    no 
SAHARAUSDT  gen_1eec02f5            short   2.00   1.29   1.01   no    no    no 
MITOUSDT    gen_08387bbe            long    1.50   5.66   0.51   no    no    no 
CVCUSDT     gen_7b4a474b            long    2.00   6.49   0.76   no    no    no 
TAUSDT      gen_01fbe76f            long    1.50   4.20   0.00   no    no    no 
XPINUSDT    gen_9a383fff            long    2.00   4.94   0.45   no    no    no 
SYRUPUSDT   gen_f6c63753            long    1.50   8.66   0.58   no    no    no 
FORMUSDT    gen_1eec02f5            long    1.50   3.55   0.57   no    no    no 
ARCUSDT     gen_96c1ed1b            long    2.00   6.46   0.14   no    no    no 
GPSUSDT     gen_bf1e00d4            long    1.50   5.13   0.76   no    no    no 
TAUSDT      gen_c647ead7            short   2.00   7.82   0.74   no    no    no 
SPXUSDT     gen_d03ff6d4            long    1.50   6.12   0.20   no    no    no 
HEMIUSDT    gen_71f018a9            long    1.50   1.46   4.94   si    si    si 
AIOUSDT     gen_fc644cd2            short   1.00   3.78   0.55   no    no    no 
EPICUSDT    gen_dfb554f7            long    1.50   5.14   1.69   si    no    si 
FLOCKUSDT   gen_c5194ce4            short   0.75   1.53   0.54   no    no    no 
PROMUSDT    gen_cd5c842f            short   2.00   4.61   1.23   no    no    no 
UBUSDT      gen_2a2898b0            short   2.00   2.48   0.04   no    no    no 
FLOCKUSDT   gen_c5194ce4            long    0.75   7.81   0.43   no    no    no 
AXSUSDT     gen_b922252e            long    1.50   2.45   0.01   no    no    no 
(mostrati i 40 piu' recenti su 368)

  trade misurati: 368 · saltati: 9 (livello assente (prezzo gia' oltre tutto, o nessuna candela prima): 1, senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.25R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  37   10%
  raggiunto il livello strutturale ........  29    8%
  raggiunto il piu' vicino dei due ........  53   14%
  Lettura: il livello strutturale sta in mediana a 3.25R (primo gradino mediano 1.50R) e viene raggiunto nel 8% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 14% dei casi; il livello e' piu' vicino del TP1 in 74 trade su 368.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  AINUSDT LONG (gen_ef115241, 15m): stop 4.5% · TP1 2R = 9.1% · TP2 4R = 18.1% · TP3 6R = 27.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.8%
    TP prima dello stop: TP1   15% · TP2    5% · TP3    3%
    TP comunque entro l'orizzonte: TP1   19% · TP2    8% · TP3    5%

  B2USDT LONG (gen_ddb3def9, 15m): stop 1.3% · TP1 2R = 2.7% (preso) · TP2 4R = 5.3% · TP3 6R = 8.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.3%
    TP prima dello stop: TP1   33% · TP2   16% · TP3    8%
    TP comunque entro l'orizzonte: TP1   59% · TP2   28% · TP3   16%

  DEXEUSDT LONG (gen_fa304106, 15m): stop 0.9% · TP1 1.5R = 1.4% · TP2 3R = 2.7% · TP3 5R = 4.5%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.1%
    TP prima dello stop: TP1   37% · TP2   22% · TP3   13%
    TP comunque entro l'orizzonte: TP1   75% · TP2   54% · TP3   36%

  IDUSDT SHORT (gen_6bc43e03, 15m): stop 1.6% · TP1 2R = 3.2% · TP2 4R = 6.4% · TP3 6R = 9.6%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.4%
    TP prima dello stop: TP1   26% · TP2    6% · TP3    1%
    TP comunque entro l'orizzonte: TP1   38% · TP2    9% · TP3    1%

  MITOUSDT SHORT (gen_8b91ba18, 15m): stop 1.6% · TP1 2R = 3.2% · TP2 4R = 6.3% · TP3 6R = 9.5%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.1%
    TP prima dello stop: TP1   28% · TP2   11% · TP3    5%
    TP comunque entro l'orizzonte: TP1   49% · TP2   21% · TP3   10%

  PUMPUSDT LONG (gen_13cc61f2, 15m): stop 2.8% · TP1 1.5R = 4.2% · TP2 3R = 8.4% · TP3 5R = 14.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 5.4%
    TP prima dello stop: TP1   43% · TP2   26% · TP3    9%
    TP comunque entro l'orizzonte: TP1   59% · TP2   32% · TP3   13%

  STXUSDT SHORT (gen_a5b0e4de, 15m): stop 2.3% · TP1 2R = 4.6% · TP2 4R = 9.1% · TP3 6R = 13.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.3%
    TP prima dello stop: TP1   18% · TP2    4% · TP3    1%
    TP comunque entro l'orizzonte: TP1   22% · TP2    4% · TP3    1%

  ZORAUSDT LONG (gen_ceab7f6a, 15m): stop 1.3% · TP1 1.5R = 2.0% · TP2 3R = 4.0% · TP3 5R = 6.6%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.0%
    TP prima dello stop: TP1   38% · TP2   21% · TP3   11%
    TP comunque entro l'orizzonte: TP1   65% · TP2   41% · TP3   21%

  Nel paper (trade chiusi): almeno 1 gradino   10% · almeno 2    3% · tutti e 3    1%
  Lettura: ingresso casuale, non il segnale; se la strategia ha un vantaggio vero le sue quote sono piu' alte. Misura, nessuna regola cambia (le uscite non si toccano prima delle letture del 7-14 ott).

==============================================================================
LA CURVA DEL VANTAGGIO DEL SEGNALE (T2)
==============================================================================
Regola (diario, 2 ott 2026, scritta PRIMA dei numeri): per ogni trade vero del paper, la mossa
del prezzo dopo 1, 4, 12 e 24 ore dall'ingresso, col segno della direzione, in «mosse tipiche
di 24 ore» della moneta (calcolate sui 30 giorni PRIMA dell'ingresso). Confronto: ingressi a
caso sulla stessa moneta negli stessi giorni, stessa direzione. Vantaggio = media dei segnali -
media del caso; margine al 95% ricampionando le giornate. Tutte le durate dentro il margine ->
«nessun vantaggio misurabile» (il lavoro sui TP si ferma, il problema e' l'ingresso o il gate:
R1); qualcuna sopra -> «c'è un vantaggio» (il TP va dove la curva smette di salire, poi T1 dopo
le letture del 7-14 ott); sotto -> «i segnali fanno peggio del caso», detto per primo.

  trade chiusi letti: 377 · a 15m: 377 (esplorativi: 15) · altri timeframe, fuori dalla curva: 0
  misurati: 303 su 21 giornate (esplorativi fra i misurati: 12) · saltati: 74 (nessun ingresso a caso utilizzabile: 1, nessuna candela chiusa subito prima dell'ingresso: 48, orizzonte oltre i dati (o buco nella serie): 25)
  ingressi a caso per segnale: mediana 20, minimo 1
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    303    -0.013  -0.002    -0.011  [-0.120, +0.126]  |        -0.12  -0.02  -0.10  [-0.41, +0.25]
  4 ore    303    +0.004  -0.018    +0.022  [-0.105, +0.155]  |        -0.06  -0.08  +0.02  [-0.41, +0.41]
  12 ore   303    +0.015  -0.054    +0.069  [-0.121, +0.239]  |        -0.12  -0.16  +0.03  [-0.58, +0.59]
  24 ore   303    -0.225  -0.192    -0.034  [-0.245, +0.160]  |        -0.80  -0.57  -0.23  [-0.94, +0.40]

  Per verso (solo informativo, non decide):
  long (139 trade, 20 giornate): 1 ora -0.041 [-0.132, +0.030] · 4 ore +0.006 [-0.101, +0.089] · 12 ore +0.022 [-0.215, +0.181] · 24 ore -0.107 [-0.577, +0.182]
  short (164 trade, 20 giornate): 1 ora +0.015 [-0.185, +0.287] · 4 ore +0.036 [-0.177, +0.301] · 12 ore +0.108 [-0.154, +0.412] · 24 ore +0.028 [-0.287, +0.335]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 303 trade su 21 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 69.2s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
