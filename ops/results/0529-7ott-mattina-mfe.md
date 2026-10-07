# 0529-7ott-mattina-mfe.req

_eseguito: 2026-10-07 06:07 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 131.7s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 345 · con mfe_r registrato: 345
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 96 trade su 345 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             345     0.82    66%    39%    14%     8%     3%     1%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_bb762669                        11     0.79    73%    27%    18%     9%     9%     9%     0%
gen_e59ad90b                        10     0.82    60%    10%    10%    10%     0%     0%     0%
gen_fa304106                        10     0.15    40%     0%     0%     0%     0%     0%     0%
gen_cd5c842f                         9     1.10    78%    67%    33%    22%    11%    11%    11%
gen_ceab7f6a                         8     0.38    38%    25%    12%     0%     0%     0%     0%
gen_4465723e                         8     1.36    88%    50%    12%     0%     0%     0%     0%
gen_4c6df481                         8     1.01    75%    50%    12%    12%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_a640dfa5                         6     1.09    83%    67%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_c647ead7                         5     0.54    80%    20%     0%     0%     0%     0%     0%
gen_fb7d035a                         5     0.84    60%    20%    20%    20%    20%     0%     0%
gen_8b91ba18                         5     0.85   100%    40%     0%     0%     0%     0%     0%
gen_bf1e00d4                         5     0.90    80%    40%    40%    40%    20%    20%     0%
gen_18c839a0                         5     0.91    80%    40%    20%    20%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_684d7623                         4     0.53    75%     0%     0%     0%     0%     0%     0%
gen_725cb5f4                         4     0.47    25%     0%     0%     0%     0%     0%     0%
gen_4f890271                         4     1.09    50%    50%    25%     0%     0%     0%     0%
gen_c0fd1d91                         4     0.40    25%    25%    25%    25%    25%     0%     0%
gen_1f7ead60                         4     1.25    50%    50%     0%     0%     0%     0%     0%
gen_f3661202                         4     1.03    75%    50%     0%     0%     0%     0%     0%
gen_a32bee42                         4     1.11    50%    50%     0%     0%     0%     0%     0%
gen_c5194ce4                         4     0.20    25%    25%     0%     0%     0%     0%     0%
gen_771790b1                         4     1.32    75%    50%    25%     0%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%
gen_96c1ed1b                         3     1.35   100%    67%    33%    33%    33%     0%     0%
gen_dfb554f7                         3     1.21   100%    67%     0%     0%     0%     0%     0%
gen_93131ef1                         3     1.88   100%   100%    67%    33%     0%     0%     0%
gen_9a383fff                         3     1.14   100%    67%     0%     0%     0%     0%     0%
gen_98837ec2                         3     0.13    33%    33%     0%     0%     0%     0%     0%
gen_2c248ee9                         3     1.32   100%    67%    33%     0%     0%     0%     0%
gen_902fb1fd                         3     1.10   100%    67%     0%     0%     0%     0%     0%
gen_8981d5f2                         3     0.97   100%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (150 su 345 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  70   47%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  79   53%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.49R, massima 1.23R; con un primo gradino a 0.49R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6   0.8/1.6/2.4
------------------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             345      -0.396        -0.419        -0.765        -0.862        -0.242 *
gen_fca11c08                        14      -0.689        -0.679        -0.896        -0.886        -0.346 *
gen_bb762669                        11      -0.473        -0.482        -0.655        -0.745        -0.262 *
gen_e59ad90b                        10      -0.825        -0.810        -0.855        -0.840        -0.236 *
gen_fa304106                        10      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_cd5c842f                         9      +0.128        +0.133 *      -0.194        -0.511        +0.093  
gen_ceab7f6a                         8      -0.619        -0.675        -0.819        -1.000        -0.475 *
gen_4465723e                         8      -0.294        -0.350        -0.819        -1.000        -0.010 *
gen_4c6df481                         8      -0.294        -0.275        -0.819        -0.800        -0.010 *
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000        -0.400  
gen_490a90e5                         7      -0.814        -0.814        -1.000        -1.000        -0.646 *
gen_a640dfa5                         6      -0.058        -0.133        -0.758        -1.000        +0.033 *
gen_6d06dca0                         6      -0.200        -0.350        -0.517        -1.000        -0.173 *
gen_c647ead7                         5      -0.740 *      -0.740        -1.000        -1.000        -0.752  
gen_fb7d035a                         5      -0.450        -0.380        -0.530        -0.680        +0.032 *
gen_8b91ba18                         5      -0.480        -0.480        -1.000        -1.000        -0.256 *
gen_bf1e00d4                         5      -0.100        +0.000        -0.240        -0.120        +0.376 *
gen_18c839a0                         5      -0.390        -0.360        -0.710        -0.680        +0.088 *
gen_f238d283                         5      -0.040        +0.020        -0.420        -0.360        +0.184 *
gen_684d7623                         4      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_725cb5f4                         4      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_4f890271                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_c0fd1d91                         4      -0.312        -0.225 *      -0.413        -0.600        -0.330  
gen_1f7ead60                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_f3661202                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_a32bee42                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_c5194ce4                         4      -0.675 *      -0.675        -1.000        -1.000        -0.690  
gen_771790b1                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000        +0.050  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_b31d8b93                         4      -0.237        -0.200        -0.637        -0.600        +0.050 *
gen_96c1ed1b                         3      +0.350        +0.467        -0.217        -0.467        +0.720 *
gen_dfb554f7                         3      -0.133        -0.133        -1.000        -1.000        +0.240 *
gen_93131ef1                         3      +0.600 *      +0.500        -0.033        -0.467        +0.560  
gen_9a383fff                         3      -0.133        -0.133        -1.000        -1.000        +0.240 *
gen_98837ec2                         3      -0.567 *      -0.567        -1.000        -1.000        -0.587  
gen_2c248ee9                         3      +0.017        -0.133        -0.517        -1.000        +0.400 *
gen_902fb1fd                         3      -0.133        -0.133        -1.000        -1.000        +0.240 *
gen_8981d5f2                         3      -0.567        -0.567        -1.000        -1.000        -0.173 *

    0.8/1.6/2.4 = SOLO MISURA (4 ott 2026): il gate non la prova, il bot non la opera.
(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misur

[... 6769 caratteri omessi (testa e coda conservate) ...]

   1.50   3.93   0.15   no    no    no 
PTBUSDT     gen_684d7623            long    1.00   4.08   0.00   no    no    no 
FORMUSDT    gen_c647ead7            long    0.75   9.06   0.54   no    no    no 
KERNELUSDT  gen_c647ead7            long    2.00   8.92   1.04   no    no    no 
DOTUSDT     gen_60c9259a            long    2.00   6.77   0.00   no    no    no 
JUPUSDT     gen_938d15dc            long    1.50   4.51   0.33   no    no    no 
CVCUSDT     gen_4c4dac5f            long    2.00   4.28   0.30   no    no    no 
SUIUSDT     gen_8c9b332f            long    1.00   4.57   0.63   no    no    no 
FORMUSDT    gen_c647ead7            long    0.75   4.16   0.41   no    no    no 
KERNELUSDT  gen_c647ead7            long    2.00   6.38   0.75   no    no    no 
SPXUSDT     gen_725cb5f4            long    0.75   5.90   0.47   no    no    no 
BMTUSDT     gen_571cdda2            long    1.50   3.65   0.55   no    no    no 
PROMUSDT    gen_cd5c842f            short   2.00   2.22   0.46   no    no    no 
PTBUSDT     gen_684d7623            long    1.00   5.24   0.53   no    no    no 
(mostrati i 40 piu' recenti su 337)

  trade misurati: 337 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.14R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  34   10%
  raggiunto il livello strutturale ........  27    8%
  raggiunto il piu' vicino dei due ........  50   15%
  Lettura: il livello strutturale sta in mediana a 3.14R (primo gradino mediano 1.50R) e viene raggiunto nel 8% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 15% dei casi; il livello e' piu' vicino del TP1 in 72 trade su 337.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  ASTERUSDT LONG (gen_96efce1b, 15m): stop 1.9% · TP1 2R = 3.8% · TP2 4R = 7.6% · TP3 6R = 11.4%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 1.3%
    TP prima dello stop: TP1   14% · TP2    5% · TP3    2%
    TP comunque entro l'orizzonte: TP1   17% · TP2    6% · TP3    3%

  BULLAUSDT LONG (gen_5a52c06b, 15m): stop 1.3% · TP1 1.5R = 2.0% · TP2 3R = 4.0% · TP3 5R = 6.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 6.7%
    TP prima dello stop: TP1   39% · TP2   28% · TP3   19%
    TP comunque entro l'orizzonte: TP1   81% · TP2   66% · TP3   50%

  DOTUSDT LONG (gen_60c9259a, 15m): stop 2.2% · TP1 2R = 4.3% · TP2 4R = 8.7% · TP3 6R = 13.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.1%
    TP prima dello stop: TP1   24% · TP2    7% · TP3    3%
    TP comunque entro l'orizzonte: TP1   27% · TP2    7% · TP3    3%

  GPSUSDT LONG (gen_ec2b5fda, 15m): stop 1.5% · TP1 2R = 3.0% · TP2 4R = 6.1% · TP3 6R = 9.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.6%
    TP prima dello stop: TP1   35% · TP2   15% · TP3    7%
    TP comunque entro l'orizzonte: TP1   58% · TP2   26% · TP3   13%

  HEIUSDT LONG (gen_9a383fff, 15m): stop 1.9% · TP1 2R = 3.8% · TP2 4R = 7.5% · TP3 6R = 11.3%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.6%
    TP prima dello stop: TP1   33% · TP2   19% · TP3   13%
    TP comunque entro l'orizzonte: TP1   56% · TP2   34% · TP3   24%

  HEMIUSDT SHORT (gen_f001d778, 15m): stop 3.3% · TP1 2R = 6.6% · TP2 4R = 13.2% · TP3 6R = 19.9%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.4%
    TP prima dello stop: TP1   20% · TP2    5% · TP3    2%
    TP comunque entro l'orizzonte: TP1   32% · TP2   11% · TP3    7%

  JASMYUSDT LONG (gen_b2f350ff, 15m): stop 2.8% · TP1 2R = 5.6% · TP2 4R = 11.3% · TP3 6R = 16.9%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.6%
    TP prima dello stop: TP1   20% · TP2    5% · TP3    2%
    TP comunque entro l'orizzonte: TP1   23% · TP2    5% · TP3    2%

  PUNDIXUSDT LONG (gen_96c1ed1b, 15m): stop 1.3% · TP1 2R = 2.6% · TP2 4R = 5.2% · TP3 6R = 7.8%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.2%
    TP prima dello stop: TP1   30% · TP2   14% · TP3    7%
    TP comunque entro l'orizzonte: TP1   43% · TP2   21% · TP3   12%

  RSRUSDT SHORT (gen_b2f350ff, 15m): stop 2.1% · TP1 2R = 4.1% (preso) · TP2 4R = 8.3% (preso) · TP3 6R = 12.4%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.4%
    TP prima dello stop: TP1   14% · TP2    1% · TP3    0%
    TP comunque entro l'orizzonte: TP1   19% · TP2    2% · TP3    1%

  SCRUSDT LONG (gen_bd8f158b, 15m): stop 3.2% · TP1 2R = 6.3% · TP2 4R = 12.7% · TP3 6R = 19.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.7%
    TP prima dello stop: TP1   25% · TP2    9% · TP3    3%
    TP comunque entro l'orizzonte: TP1   27% · TP2    9% · TP3    4%

  SYRUPUSDT LONG (gen_f3b97917, 15m): stop 1.8% · TP1 2R = 3.5% · TP2 4R = 7.1% · TP3 6R = 10.6%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.0%
    TP prima dello stop: TP1   32% · TP2   15% · TP3    6%
    TP comunque entro l'orizzonte: TP1   44% · TP2   20% · TP3    8%

  VETUSDT LONG (gen_b9c251a1, 15m): stop 1.8% · TP1 1R = 1.8% · TP2 1.5R = 2.7% · TP3 2.5R = 4.6%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.3%
    TP prima dello stop: TP1   47% · TP2   35% · TP3   21%
    TP comunque entro l'orizzonte: TP1   58% · TP2   44% · TP3   27%

  XPINUSDT LONG (gen_c60cc1b9, 15m): stop 1.9% · TP1 2R = 3.7% · TP2 4R = 7.5% · TP3 6R = 11.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.7%
    TP prima dello stop: TP1   29% · TP2   12% · TP3    5%
    TP comunque entro l'orizzonte: TP1   49% · TP2   21% · TP3   10%

  Nel paper (trade chiusi): almeno 1 gradino   10% · almeno 2    2% · tutti e 3    1%
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

  trade chiusi letti: 345 · a 15m: 345 (esplorativi: 13) · altri timeframe, fuori dalla curva: 0
  misurati: 293 su 20 giornate (esplorativi fra i misurati: 11) · saltati: 52 (nessun ingresso a caso utilizzabile: 1, nessuna candela chiusa subito prima dell'ingresso: 29, orizzonte oltre i dati (o buco nella serie): 22)
  ingressi a caso per segnale: mediana 20, minimo 7
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    293    -0.017  -0.001    -0.016  [-0.128, +0.117]  |        -0.13  -0.01  -0.11  [-0.44, +0.23]
  4 ore    293    +0.003  -0.016    +0.020  [-0.108, +0.152]  |        -0.05  -0.07  +0.02  [-0.43, +0.43]
  12 ore   293    +0.006  -0.056    +0.062  [-0.128, +0.239]  |        -0.14  -0.17  +0.02  [-0.62, +0.60]
  24 ore   293    -0.238  -0.195    -0.043  [-0.268, +0.171]  |        -0.84  -0.59  -0.24  [-1.01, +0.45]

  Per verso (solo informativo, non decide):
  long (136 trade, 19 giornate): 1 ora -0.046 [-0.134, +0.030] · 4 ore +0.001 [-0.105, +0.081] · 12 ore +0.010 [-0.206, +0.175] · 24 ore -0.096 [-0.544, +0.201]
  short (157 trade, 19 giornate): 1 ora +0.010 [-0.190, +0.274] · 4 ore +0.036 [-0.183, +0.279] · 12 ore +0.106 [-0.165, +0.430] · 24 ore +0.003 [-0.313, +0.297]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 293 trade su 20 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 86.7s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
