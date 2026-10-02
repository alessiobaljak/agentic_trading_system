# 0437-2ott-t2-curva.req

_eseguito: 2026-10-02 06:21 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 65.3s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 224 · con mfe_r registrato: 224
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 86 trade su 224 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             224     0.85    68%    41%    16%     7%     2%     1%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_bb762669                         7     0.79    86%    29%    14%     0%     0%     0%     0%
gen_fa304106                         7     0.10    43%     0%     0%     0%     0%     0%     0%
gen_cd5c842f                         7     1.10    86%    71%    29%    29%    14%    14%    14%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_4465723e                         6     1.36   100%    50%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_ba3a671f                         6     0.33    33%    17%     0%     0%     0%     0%     0%
gen_4c6df481                         5     1.01    60%    60%    20%    20%     0%     0%     0%
gen_e59ad90b                         5     0.86    80%    20%    20%    20%     0%     0%     0%
gen_18c839a0                         5     0.91    80%    40%    20%    20%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_771790b1                         4     1.32    75%    50%    25%     0%     0%     0%     0%
gen_a640dfa5                         4     1.17   100%   100%    25%     0%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%
gen_bf1e00d4                         4     0.90    75%    25%    25%    25%    25%    25%     0%
gen_7ac562e3                         3     1.13    67%    67%     0%     0%     0%     0%     0%
gen_c0fd1d91                         3     0.14     0%     0%     0%     0%     0%     0%     0%
gen_8b91ba18                         3     0.85   100%    33%     0%     0%     0%     0%     0%
gen_f3661202                         3     0.77    67%    33%     0%     0%     0%     0%     0%
gen_c5194ce4                         3     0.05    33%    33%     0%     0%     0%     0%     0%
gen_35632db9                         3     0.84    67%    33%     0%     0%     0%     0%     0%
gen_f3124a14                         3     0.58    67%    33%    33%    33%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (100 su 224 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  46   46%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  53   53%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.56R, massima 1.23R; con un primo gradino a 0.56R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             224      -0.373 *      -0.404        -0.748        -0.877  
gen_fca11c08                        14      -0.689        -0.679 *      -0.896        -0.886  
gen_bb762669                         7      -0.564 *      -0.629        -0.793        -1.000  
gen_fa304106                         7      -1.000 *      -1.000        -1.000        -1.000  
gen_cd5c842f                         7      +0.200        +0.271 *      -0.171        -0.371  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000  
gen_490a90e5                         7      -0.814 *      -0.814        -1.000        -1.000  
gen_4465723e                         6      -0.275 *      -0.350        -0.758        -1.000  
gen_6d06dca0                         6      -0.200 *      -0.350        -0.517        -1.000  
gen_ba3a671f                         6      -0.783 *      -0.783        -1.000        -1.000  
gen_4c6df481                         5      -0.130        -0.100 *      -0.710        -0.680  
gen_e59ad90b                         5      -0.650        -0.620 *      -0.710        -0.680  
gen_18c839a0                         5      -0.390        -0.360 *      -0.710        -0.680  
gen_f238d283                         5      -0.040        +0.020 *      -0.420        -0.360  
gen_771790b1                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_a640dfa5                         4      +0.412 *      +0.300        -0.637        -1.000  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_b31d8b93                         4      -0.237        -0.200 *      -0.637        -0.600  
gen_bf1e00d4                         4      -0.312        -0.225 *      -0.413        -0.300  
gen_7ac562e3                         3      -0.133 *      -0.133        -1.000        -1.000  
gen_c0fd1d91                         3      -1.000 *      -1.000        -1.000        -1.000  
gen_8b91ba18                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_f3661202                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_c5194ce4                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_35632db9                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_f3124a14                         3      -0.083 *      -0.367        -0.517        -0.467  
gen_b9bf5d01                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_af734c68                         3      -0.567 *      -0.567        -1.000        -1.000  

(*) scala col miglior R medio in questo gruppo, secondo il modello
    semplificato: gradini raggiunti = incassati, residuo a break-even.
    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,
    che simula il percorso completo con lo stop che si sposta.
    Campioni piccoli non decidono nulla: guardare la colonna n.

LIVELLO STRUTTURALE all'ingresso (A5, passo 1: misurare)
  livello = massimo (long) / minimo (short) delle ultime 96 candele a 15m
  oltre il prezzo d'ingresso (192 se in 96 non c'e' niente), in R dello stop.
[backtest] dati da cache: 985 candele (HUMAUSDT 15m)
[backtest] dati da cache: 505 candele (AIOUSDT 15m)
[backtest] dati da cache: 1081 candele (BULLAUSDT 15m)
[backtest] dati da cache: 1749 candele (SYRUPUSDT 15m)
[backtest] dati da cache: 981 candele (ZORAUSDT 15m)
[backtest] dati da cache: 1365 candele (QUSDT 15m)
[backtest] dati da cache: 769 candele (JUPUSDT 15m)
[backtest] dati da cache: 385 candele (SCRUSDT 15m)
[backtest] dati da cache: 865 candele (TAUSDT 15m)
[backtest] dati da cache: 577 candele (BTRUSDT 15m)
[backtest] dati da cache: 865 candele (TSTUSDT 15m)
[backtest] dati da cache: 385 candele (SUPERUSDT 15m)
[backtest] dati da cache: 1057 candele (XPLUSDT 15m)
[backtest] dati da cache: 961 candele (ENAUSDT 15m)
[backtest] dati da cache: 1345 candele (USELESSUSDT 15m)
[backtest] dati da cache: 385 candele (JASMYUSDT 15m)
[backtest] dati da cache: 1633 candele (ORCAUSDT 15m)
[backtest] dati da cache: 865 candele (MITOUSDT 15m)
[backtest] dati da cache: 601 candele (PNUTUSDT 15m)
[backtest] dati da cache: 601 candele (PHAUSDT 15m)
[backtest] dati da cache: 697 candele (HEMIUSDT 15m)
[backtest] dati da cache: 505 candele (UBUSDT 15m)
[backtest] dati da cache: 865 candele (SUIUSDT 15m)
[backtest] dati da cache: 1537 candele (TUTUSDT 15m)
[backtest] dati da cache: 1057 candele (DOTUSDT 15m)
[backtest] dati da cache: 1249 candele (MUBARAKUSDT 15m)
[backtest] dati da cache: 769 candele (CROSSUSDT 15m)
[backtest] dati da cache: 1441 candele (STXUSDT 15m)
[backtest] dati da cache: 673 candele (SEIUSDT 15m)
[backtest] dati da cache: 385 candele (RAYSOLUSDT 15m)
[backtest] dati da cache: 385 candele (GALAUSDT 15m)
[backtest] dati da cache: 385 candele (AXSUSDT 15m)
[backtest] dati da binance: 481 candele
[backtest] dati da cache: 385 candele (OPENUSDT 15m)
[backtest] dati da binance: 673 candele
[backtest] dati da binance: 1441 candele
[backtest] dati da binance: 1345 candele
[backtest] dati da binance: 1633 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 577 candele
[backtest] dati da binance: 577 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 1345 candele
[backtest] dati da cache: 1249 candele (VETUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da cache: 1249 candele (NEIROUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 481 candele
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 577 candele

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
JUPUSDT     gen_bb762669            long    1.50   1.49   1.50   no    si    si 
RAYSOLUSDT  gen_fa304106            long    2.00   1.41   0.06   no    no    no 
GALAUSDT    gen_b9aa9989            long    1.00   0.51   0.01   no    no    no 
UBUSDT      gen_fb7d035a            long    1.50   2.53   0.84   no    no    no 
HEMIUSDT    gen_f001d778            long    2.00   2.32   1.08   no    no    no 
AIOUSDT     gen_581d4a68            long    2.00   1.40   0.13   no    no    no 
STXUSDT     gen_a5b0e4de            short   2.00   1.06   0.89   no    no    no 
UBUSDT      gen_f3661202            long    2.00   6.51   1.16   no    no    no 
CROSSUSDT   gen_d606fde3            long    2.00   1.74   1.16   no    no    no 
TUTUSDT     gen_4465723e            long    1.50   0.25   0.82   no    si    si 
DOTUSDT     gen_919c110c            short   2.00   3.60   1.18   no    no    no 
SUIUSDT     gen_8c9b332f            short   1.00   2.67   0.82   no    no    no 
QUSDT       gen_85fadf54            long    1.50   3.85   0.01   no    no    no 
HUMAUSDT    gen_771790b1            short   2.00   2.99   0.29   no    no    no 
UBUSDT      gen_fb7d035a            long    1.50   4.62   0.37   no    no    no 
QUSDT       gen_18c839a0            short   1.50   1.63   0.91   no    no    no 
SYRUPUSDT   gen_f3b97917            long    1.00   4.25   0.92   no    no    no 
HEMIUSDT    gen_f4c1300a            short   1.50   2.80   0.89   no    no    no 
TSTUSDT     gen_a640dfa5            short   2.00   1.30   1.52   no    si    si 
MITOUSDT    gen_8b91ba18            short   2.00   2.05   0.62   no    no    no 
PHAUSDT     gen_fa304106            long    1.50   2.26   0.08   no    no    no 
PNUTUSDT    gen_4810faab            long    2.00   2.52   1.62   no    no    no 
JASMYUSDT   gen_b2f350ff            short   2.00   2.89   0.17   no    no    no 
ORCAUSDT    gen_cb8176f2            short   1.50   6.17   0.41   no    no    no 
BTRUSDT     gen_8981d5f2            long    1.50   2.96   1.31   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   2.17   0.00   no    no    no 
XPLUSDT     gen_e59ad90b            short   1.50   2.49   0.80   no    no    no 
ENAUSDT     gen_bb762669            long    1.50   1.85   0.44   no    no    no 
USELESSUSDT gen_c0fd1d91            long    1.50   3.35   0.40   no    no    no 
SUPERUSDT   gen_0eb999b7            short   1.50   1.11   0.49   no    no    no 
BTRUSDT     gen_8981d5f2            short   1.50   2.10   0.80   no    no    no 
QUSDT       gen_85fadf54            long    1.50   3.54   0.38   no    no    no 
JUPUSDT     gen_bb762669            short   1.50   1.81   0.87   no    no    no 
TAUSDT      gen_4e6e1ae0            long    2.00   2.50   0.00   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   2.22   1.65   si    no    si 
SCRUSDT     gen_bd8f158b            short   2.00   4.71   2.11   si    no    si 
SYRUPUSDT   gen_4c6df481            long    2.00   1.56   1.01   no    no    no 
AIOUSDT     gen_581d4a68            long    2.00   2.04   0.13   no    no    no 
BULLAUSDT   gen_7ac562e3            short   1.50   6.16   0.11   no    no    no 
HUMAUSDT    gen_771790b1            short   2.00   4.64   0.73   no    no    no 
(mostrati i 40 piu' recenti su 216)

  trade misurati: 216 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.12R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  22   10%
  raggiunto il livello strutturale ........  15    7%
  raggiunto il piu' vicino dei due ........  32   15%
  Lettura: il livello strutturale sta in mediana a 3.12R (primo gradino mediano 1.50R) e viene raggiunto nel 7% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 15% dei casi; il livello e' piu' vicino del TP1 in 45 trade su 216.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  CROSSUSDT LONG (gen_d606fde3, 15m): stop 3.9% · TP1 2R = 7.9% · TP2 4R = 15.8% · TP3 6R = 23.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.2%
    TP prima dello stop: TP1   23% · TP2    8% · TP3    4%
    TP comunque entro l'orizzonte: TP1   25% · TP2    9% · TP3    4%

  ENAUSDT SHORT (gen_bb762669, 15m): stop 2.5% · TP1 1.5R = 3.7% · TP2 3R = 7.5% · TP3 5R = 12.4%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.9%
    TP prima dello stop: TP1   25% · TP2    6% · TP3    0%
    TP comunque entro l'orizzonte: TP1   37% · TP2   10% · TP3    0%

  HEMIUSDT SHORT (gen_f001d778, 15m): stop 1.8% · TP1 2R = 3.7% · TP2 4R = 7.4% · TP3 6R = 11.0%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.4%
    TP prima dello stop: TP1   29% · TP2   11% · TP3    5%
    TP comunque entro l'orizzonte: TP1   58% · TP2   28% · TP3   15%

  SYRUPUSDT LONG (gen_4c6df481, 15m): stop 2.1% · TP1 2R = 4.2% · TP2 4R = 8.5% · TP3 6R = 12.7%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.0%
    TP prima dello stop: TP1   30% · TP2   11% · TP3    5%
    TP comunque entro l'orizzonte: TP1   38% · TP2   14% · TP3    6%

  Nel paper (trade chiusi): almeno 1 gradino   11% · almeno 2    1% · tutti e 3    1%
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

  trade chiusi letti: 224 · a 15m: 224 (esplorativi: 8) · altri timeframe, fuori dalla curva: 0
  misurati: 201 su 15 giornate (esplorativi fra i misurati: 8) · saltati: 23 (nessuna candela chiusa subito prima dell'ingresso: 7, orizzonte oltre i dati (o buco nella serie): 16)
  ingressi a caso per segnale: mediana 20, minimo 2
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    201    -0.083  -0.003    -0.080  [-0.205, +0.029]  |        -0.28  -0.03  -0.25  [-0.66, +0.12]
  4 ore    201    -0.032  -0.031    -0.001  [-0.129, +0.127]  |        -0.09  -0.13  +0.04  [-0.43, +0.51]
  12 ore   201    -0.072  -0.098    +0.026  [-0.217, +0.253]  |        -0.39  -0.32  -0.07  [-0.85, +0.68]
  24 ore   201    -0.406  -0.337    -0.068  [-0.341, +0.179]  |        -1.37  -1.10  -0.27  [-1.24, +0.59]

  Per verso (solo informativo, non decide):
  long (84 trade, 14 giornate): 1 ora -0.046 [-0.188, +0.055] · 4 ore -0.029 [-0.184, +0.074] · 12 ore -0.055 [-0.394, +0.173] · 24 ore -0.141 [-0.858, +0.304]
  short (117 trade, 14 giornate): 1 ora -0.104 [-0.317, +0.092] · 4 ore +0.019 [-0.175, +0.231] · 12 ore +0.084 [-0.216, +0.462] · 24 ore -0.016 [-0.364, +0.288]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 201 trade su 15 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 48.0s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
