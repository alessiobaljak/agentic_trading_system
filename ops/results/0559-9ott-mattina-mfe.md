# 0559-9ott-mattina-mfe.req

_eseguito: 2026-10-09 03:49 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 110.0s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 417 · con mfe_r registrato: 417
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 125 trade su 417 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             417     0.81    66%    38%    14%     8%     3%     2%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_fa304106                        11     0.15    36%     0%     0%     0%     0%     0%     0%
gen_bb762669                        11     0.79    73%    27%    18%     9%     9%     9%     0%
gen_cd5c842f                        10     1.17    80%    70%    30%    20%    10%    10%    10%
gen_e59ad90b                        10     0.82    60%    10%    10%    10%     0%     0%     0%
gen_4465723e                         9     1.29    89%    56%    11%     0%     0%     0%     0%
gen_4c6df481                         9     0.88    67%    44%    11%    11%     0%     0%     0%
gen_ceab7f6a                         9     0.37    33%    22%    11%     0%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_18c839a0                         6     0.91    67%    33%    17%    17%     0%     0%     0%
gen_9a383fff                         6     1.14    67%    50%     0%     0%     0%     0%     0%
gen_8b91ba18                         6     1.17   100%    50%    17%     0%     0%     0%     0%
gen_c5194ce4                         6     0.43    33%    17%     0%     0%     0%     0%     0%
gen_bf1e00d4                         6     0.90    83%    33%    33%    33%    17%    17%     0%
gen_c647ead7                         6     0.74    83%    17%     0%     0%     0%     0%     0%
gen_a640dfa5                         6     1.09    83%    67%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_725cb5f4                         5     0.47    20%     0%     0%     0%     0%     0%     0%
gen_b2f350ff                         5     0.94    80%    40%    20%    20%    20%    20%    20%
gen_771790b1                         5     1.27    80%    60%    20%     0%     0%     0%     0%
gen_96c1ed1b                         5     0.80    60%    40%    20%    20%    20%     0%     0%
gen_fb7d035a                         5     0.84    60%    20%    20%    20%    20%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_4810faab                         4     1.62    75%    75%    50%    25%    25%     0%     0%
gen_902fb1fd                         4     1.10    75%    50%     0%     0%     0%     0%     0%
gen_14e1775b                         4     0.97    50%    25%     0%     0%     0%     0%     0%
gen_dfb554f7                         4     1.28   100%    75%    25%     0%     0%     0%     0%
gen_f001d778                         4     1.07    75%    50%     0%     0%     0%     0%     0%
gen_684d7623                         4     0.53    75%     0%     0%     0%     0%     0%     0%
gen_4f890271                         4     1.09    50%    50%    25%     0%     0%     0%     0%
gen_c0fd1d91                         4     0.40    25%    25%    25%    25%    25%     0%     0%
gen_1f7ead60                         4     1.25    50%    50%     0%     0%     0%     0%     0%
gen_f3661202                         4     1.03    75%    50%     0%     0%     0%     0%     0%
gen_a32bee42                         4     1.11    50%    50%     0%     0%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%

