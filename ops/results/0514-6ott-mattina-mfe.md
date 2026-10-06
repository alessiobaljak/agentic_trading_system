# 0514-6ott-mattina-mfe.req

_eseguito: 2026-10-06 06:07 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 94.5s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 309 · con mfe_r registrato: 309
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 102 trade su 309 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             309     0.85    68%    40%    15%     7%     2%     2%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_bb762669                        11     0.79    73%    27%    18%     9%     9%     9%     0%
gen_fa304106                         9     0.10    33%     0%     0%     0%     0%     0%     0%
gen_cd5c842f                         8     1.17    88%    75%    38%    25%    12%    12%    12%
gen_4c6df481                         8     1.01    75%    50%    12%    12%     0%     0%     0%
gen_e59ad90b                         8     0.82    75%    12%    12%    12%     0%     0%     0%
gen_ceab7f6a                         7     0.38    43%    29%    14%     0%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_a640dfa5                         6     1.09    83%    67%    17%     0%     0%     0%     0%
gen_4465723e                         6     1.36   100%    50%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_18c839a0                         5     0.91    80%    40%    20%    20%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_c0fd1d91                         4     0.40    25%    25%    25%    25%    25%     0%     0%
gen_1f7ead60                         4     1.25    50%    50%     0%     0%     0%     0%     0%
gen_f3661202                         4     1.03    75%    50%     0%     0%     0%     0%     0%
gen_a32bee42                         4     1.11    50%    50%     0%     0%     0%     0%     0%
gen_8b91ba18                         4     1.17   100%    50%     0%     0%     0%     0%     0%
gen_fb7d035a                         4     0.84    50%     0%     0%     0%     0%     0%     0%
gen_c5194ce4                         4     0.20    25%    25%     0%     0%     0%     0%     0%
gen_771790b1                         4     1.32    75%    50%    25%     0%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%
gen_bf1e00d4                         4     0.90    75%    25%    25%    25%    25%    25%     0%
gen_902fb1fd                         3     1.10   100%    67%     0%     0%     0%     0%     0%
gen_4f890271                         3     1.09    67%    67%    33%     0%     0%     0%     0%
gen_8981d5f2                         3     0.97   100%    33%     0%     0%     0%     0%     0%
gen_fb3d971f                         3     1.49    67%    67%    33%     0%     0%     0%     0%
gen_f001d778                         3     1.07   100%    67%     0%     0%     0%     0%     0%
gen_4508a416                         3     1.09   100%    67%    33%     0%     0%     0%     0%
gen_4810faab                         3     1.13    67%    67%    33%     0%     0%     0%     0%
gen_14e1775b                         3     0.97    67%    33%     0%     0%     0%     0%     0%
gen_bf2be656                         3     0.42     0%     0%     0%     0%     0%     0%     0%
gen_d606fde3                         3     0.44    33%    33%     0%     0%     0%     0%     0%
gen_7ac562e3                         3     1.13    67%    67%     0%     0%     0%     0%     0%
gen_35632db9                         3     0.84    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (132 su 309 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  61   46%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  70   53%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.49R, massima 1.23R; con un primo gradino a 0.49R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6   0.8/1.6/2.4
------------------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             309      -0.376        -0.402        -0.762        -0.861        -0.210 *
gen_fca11c08                        14      -0.689        -0.679        -0.896        -0.886        -0.346 *
gen_bb762669                        11      -0.473        -0.482        -0.655        -0.745        -0.262 *
gen_fa304106                         9      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_cd5c842f                         8      +0.269        +0.275 *      -0.094        -0.450        +0.230  
gen_4c6df481                         8      -0.294        -0.275        -0.819        -0.800        -0.010 *
gen_e59ad90b                         8      -0.781        -0.762        -0.819        -0.800        -0.045 *
gen_ceab7f6a                         7      -0.564        -0.629        -0.793        -1.000        -0.400 *
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000        -0.400  
gen_490a90e5                         7      -0.814        -0.814        -1.000        -1.000        -0.646 *
gen_a640dfa5                         6      -0.058        -0.133        -0.758        -1.000        +0.033 *
gen_4465723e                         6      -0.275        -0.350        -0.758        -1.000        +0.113 *
gen_6d06dca0                         6      -0.200        -0.350        -0.517        -1.000        -0.173 *
gen_18c839a0                         5      -0.390        -0.360        -0.710        -0.680        +0.088 *
gen_f238d283                         5      -0.040        +0.020        -0.420        -0.360        +0.184 *
gen_c0fd1d91                         4      -0.312        -0.225 *      -0.413        -0.600        -0.330  
gen_1f7ead60                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_f3661202                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_a32bee42                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_8b91ba18                         4      -0.350        -0.350        -1.000        -1.000        -0.070 *
gen_fb7d035a                         4      -1.000        -1.000        -1.000        -1.000        -0.380 *
gen_c5194ce4                         4      -0.675 *      -0.675        -1.000        -1.000        -0.690  
gen_771790b1                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000        +0.050  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_b31d8b93                         4      -0.237        -0.200        -0.637        -0.600        +0.050 *
gen_bf1e00d4                         4      -0.312        -0.225        -0.413        -0.300        +0.290 *
gen_902fb1fd                         3      -0.133        -0.133        -1.000        -1.000        +0.240 *
gen_4f890271                         3      +0.017 *      -0.133        -0.517        -1.000        -0.013  
gen_8981d5f2                         3      -0.567        -0.567        -1.000        -1.000        -0.173 *
gen_fb3d971f                         3      +0.017 *      -0.133        -0.517        -1.000        -0.173  
gen_f001d778                         3      -0.133        -0.133        -1.000        -1.000        +0.240 *
gen_4508a416                         3      +0.017        -0.133        -0.517        -1.000        +0.240 *
gen_4810faab                         3      +0.017 *      -0.133        -0.517        -1.000        -0.013  
gen_14e1775b                         3      -0.567        -0.567        -1.000        -1.000        -0.173 *
gen_bf2be656                         3      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_d606fde3                         3      -0.567 *      -0.567        -1.000        -1.000        -0.587  
gen_7ac562e3                         3      -0.133 *      -0.133        -1.000        -1.000        -0.173  
gen_35632db9                         3      -0.567        -0.567        -1.000        -1.000        -0.173 *

    0.8/1.6/2.4 = SOLO MISURA (4 ott 2026): il gate non la prova, il bot non la opera.
(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misu

[... 3104 caratteri omessi (testa e coda conservate) ...]

 cache: 385 candele (JASMYUSDT 15m)
[backtest] dati da cache: 865 candele (SUIUSDT 15m)
[backtest] dati da cache: 1537 candele (TUTUSDT 15m)
[backtest] dati da cache: 481 candele (GALAUSDT 15m)
[backtest] dati da cache: 385 candele (AXSUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 577 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 385 candele
[backtest] dati da cache: 1249 candele (NEIROUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 577 candele

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
MITOUSDT    gen_8b91ba18            long    2.00   0.96   1.17   no    si    si 
ZORAUSDT    gen_ceab7f6a            long    1.50   1.66   0.83   no    no    no 
HUMAUSDT    gen_630b2a40            short   1.50   6.53   1.10   no    no    no 
TAUSDT      gen_543186c5            long    2.00   3.45   0.28   no    no    no 
PLUMEUSDT   gen_e94b056d            short   2.00   4.42   0.38   no    no    no 
GPSUSDT     gen_8a66a70b            short   2.00   3.36   1.00   no    no    no 
HEMIUSDT    gen_f001d778            short   2.00   2.61   0.98   no    no    no 
OPENUSDT    gen_2bb283ca            long    1.50   2.01   1.26   no    no    no 
MUBARAKUSDT gen_1f7ead60            short   2.00   6.28   1.38   no    no    no 
ENAUSDT     gen_bb762669            short   1.50   1.41   0.16   no    no    no 
MYXUSDT     gen_a5b0e4de            long    1.50   2.71   0.88   no    no    no 
PHAUSDT     gen_fa304106            short   1.50   2.63   0.02   no    no    no 
CATIUSDT    gen_b3e46005            long    1.50   5.06   2.26   si    no    si 
XPLUSDT     gen_e59ad90b            short   1.50   1.64   0.82   no    no    no 
THEUSDT     gen_a640dfa5            short   2.00   1.71   0.87   no    no    no 
RENDERUSDT  gen_1eec02f5            long    1.50   1.28   0.89   no    no    no 
USELESSUSDT gen_acea368d            short   2.00   0.76   1.44   no    si    si 
HUMAUSDT    gen_a32bee42            short   2.00   8.70   0.39   no    no    no 
MUBARAKUSDT gen_e933160c            short   1.50   1.17   0.17   no    no    no 
BANKUSDT    gen_fb3d971f            short   2.00   3.67   1.49   no    no    no 
UBUSDT      gen_f3661202            long    2.00   1.72   1.03   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   1.79   0.03   no    no    no 
HEMIUSDT    gen_4c6df481            long    1.50   0.73   0.88   no    si    si 
MUBARAKUSDT gen_1f7ead60            short   2.00   5.75   1.25   no    no    no 
BTRUSDT     gen_8981d5f2            short   1.50   1.78   0.97   no    no    no 
ENAUSDT     gen_bb762669            short   1.50   1.84   0.00   no    no    no 
THEUSDT     gen_a640dfa5            short   2.00   1.07   0.49   no    no    no 
PROMUSDT    gen_cd5c842f            short   2.00   1.70   1.90   no    si    si 
USELESSUSDT gen_c0fd1d91            short   1.50   1.27   3.44   si    si    si 
B2USDT      gen_ddb3def9            long    2.00   4.83   0.26   no    no    no 
SKYAIUSDT   gen_98837ec2            short   2.00   3.43   1.30   no    no    no 
PTBUSDT     gen_684d7623            short   1.00   3.03   0.53   no    no    no 
SEIUSDT     gen_4f890271            short   2.00   1.63   0.15   no    no    no 
ORCAUSDT    gen_271ab7ec            short   1.00   3.77   0.41   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   2.91   0.38   no    no    no 
SKYAIUSDT   gen_6cf80ae6            short   2.00   2.49   1.12   no    no    no 
FLOCKUSDT   gen_2350695a            long    2.00   0.90   0.55   no    no    no 
RAYSOLUSDT  gen_fa304106            long    2.00   1.76   0.15   no    no    no 
FORMUSDT    gen_c647ead7            long    0.75   6.96   0.51   no    no    no 
PLUMEUSDT   gen_902fb1fd            long    1.50   3.47   0.88   no    no    no 
(mostrati i 40 piu' recenti su 301)

  trade misurati: 301 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 2.99R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  31   10%
  raggiunto il livello strutturale ........  24    8%
  raggiunto il piu' vicino dei due ........  47   16%
  Lettura: il livello strutturale sta in mediana a 2.99R (primo gradino mediano 1.50R) e viene raggiunto nel 8% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 16% dei casi; il livello e' piu' vicino del TP1 in 69 trade su 301.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  HEIUSDT LONG (gen_9a383fff, 15m): stop 1.1% · TP1 2R = 2.1% · TP2 4R = 4.3% · TP3 6R = 6.4%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.6%
    TP prima dello stop: TP1   33% · TP2   20% · TP3   14%
    TP comunque entro l'orizzonte: TP1   72% · TP2   52% · TP3   39%

  PTBUSDT LONG (gen_684d7623, 15m): stop 2.3% · TP1 1R = 2.3% · TP2 1.5R = 3.4% · TP3 2.5R = 5.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 5.1%
    TP prima dello stop: TP1   51% · TP2   42% · TP3   28%
    TP comunque entro l'orizzonte: TP1   74% · TP2   65% · TP3   45%

  ZORAUSDT SHORT (gen_2c248ee9, 15m): stop 0.8% · TP1 1.5R = 1.2% · TP2 3R = 2.4% · TP3 5R = 4.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.9%
    TP prima dello stop: TP1   40% · TP2   24% · TP3   13%
    TP comunque entro l'orizzonte: TP1   81% · TP2   59% · TP3   34%

  Nel paper (trade chiusi): almeno 1 gradino   11% · almeno 2    2% · tutti e 3    1%
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

  trade chiusi letti: 309 · a 15m: 309 (esplorativi: 12) · altri timeframe, fuori dalla curva: 0
  misurati: 273 su 19 giornate (esplorativi fra i misurati: 11) · saltati: 36 (nessun ingresso a caso utilizzabile: 1, nessuna candela chiusa subito prima dell'ingresso: 10, orizzonte oltre i dati (o buco nella serie): 25)
  ingressi a caso per segnale: mediana 20, minimo 9
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    273    -0.018  -0.002    -0.016  [-0.141, +0.133]  |        -0.14  -0.02  -0.12  [-0.48, +0.27]
  4 ore    273    +0.000  -0.019    +0.019  [-0.116, +0.165]  |        -0.06  -0.08  +0.02  [-0.46, +0.47]
  12 ore   273    -0.005  -0.065    +0.060  [-0.138, +0.254]  |        -0.19  -0.19  +0.01  [-0.65, +0.62]
  24 ore   273    -0.241  -0.209    -0.033  [-0.271, +0.204]  |        -0.84  -0.65  -0.20  [-1.02, +0.56]

  Per verso (solo informativo, non decide):
  long (131 trade, 18 giornate): 1 ora -0.046 [-0.138, +0.033] · 4 ore -0.012 [-0.120, +0.062] · 12 ore -0.010 [-0.226, +0.144] · 24 ore -0.116 [-0.568, +0.190]
  short (142 trade, 18 giornate): 1 ora +0.012 [-0.215, +0.314] · 4 ore +0.049 [-0.191, +0.342] · 12 ore +0.124 [-0.157, +0.469] · 24 ore +0.045 [-0.293, +0.375]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 273 trade su 19 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 75.1s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
