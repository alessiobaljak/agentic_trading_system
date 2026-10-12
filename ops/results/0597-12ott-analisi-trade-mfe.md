# 0597-12ott-analisi-trade-mfe.req

_eseguito: 2026-10-12 16:54 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 139.5s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 506 · con mfe_r registrato: 506
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 159 trade su 506 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             506     0.81    66%    38%    15%     8%     3%     2%     0%
gen_ceab7f6a                        15     0.76    53%    33%    13%     0%     0%     0%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_fa304106                        12     0.30    42%     8%     0%     0%     0%     0%     0%
gen_4c6df481                        11     0.88    73%    45%    18%     9%     0%     0%     0%
gen_bb762669                        11     0.79    73%    27%    18%     9%     9%     9%     0%
gen_cd5c842f                        10     1.17    80%    70%    30%    20%    10%    10%    10%
gen_e59ad90b                        10     0.82    60%    10%    10%    10%     0%     0%     0%
gen_4465723e                         9     1.29    89%    56%    11%     0%     0%     0%     0%
gen_18c839a0                         8     0.90    50%    25%    12%    12%     0%     0%     0%
gen_8b91ba18                         7     0.85   100%    43%    14%     0%     0%     0%     0%
gen_c5194ce4                         7     0.24    29%    14%     0%     0%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_96c1ed1b                         6     0.80    50%    33%    17%    17%    17%     0%     0%
gen_9a383fff                         6     1.14    67%    50%     0%     0%     0%     0%     0%
gen_bf1e00d4                         6     0.90    83%    33%    33%    33%    17%    17%     0%
gen_c647ead7                         6     0.74    83%    17%     0%     0%     0%     0%     0%
gen_a640dfa5                         6     1.09    83%    67%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_684d7623                         5     0.53    80%     0%     0%     0%     0%     0%     0%
gen_4810faab                         5     1.13    80%    80%    40%    20%    20%     0%     0%
gen_1eec02f5                         5     1.00   100%    40%    20%    20%     0%     0%     0%
gen_902fb1fd                         5     1.10    80%    60%     0%     0%     0%     0%     0%
gen_658b2edb                         5     1.30   100%    80%    40%     0%     0%     0%     0%
gen_f3661202                         5     0.77    60%    40%     0%     0%     0%     0%     0%
gen_725cb5f4                         5     0.47    20%     0%     0%     0%     0%     0%     0%
gen_b2f350ff                         5     0.94    80%    40%    20%    20%    20%    20%    20%
gen_771790b1                         5     1.27    80%    60%    20%     0%     0%     0%     0%
gen_fb7d035a                         5     0.84    60%    20%    20%    20%    20%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_e09c5203                         4     1.05    50%    50%    25%    25%     0%     0%     0%
gen_5a52c06b                         4     1.07    75%    50%    25%     0%     0%     0%     0%
gen_7ac562e3                         4     1.13    75%    50%     0%     0%     0%     0%     0%
gen_b9c251a1                         4     0.53    50%    25%    25%    25%     0%     0%     0%
gen_4508a416                         4     1.45   100%    75%    25%     0%     0%     0%     0%
gen_8c9b332f                         4     0.82   100%    25%     0%     0%     0%     0%     0%
gen_fb3d971f                         4     1.57    75%    75%    50%     0%     0%     0%     0%
gen_14e1775b                         4     0.97    50%    25%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (221 su 506 trade):
  sbagliati dall'inizio (mfe < 0.25R) .......... 101   46%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino ....... 119   54%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    0%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.49R, massima 1.23R; con un primo gradino a 0.49R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6   0.8/1.6/2.4