STOP LOSS divisi per come sono morti (184 su 417 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  82   45%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino ....... 101   55%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.49R, massima 1.23R; con un primo gradino a 0.49R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6   0.8/1.6/2.4
------------------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             417      -0.408        -0.424        -0.764        -0.854        -0.269 *
gen_fca11c08                        14      -0.689        -0.679        -0.896        -0.886        -0.346 *
gen_fa304106                        11      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_bb762669                        11      -0.473        -0.482        -0.655        -0.745        -0.262 *
gen_cd5c842f                        10      +0.145        +0.150 *      -0.275        -0.560        +0.108  
gen_e59ad90b                        10      -0.825        -0.810        -0.855        -0.840        -0.236 *
gen_4465723e                         9      -0.228        -0.278        -0.839        -1.000        +0.018 *
gen_4c6df481                         9      -0.372        -0.356        -0.839        -0.822        -0.120 *
gen_ceab7f6a                         9      -0.661        -0.711        -0.839        -1.000        -0.533 *
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000        -0.823  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000        -0.400  
gen_490a90e5                         7      -0.814        -0.814        -1.000        -1.000        -0.646 *
gen_18c839a0                         6      -0.492        -0.467        -0.758        -0.733        -0.093 *
gen_9a383fff                         6      -0.350        -0.350        -1.000        -1.000        -0.173 *
gen_8b91ba18                         6      -0.275        -0.350        -0.758        -1.000        -0.093 *
gen_c5194ce4                         6      -0.783 *      -0.783        -1.000        -1.000        -0.793  
gen_bf1e00d4                         6      -0.250        -0.167        -0.367        -0.267        +0.147 *
gen_c647ead7                         6      -0.783 *      -0.783        -1.000        -1.000        -0.793  
gen_a640dfa5                         6      -0.058        -0.133        -0.758        -1.000        +0.033 *
gen_6d06dca0                         6      -0.200        -0.350        -0.517        -1.000        -0.173 *
gen_725cb5f4                         5      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_b2f350ff                         5      -0.190        -0.120        -0.130        -0.440        +0.032 *
gen_771790b1                         5      -0.130 *      -0.220        -0.710        -1.000        -0.160  
gen_96c1ed1b                         5      -0.190        -0.120        -0.530        -0.680        +0.032 *
gen_fb7d035a                         5      -0.450        -0.380        -0.530        -0.680        +0.032 *
gen_f238d283                         5      -0.040        +0.020        -0.420        -0.360        +0.184 *
gen_4810faab                         4      +0.450 *      +0.425        -0.050        -0.600        +0.410  
gen_902fb1fd                         4      -0.350        -0.350        -1.000        -1.000        -0.070 *
gen_14e1775b                         4      -0.675        -0.675        -1.000        -1.000        -0.380 *
gen_dfb554f7                         4      +0.087        -0.025        -0.637        -1.000        +0.360 *
gen_f001d778                         4      -0.350        -0.350        -1.000        -1.000        -0.070 *
gen_684d7623                         4      -1.000 *      -1.000        -1.000        -1.000        -1.000  
gen_4f890271                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_c0fd1d91                         4      -0.312        -0.225 *      -0.413        -0.600        -0.330  
gen_1f7ead60                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_f3661202                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_a32bee42                         4      -0.350 *      -0.350        -1.000        -1.000        -0.380  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000        +0.050  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000        -0.260  
gen_b31d8b93                         4      -0.237        -0.200        -0.637        -0.600        +0.050 *

    0.8/1.6/2.4 = SOLO MISURA (4 ott 2026): il gate non la prova, il bot non la opera.
(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misu

[... 6073 caratteri omessi (testa e coda conservate) ...]

8c22b92            long    1.50   2.08   0.76   no    no    no 
ZECUSDT     gen_e6ddc613            long    1.00   4.59   0.44   no    no    no 
SYRUPUSDT   gen_4c6df481            long    2.00   5.47   0.07   no    no    no 
PUMPUSDT    gen_08664b28            long    1.50   3.78   0.48   no    no    no 
STXUSDT     gen_14e1775b            long    2.00   2.25   0.44   no    no    no 
USELESSUSDT gen_e09c5203            long    2.00   5.18   2.45   si    no    si 
SPXUSDT     gen_64263ae7            long    1.50   3.62   1.23   no    no    no 
PNUTUSDT    gen_4810faab            short   2.00   1.74   3.69   si    si    si 
BULLAUSDT   gen_5a52c06b            long    1.50   5.68   0.03   no    no    no 
HEIUSDT     gen_9a383fff            long    2.00   2.68   0.24   no    no    no 
CVCUSDT     gen_cb4d9121            long    2.00   4.69   0.28   no    no    no 
XPINUSDT    gen_902fb1fd            long    0.75   4.00   0.40   no    no    no 
ASTERUSDT   gen_d74845a5            long    1.50   4.01   0.68   no    no    no 
TUTUSDT     gen_4465723e            short   1.50   0.58   1.29   no    si    si 
DEXEUSDT    gen_b9c251a1            long    1.00   3.79   0.53   no    no    no 
UBUSDT      gen_5b847426            long    1.50   4.52   1.37   no    no    no 
CROSSUSDT   gen_4e6e1ae0            long    2.00   2.94   0.33   no    no    no 
QUSDT       gen_18c839a0            short   1.50   2.85   0.24   no    no    no 
SPXUSDT     gen_725cb5f4            long    0.75   3.81   0.47   no    no    no 
HUSDT       gen_22b2cade            long    1.50   3.94   1.32   no    no    no 
SUIUSDT     gen_8c9b332f            long    1.00   4.29   0.58   no    no    no 
BULLAUSDT   gen_5a52c06b            long    1.50   6.55   1.07   no    no    no 
AIOUSDT     gen_fc644cd2            short   1.00   3.07   0.59   no    no    no 
OPENUSDT    gen_46f0717f            short   2.00   1.51   0.86   no    no    no 
XPINUSDT    gen_2e0818c8            short   0.75   2.63   0.00   no    no    no 
1000PEPEUSD gen_f9d90376            long    2.00   5.71   1.01   no    no    no 
HEMIUSDT    gen_acea368d            short   1.50   2.12   0.00   no    no    no 
QUSDT       gen_1f224994            short   1.50   3.12   0.80   no    no    no 
(mostrati i 40 piu' recenti su 409)

  trade misurati: 409 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.27R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  41   10%
  raggiunto il livello strutturale ........  34    8%
  raggiunto il piu' vicino dei due ........  60   15%
  Lettura: il livello strutturale sta in mediana a 3.27R (primo gradino mediano 1.50R) e viene raggiunto nel 8% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 15% dei casi; il livello e' piu' vicino del TP1 in 80 trade su 409.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  0GUSDT LONG (gen_aa6bb820, 15m): stop 2.0% · TP1 1.5R = 3.1% · TP2 3R = 6.1% · TP3 5R = 10.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.7%
    TP prima dello stop: TP1   42% · TP2   20% · TP3    8%
    TP comunque entro l'orizzonte: TP1   58% · TP2   28% · TP3   12%

  CATIUSDT LONG (gen_b3e46005, 15m): stop 1.3% · TP1 1.5R = 1.9% · TP2 3R = 3.9% · TP3 5R = 6.5%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.3%
    TP prima dello stop: TP1   44% · TP2   25% · TP3   13%
    TP comunque entro l'orizzonte: TP1   70% · TP2   44% · TP3   25%

  FLOCKUSDT SHORT (gen_c5194ce4, 15m): stop 2.8% · TP1 0.75R = 2.1% · TP2 1.25R = 3.5% · TP3 1.75R = 4.8%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.9%
    TP prima dello stop: TP1   50% · TP2   31% · TP3   21%
    TP comunque entro l'orizzonte: TP1   63% · TP2   42% · TP3   31%

  ORCAUSDT LONG (gen_fb3d971f, 15m): stop 5.0% · TP1 1.5R = 7.6% (preso) · TP2 3R = 15.1% · TP3 5R = 25.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.4%
    TP prima dello stop: TP1   13% · TP2    5% · TP3    2%
    TP comunque entro l'orizzonte: TP1   13% · TP2    5% · TP3    2%

  PUMPUSDT LONG (gen_13cc61f2, 15m): stop 3.7% · TP1 1.5R = 5.5% · TP2 3R = 11.1% · TP3 5R = 18.5%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 5.4%
    TP prima dello stop: TP1   41% · TP2   17% · TP3    5%
    TP comunque entro l'orizzonte: TP1   49% · TP2   21% · TP3    6%

  SOPHUSDT LONG (gen_42acf37e, 15m): stop 3.4% · TP1 1.5R = 5.0% (preso) · TP2 3R = 10.1% · TP3 5R = 16.8%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.5%
    TP prima dello stop: TP1   27% · TP2   10% · TP3    4%
    TP comunque entro l'orizzonte: TP1   29% · TP2   11% · TP3    5%

  SUPERUSDT SHORT (gen_0eb999b7, 15m): stop 3.1% · TP1 1.5R = 4.7% · TP2 3R = 9.4% · TP3 5R = 15.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 1.7%
    TP prima dello stop: TP1   10% · TP2    1% · TP3    0%
    TP comunque entro l'orizzonte: TP1   13% · TP2    2% · TP3    0%

  VETUSDT LONG (gen_b9c251a1, 15m): stop 3.1% · TP1 1R = 3.1% (preso) · TP2 1.5R = 4.7% (preso) · TP3 2.5R = 7.8%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.3%
    TP prima dello stop: TP1   36% · TP2   24% · TP3   12%
    TP comunque entro l'orizzonte: TP1   39% · TP2   26% · TP3   13%

  ZORAUSDT SHORT (gen_ceab7f6a, 15m): stop 3.2% · TP1 1.5R = 4.8% · TP2 3R = 9.5% · TP3 5R = 15.9%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.0%
    TP prima dello stop: TP1   20% · TP2    4% · TP3    1%
    TP comunque entro l'orizzonte: TP1   27% · TP2    6% · TP3    2%

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

  trade chiusi letti: 417 · a 15m: 417 (esplorativi: 18) · altri timeframe, fuori dalla curva: 0
  misurati: 337 su 22 giornate (esplorativi fra i misurati: 13) · saltati: 80 (nessun ingresso a caso utilizzabile: 1, nessuna candela chiusa subito prima dell'ingresso: 35, orizzonte oltre i dati (o buco nella serie): 44)
  ingressi a caso per segnale: mediana 20, minimo 5
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    337    -0.004  -0.003    -0.000  [-0.109, +0.122]  |        -0.07  -0.02  -0.05  [-0.37, +0.27]
  4 ore    337    -0.001  -0.034    +0.033  [-0.089, +0.168]  |        -0.05  -0.11  +0.07  [-0.35, +0.46]
  12 ore   337    +0.004  -0.069    +0.074  [-0.101, +0.240]  |        -0.11  -0.21  +0.10  [-0.49, +0.65]
  24 ore   337    -0.230  -0.195    -0.035  [-0.234, +0.145]  |        -0.81  -0.61  -0.20  [-0.89, +0.39]

  Per verso (solo informativo, non decide):
  long (162 trade, 21 giornate): 1 ora -0.039 [-0.114, +0.029] · 4 ore +0.024 [-0.071, +0.111] · 12 ore +0.050 [-0.183, +0.233] · 24 ore -0.077 [-0.459, +0.175]
  short (175 trade, 21 giornate): 1 ora +0.035 [-0.152, +0.287] · 4 ore +0.042 [-0.158, +0.285] · 12 ore +0.095 [-0.149, +0.385] · 24 ore +0.004 [-0.275, +0.286]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 337 trade su 22 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 75.6s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
