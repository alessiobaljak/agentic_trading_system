# 0574-10ott-mattina-mfe.req

_eseguito: 2026-10-10 03:49 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 102.0s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 440 · con mfe_r registrato: 440
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 128 trade su 440 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             440     0.81    66%    38%    15%     8%     3%     2%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_ceab7f6a                        11     0.37    36%    18%     9%     0%     0%     0%     0%
gen_fa304106                        11     0.15    36%     0%     0%     0%     0%     0%     0%
gen_bb762669                        11     0.79    73%    27%    18%     9%     9%     9%     0%
gen_cd5c842f                        10     1.17    80%    70%    30%    20%    10%    10%    10%
gen_e59ad90b                        10     0.82    60%    10%    10%    10%     0%     0%     0%
gen_4465723e                         9     1.29    89%    56%    11%     0%     0%     0%     0%
gen_4c6df481                         9     0.88    67%    44%    11%    11%     0%     0%     0%
gen_c5194ce4                         7     0.24    29%    14%     0%     0%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_96c1ed1b                         6     0.80    50%    33%    17%    17%    17%     0%     0%
gen_18c839a0                         6     0.91    67%    33%    17%    17%     0%     0%     0%
gen_9a383fff                         6     1.14    67%    50%     0%     0%     0%     0%     0%
gen_8b91ba18                         6     1.17   100%    50%    17%     0%     0%     0%     0%
gen_bf1e00d4                         6     0.90    83%    33%    33%    33%    17%    17%     0%
gen_c647ead7                         6     0.74    83%    17%     0%     0%     0%     0%     0%
gen_a640dfa5                         6     1.09    83%    67%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_658b2edb                         5     1.30   100%    80%    40%     0%     0%     0%     0%
gen_f3661202                         5     0.77    60%    40%     0%     0%     0%     0%     0%
gen_725cb5f4                         5     0.47    20%     0%     0%     0%     0%     0%     0%
gen_b2f350ff                         5     0.94    80%    40%    20%    20%    20%    20%    20%
gen_771790b1                         5     1.27    80%    60%    20%     0%     0%     0%     0%
gen_fb7d035a                         5     0.84    60%    20%    20%    20%    20%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_1eec02f5                         4     1.00   100%    25%     0%     0%     0%     0%     0%
gen_b9c251a1                         4     0.53    50%    25%    25%    25%     0%     0%     0%
gen_4508a416                         4     1.45   100%    75%    25%     0%     0%     0%     0%
gen_8c9b332f                         4     0.82   100%    25%     0%     0%     0%     0%     0%
gen_fb3d971f                         4     1.57    75%    75%    50%     0%     0%     0%     0%
gen_4810faab                         4     1.62    75%    75%    50%    25%    25%     0%     0%
gen_902fb1fd                         4     1.10    75%    50%     0%     0%     0%     0%     0%
gen_14e1775b                         4     0.97    50%    25%     0%     0%     0%     0%     0%
gen_dfb554f7                         4     1.28   100%    75%    25%     0%     0%     0%     0%
gen_f001d778                         4     1.07    75%    50%     0%     0%     0%     0%     0%
gen_684d7623                         4     0.53    75%     0%     0%     0%     0%     0%     0%
gen_4f890271                         4     1.09    50%    50%    25%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (191 su 440 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  85   45%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino ....... 105   55%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.49R, massima 1.23R; con un primo gradino a 0.49R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6   0.8/1.6/2.4
------------------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             440      -0.397        -0.413        -0.751        -0.845        -0.260 *
gen_fca11c08                        14      -0.689        -0.679        -0.896        -0.886        -0.346 *
gen_ceab7f6a                        11      -0.723        -0.764        -0.868        -1.000        -0.618 *
gen_fa304106                        11      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_bb762669                        11      -0.473        -0.482        -0.655        -0.745        -0.262 *
gen_cd5c842f                        10      +0.145        +0.150 *      -0.275        -0.560        +0.108  
gen_e59ad90b                        10      -0.825        -0.810        -0.855        -0.840        -0.236 *
gen_4465723e                         9      -0.228        -0.278        -0.839        -1.000        +0.018 *
gen_4c6df481                         9      -0.372        -0.356        -0.839        -0.822        -0.120 *
gen_c5194ce4                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000        -0.400  
gen_490a90e5                         7      -0.814        -0.814        -1.000        -1.000        -0.646 *
gen_96c1ed1b                         6      -0.325        -0.267        -0.608        -0.733        -0.140 *
gen_18c839a0                         6      -0.492        -0.467        -0.758        -0.733        -0.093 *
gen_9a383fff                         6      -0.350        -0.350        -1.000        -1.000        -0.173 *
gen_8b91ba18                         6      -0.275        -0.350        -0.758        -1.000        -0.093 *
gen_bf1e00d4                         6      -0.250        -0.167        -0.367        -0.267        +0.147 *
gen_c647ead7                         6      -0.783 *      -0.783        -1.000        -1.000        -0.793  
gen_a640dfa5                         6      -0.058        -0.133        -0.758        -1.000        +0.033 *
gen_6d06dca0                         6      -0.200        -0.350        -0.517        -1.000        -0.173 *
gen_658b2edb                         5      +0.220 *      +0.040        -0.420        -1.000        +0.088  
gen_f3661202                         5      -0.480 *      -0.480        -1.000        -1.000        -0.504  
gen_725cb5f4                         5      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_b2f350ff                         5      -0.190        -0.120        -0.130        -0.440        +0.032 *
gen_771790b1                         5      -0.130 *      -0.220        -0.710        -1.000        -0.160  
gen_fb7d035a                         5      -0.450        -0.380        -0.530        -0.680        +0.032 *
gen_f238d283                         5      -0.040        +0.020        -0.420        -0.360        +0.184 *
gen_1eec02f5                         4      -0.675        -0.675        -1.000        -1.000        -0.070 *
gen_b9c251a1                         4      -0.562        -0.525 *      -0.637        -0.600        -0.570  
gen_4508a416                         4      +0.087        -0.025        -0.637        -1.000        +0.240 *
gen_8c9b332f                         4      -0.675        -0.675        -1.000        -1.000        -0.380 *
gen_fb3d971f                         4      +0.200 *      -0.025        -0.275        -1.000        +0.050  
gen_4810faab                         4      +0.450 *      +0.425        -0.050        -0.600        +0.410  
gen_902fb1fd                         4      -0.350        -0.350        -1.000        -1.000        -0.070 *
gen_14e1775b                         4      -0.675        -0.675        -1.000        -1.000        -0.380 *
gen_dfb554f7                         4      +0.087        -0.025        -0.637        -1.000        +0.360 *
gen_f001d778                         4      -0.350        -0.350        -1.000        -1.000        -0.070 *
gen_684d7623                         4      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_4f890271                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  

    0.8/1.6/2.4 = SOLO MISURA (4 ott 2026): il gate non la prova, il bot non la opera.
(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misu

[... 4428 caratteri omessi (testa e coda conservate) ...]

acktest] dati da cache: 865 candele (TSTUSDT 15m)
[backtest] dati da cache: 481 candele (GALAUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 577 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 385 candele
[backtest] dati da cache: 1249 candele (NEIROUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 577 candele

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
VETUSDT     gen_b9c251a1            long    1.00   3.27   2.00   si    no    si 
XPINUSDT    gen_902fb1fd            long    0.75   2.42   0.40   no    no    no 
ASTERUSDT   gen_d74845a5            long    1.50   4.01   0.68   no    no    no 
TUTUSDT     gen_4465723e            short   1.50   0.58   1.29   no    si    si 
DEXEUSDT    gen_b9c251a1            long    1.00   3.79   0.53   no    no    no 
UBUSDT      gen_5b847426            long    1.50   4.52   1.37   no    no    no 
CROSSUSDT   gen_4e6e1ae0            long    2.00   2.94   0.33   no    no    no 
QUSDT       gen_18c839a0            short   1.50   2.85   0.24   no    no    no 
SPXUSDT     gen_725cb5f4            long    0.75   3.81   0.47   no    no    no 
HUSDT       gen_22b2cade            long    1.50   3.94   1.32   no    no    no 
SOPHUSDT    gen_42acf37e            long    1.50   3.14   2.25   si    no    si 
ORCAUSDT    gen_fb3d971f            long    1.50   6.64   1.88   si    no    si 
SUIUSDT     gen_8c9b332f            long    1.00   4.29   0.58   no    no    no 
ZORAUSDT    gen_ceab7f6a            short   1.50   1.25   0.11   no    no    no 
BULLAUSDT   gen_5a52c06b            long    1.50   6.55   1.07   no    no    no 
FLOCKUSDT   gen_c5194ce4            short   0.75   1.77   0.24   no    no    no 
SUPERUSDT   gen_0eb999b7            short   1.50   1.46   0.65   no    no    no 
AIOUSDT     gen_fc644cd2            short   1.00   2.60   0.59   no    no    no 
OPENUSDT    gen_46f0717f            short   2.00   1.51   0.86   no    no    no 
XPINUSDT    gen_2e0818c8            short   0.75   5.16   0.00   no    no    no 
CATIUSDT    gen_b3e46005            long    1.50   3.82   4.25   si    si    si 
PUMPUSDT    gen_13cc61f2            long    1.50   3.92   1.27   no    no    no 
1000PEPEUSD gen_f9d90376            long    2.00   5.71   1.01   no    no    no 
HEMIUSDT    gen_acea368d            short   1.50   2.12   0.00   no    no    no 
0GUSDT      gen_aa6bb820            long    1.50   6.18   2.26   si    no    si 
QUSDT       gen_1f224994            short   1.50   3.12   0.80   no    no    no 
CVCUSDT     gen_8c9b332f            long    2.00   6.05   1.16   no    no    no 
HEMIUSDT    gen_f695fd53            long    2.00   9.47   0.70   no    no    no 
OPENUSDT    gen_f3661202            long    1.50   6.75   0.30   no    no    no 
AIOUSDT     gen_581d4a68            long    2.00   3.01   1.50   no    no    no 
1000BONKUSD gen_86a8b183            long    1.50   2.84   1.52   si    no    si 
STEEMUSDT   gen_4508a416            long    2.00   1.39   1.45   no    si    si 
THEUSDT     gen_658b2edb            long    2.00   4.50   1.51   no    no    no 
HUSDT       gen_22b2cade            long    1.50   6.80   0.45   no    no    no 
FORMUSDT    gen_1eec02f5            short   1.50   5.16   1.00   no    no    no 
HEMIUSDT    gen_c1f71d65            short   1.50   3.33   0.94   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   3.25   0.77   no    no    no 
PUNDIXUSDT  gen_96c1ed1b            short   2.00   3.67   0.00   no    no    no 
CATIUSDT    gen_b3e46005            long    1.50   5.67   0.04   no    no    no 
XPINUSDT    gen_f311acf9            short   1.00   4.13   0.95   no    no    no 
(mostrati i 40 piu' recenti su 432)

  trade misurati: 432 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.33R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  47   11%
  raggiunto il livello strutturale ........  36    8%
  raggiunto il piu' vicino dei due ........  67   16%
  Lettura: il livello strutturale sta in mediana a 3.33R (primo gradino mediano 1.50R) e viene raggiunto nel 8% dei trade contro il 11% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 16% dei casi; il livello e' piu' vicino del TP1 in 83 trade su 432.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  ASTERUSDT SHORT (gen_b0e86c70, 15m): stop 0.6% · TP1 1.5R = 1.0% · TP2 3R = 1.9% · TP3 5R = 3.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 1.4%
    TP prima dello stop: TP1   35% · TP2   16% · TP3    9%
    TP comunque entro l'orizzonte: TP1   61% · TP2   38% · TP3   23%

  AVAAIUSDT SHORT (gen_8b91ba18, 15m): stop 2.0% · TP1 1.5R = 3.0% · TP2 3R = 5.9% · TP3 5R = 9.9%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.5%
    TP prima dello stop: TP1   32% · TP2   12% · TP3    6%
    TP comunque entro l'orizzonte: TP1   57% · TP2   27% · TP3   15%

  BULLAUSDT SHORT (gen_7ac562e3, 15m): stop 1.7% · TP1 1.5R = 2.6% · TP2 3R = 5.2% · TP3 5R = 8.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.3%
    TP prima dello stop: TP1   37% · TP2   17% · TP3    8%
    TP comunque entro l'orizzonte: TP1   69% · TP2   42% · TP3   25%

  UBUSDT LONG (gen_0d7be682, 15m): stop 1.4% · TP1 2R = 2.9% · TP2 4R = 5.8% · TP3 6R = 8.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 5.3%
    TP prima dello stop: TP1   36% · TP2   20% · TP3   14%
    TP comunque entro l'orizzonte: TP1   70% · TP2   47% · TP3   33%

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

  trade chiusi letti: 440 · a 15m: 440 (esplorativi: 18) · altri timeframe, fuori dalla curva: 0
  misurati: 381 su 24 giornate (esplorativi fra i misurati: 15) · saltati: 59 (nessuna candela chiusa subito prima dell'ingresso: 14, orizzonte oltre i dati (o buco nella serie): 45)
  ingressi a caso per segnale: mediana 20, minimo 1
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    381    -0.006  -0.003    -0.003  [-0.092, +0.101]  |        -0.07  -0.02  -0.05  [-0.32, +0.23]
  4 ore    381    +0.016  -0.033    +0.049  [-0.055, +0.157]  |        -0.01  -0.11  +0.11  [-0.24, +0.43]
  12 ore   381    +0.003  -0.094    +0.097  [-0.059, +0.229]  |        -0.13  -0.29  +0.15  [-0.37, +0.61]
  24 ore   381    -0.235  -0.233    -0.001  [-0.187, +0.158]  |        -0.82  -0.73  -0.10  [-0.72, +0.44]

  Per verso (solo informativo, non decide):
  long (197 trade, 23 giornate): 1 ora -0.029 [-0.096, +0.035] · 4 ore +0.040 [-0.052, +0.121] · 12 ore +0.056 [-0.135, +0.233] · 24 ore -0.026 [-0.342, +0.180]
  short (184 trade, 21 giornate): 1 ora +0.026 [-0.152, +0.251] · 4 ore +0.058 [-0.135, +0.289] · 12 ore +0.140 [-0.105, +0.442] · 24 ore +0.025 [-0.233, +0.293]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 381 trade su 24 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 81.8s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