------------------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             506      -0.398        -0.418        -0.749        -0.849        -0.265 *
gen_ceab7f6a                        15      -0.507        -0.567        -0.807        -1.000        -0.440 *
gen_fca11c08                        14      -0.689        -0.679        -0.896        -0.886        -0.346 *
gen_fa304106                        12      -0.892 *      -0.892        -1.000        -1.000        -0.897  
gen_4c6df481                        11      -0.327        -0.355        -0.736        -0.855        -0.124 *
gen_bb762669                        11      -0.473        -0.482        -0.655        -0.745        -0.262 *
gen_cd5c842f                        10      +0.145        +0.150 *      -0.275        -0.560        +0.108  
gen_e59ad90b                        10      -0.825        -0.810        -0.855        -0.840        -0.236 *
gen_4465723e                         9      -0.228        -0.278        -0.839        -1.000        +0.018 *
gen_18c839a0                         8      -0.619        -0.600        -0.819        -0.800        -0.320 *
gen_8b91ba18                         7      -0.379        -0.443        -0.793        -1.000        -0.223 *
gen_c5194ce4                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000        -0.400  
gen_490a90e5                         7      -0.814        -0.814        -1.000        -1.000        -0.646 *
gen_96c1ed1b                         6      -0.325        -0.267        -0.608        -0.733        -0.140 *
gen_9a383fff                         6      -0.350        -0.350        -1.000        -1.000        -0.173 *
gen_bf1e00d4                         6      -0.250        -0.167        -0.367        -0.267        +0.147 *
gen_c647ead7                         6      -0.783 *      -0.783        -1.000        -1.000        -0.793  
gen_a640dfa5                         6      -0.058        -0.133        -0.758        -1.000        +0.033 *
gen_6d06dca0                         6      -0.200        -0.350        -0.517        -1.000        -0.173 *
gen_684d7623                         5      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_4810faab                         5      +0.420 *      +0.400        -0.240        -0.680        +0.376  
gen_1eec02f5                         5      -0.390        -0.360        -0.710        -0.680        +0.088 *
gen_902fb1fd                         5      -0.220        -0.220        -1.000        -1.000        -0.008 *
gen_658b2edb                         5      +0.220 *      +0.040        -0.420        -1.000        +0.088  
gen_f3661202                         5      -0.480 *      -0.480        -1.000        -1.000        -0.504  
gen_725cb5f4                         5      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_b2f350ff                         5      -0.190        -0.120        -0.130        -0.440        +0.032 *
gen_771790b1                         5      -0.130 *      -0.220        -0.710        -1.000        -0.160  
gen_fb7d035a                         5      -0.450        -0.380        -0.530        -0.680        +0.032 *
gen_f238d283                         5      -0.040        +0.020        -0.420        -0.360        +0.184 *
gen_e09c5203                         4      -0.237        -0.200        -0.637        -0.600        -0.020 *
gen_5a52c06b                         4      -0.237 *      -0.350        -0.637        -1.000        -0.380  
gen_7ac562e3                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_b9c251a1                         4      -0.562        -0.525 *      -0.637        -0.600        -0.570  
gen_4508a416                         4      +0.087        -0.025        -0.637        -1.000        +0.240 *
gen_8c9b332f                         4      -0.675        -0.675        -1.000        -1.000        -0.380 *
gen_fb3d971f                         4      +0.200 *      -0.025        -0.275        -1.000        +0.050  
gen_14e1775b                         4      -0.675        -0.675        -1.000        -1.000        -0.380 *

    0.8/1.6/2.4 = SOLO MISURA (4 ott 2026): il gate non la prova, il bot non la opera.
(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misu

[... 4935 caratteri omessi (testa e coda conservate) ...]

65 candele
[backtest] dati da cache: 481 candele (TRUMPUSDT 15m)
[backtest] dati da cache: 577 candele (XMRUSDT 15m)
[backtest] dati da cache: 385 candele (SOLUSDT 15m)
[backtest] dati da cache: 481 candele (XRPUSDT 15m)
[backtest] dati da cache: 385 candele (ATOMUSDT 15m)
[backtest] dati da binance: 1249 candele
[backtest] dati da cache: 481 candele (JTOUSDT 15m)
[backtest] dati da cache: 577 candele (BICOUSDT 15m)

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
GRASSUSDT   gen_f4ac85e0            short   2.00   3.25   0.78   no    no    no 
MUBARAKUSDT gen_ff3e4154            long    1.50   2.04   0.00   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   1.83   0.76   no    no    no 
SYRUPUSDT   gen_4c6df481            short   2.00   2.20   0.79   no    no    no 
PLUMEUSDT   gen_353f3f19            short   2.00   4.74   0.49   no    no    no 
SAHARAUSDT  gen_9839aec0            short   1.50   1.70   0.16   no    no    no 
QUSDT       gen_18c839a0            long    1.50   7.66   0.08   no    no    no 
AKTUSDT     gen_f4c1300a            short   1.00   2.98   0.27   no    no    no 
ARKMUSDT    gen_913d0c3a            short   1.50   4.14   0.00   no    no    no 
SKYAIUSDT   gen_bd109329            short   1.50   1.72   0.16   no    no    no 
ZECUSDT     gen_1623b4cb            short   1.50   2.58   0.07   no    no    no 
AVAAIUSDT   gen_1eec02f5            short   1.50   1.48   2.33   si    si    si 
BRUSDT      gen_95fb50ce            long    2.00   6.36   0.39   no    no    no 
FLOCKUSDT   gen_33de4c13            short   1.50   4.82   2.99   si    no    si 
XPINUSDT    gen_6bc43e03            short   2.00   1.22   1.99   no    si    si 
SAHARAUSDT  gen_cb8176f2            short   1.50   4.79   1.75   si    no    si 
HUMAUSDT    gen_da39a23a            short   1.00   5.96   0.06   no    no    no 
ARKMUSDT    gen_913d0c3a            short   1.50   5.89   0.92   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   2.54   1.80   si    no    si 
IDUSDT      gen_fa304106            long    1.50   1.69   1.43   no    no    no 
RAYSOLUSDT  gen_a01bcc1a            long    1.50   2.09   1.07   no    no    no 
RENDERUSDT  gen_fdaa6e0b            long    1.50   1.18   0.79   no    no    no 
SAHARAUSDT  gen_66848d49            short   2.00   3.95   0.19   no    no    no 
BULLAUSDT   gen_5a52c06b            long    1.50  20.76   1.57   si    no    si 
QUSDT       gen_f1e7ff62            short   1.00   1.68   0.11   no    no    no 
PNUTUSDT    gen_4810faab            short   2.00   4.03   1.02   no    no    no 
HEMIUSDT    gen_c1f71d65            long    1.50   1.93   0.92   no    no    no 
HEMIUSDT    gen_acea368d            short   1.50   2.84   0.98   no    no    no 
PUMPUSDT    gen_1000366e            short   1.50   3.79   0.84   no    no    no 
AINUSDT     gen_d926b0fd            long    1.50   2.07   0.18   no    no    no 
ASTERUSDT   gen_96efce1b            short   2.00   3.34   3.52   si    si    si 
IDOLUSDT    gen_5ad54558            short   1.50   4.23   1.19   no    no    no 
HYPEUSDT    gen_f19b67e8            long    1.00   0.91   0.36   no    no    no 
UBUSDT      gen_08664b28            long    1.50   3.67   0.63   no    no    no 
TAUSDT      gen_01fbe76f            long    1.50   6.80   0.80   no    no    no 
USELESSUSDT gen_e09c5203            long    2.00   4.88   0.12   no    no    no 
UBUSDT      gen_f3e1ade7            long    2.00   5.92   0.00   no    no    no 
BANKUSDT    gen_7100bb59            long    0.75   0.78   0.21   no    no    no 
USELESSUSDT gen_e09c5203            long    2.00   5.63   0.14   no    no    no 
PTBUSDT     gen_684d7623            long    1.00   3.73   0.76   no    no    no 
(mostrati i 40 piu' recenti su 498)

  trade misurati: 498 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.29R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  56   11%
  raggiunto il livello strutturale ........  42    8%
  raggiunto il piu' vicino dei due ........  78   16%
  Lettura: il livello strutturale sta in mediana a 3.29R (primo gradino mediano 1.50R) e viene raggiunto nel 8% dei trade contro il 11% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 16% dei casi; il livello e' piu' vicino del TP1 in 92 trade su 498.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  DEXEUSDT SHORT (gen_3d4be8c7, 1h): stop 1.2% · TP1 1.5R = 1.8% · TP2 3R = 3.6% · TP3 5R = 5.9%
    su 2160 ingressi casuali: massimo a favore mediano in 96 candele 9.0%
    TP prima dello stop: TP1   38% · TP2   28% · TP3   20%
    TP comunque entro l'orizzonte: TP1   87% · TP2   78% · TP3   65%

  IDOLUSDT LONG (gen_5ad54558, 15m): stop 0.8% · TP1 1.5R = 1.3% (preso) · TP2 3R = 2.5% · TP3 5R = 4.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.6%
    TP prima dello stop: TP1   39% · TP2   22% · TP3   12%
    TP comunque entro l'orizzonte: TP1   74% · TP2   51% · TP3   32%

  RENDERUSDT LONG (gen_8b9bfc7d, 15m): stop 3.8% · TP1 1.5R = 5.7% · TP2 3R = 11.3% · TP3 5R = 18.9%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.1%
    TP prima dello stop: TP1   16% · TP2    2% · TP3    0%
    TP comunque entro l'orizzonte: TP1   17% · TP2    2% · TP3    0%

  UBUSDT LONG (gen_4348f9d4, 15m): stop 3.2% · TP1 1.5R = 4.8% · TP2 3R = 9.6% · TP3 5R = 16.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 5.2%
    TP prima dello stop: TP1   37% · TP2   19% · TP3    8%
    TP comunque entro l'orizzonte: TP1   53% · TP2   28% · TP3   12%

  Nel paper (trade chiusi): almeno 1 gradino   11% · almeno 2    3% · tutti e 3    1%
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

  trade chiusi letti: 506 · a 15m: 504 (esplorativi: 25) · altri timeframe, fuori dalla curva: 2 (1h: 2)
  misurati: 448 su 25 giornate (esplorativi fra i misurati: 20) · saltati: 56 (nessuna candela chiusa subito prima dell'ingresso: 30, orizzonte oltre i dati (o buco nella serie): 26)
  ingressi a caso per segnale: mediana 20, minimo 5
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    448    +0.005  -0.002    +0.008  [-0.075, +0.103]  |        -0.02  -0.02  -0.01  [-0.25, +0.25]
  4 ore    448    +0.039  -0.027    +0.066  [-0.031, +0.164]  |        +0.06  -0.09  +0.15  [-0.16, +0.44]
  12 ore   448    +0.029  -0.090    +0.119  [-0.022, +0.240]  |        -0.03  -0.26  +0.23  [-0.25, +0.65]
  24 ore   448    -0.187  -0.214    +0.028  [-0.136, +0.165]  |        -0.65  -0.65  +0.01  [-0.55, +0.47]

  Per verso (solo informativo, non decide):
  long (242 trade, 24 giornate): 1 ora -0.015 [-0.074, +0.036] · 4 ore +0.064 [-0.017, +0.136] · 12 ore +0.108 [-0.064, +0.261] · 24 ore +0.009 [-0.258, +0.178]
  short (206 trade, 24 giornate): 1 ora +0.034 [-0.128, +0.227] · 4 ore +0.068 [-0.100, +0.266] · 12 ore +0.132 [-0.095, +0.385] · 24 ore +0.050 [-0.198, +0.281]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 448 trade su 25 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 108.0s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
