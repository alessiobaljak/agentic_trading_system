# 0451-3ott-mattina-mfe.req

_eseguito: 2026-10-03 06:05 UTC_

**richiesta:** `mfe`
**eseguito:** `.venv/bin/python -m scripts.mfe_report`
**esito:** codice 0 in 89.9s

```
[firebase] connesso (Firestore + RTDB)
[mfe] trade chiusi: 246 · con mfe_r registrato: 246
[mfe] scala globale attuale: (1.5, 3.0, 5.0) quote (0.3, 0.3, 0.4)

[mfe] 94 trade su 246 sono in gruppi sotto --min-trades 3 e NON compaiono nelle righe per gruppo (compaiono solo nel TOTALE).
gruppo                               n  mediana  ≥0.5R    ≥1R  ≥1.5R    ≥2R    ≥3R    ≥4R    ≥5R
------------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             246     0.85    68%    41%    15%     7%     2%     1%     0%
gen_fca11c08                        14     0.82    50%    21%     7%     7%     0%     0%     0%
gen_bb762669                         8     0.81    88%    25%    12%     0%     0%     0%     0%
gen_ba3a671f                         7     0.33    29%    14%     0%     0%     0%     0%     0%
gen_fa304106                         7     0.10    43%     0%     0%     0%     0%     0%     0%
gen_cd5c842f                         7     1.10    86%    71%    29%    29%    14%    14%    14%
gen_2031005e                         7     0.80    57%    43%    14%     0%     0%     0%     0%
gen_490a90e5                         7     0.62    71%    14%     0%     0%     0%     0%     0%
gen_e59ad90b                         6     0.86    67%    17%    17%    17%     0%     0%     0%
gen_4c6df481                         6     1.27    67%    67%    17%    17%     0%     0%     0%
gen_4465723e                         6     1.36   100%    50%    17%     0%     0%     0%     0%
gen_6d06dca0                         6     1.05    67%    50%    33%     0%     0%     0%     0%
gen_18c839a0                         5     0.91    80%    40%    20%    20%     0%     0%     0%
gen_f238d283                         5     1.37    80%    60%    40%    40%     0%     0%     0%
gen_c5194ce4                         4     0.20    25%    25%     0%     0%     0%     0%     0%
gen_771790b1                         4     1.32    75%    50%    25%     0%     0%     0%     0%
gen_a640dfa5                         4     1.17   100%   100%    25%     0%     0%     0%     0%
gen_658b2edb                         4     1.30   100%    75%    25%     0%     0%     0%     0%
gen_e50a9211                         4     1.30    50%    50%    25%     0%     0%     0%     0%
gen_b31d8b93                         4     1.23    75%    50%    25%    25%     0%     0%     0%
gen_bf1e00d4                         4     0.90    75%    25%    25%    25%    25%    25%     0%
gen_d606fde3                         3     0.44    33%    33%     0%     0%     0%     0%     0%
gen_fb7d035a                         3     0.37    33%     0%     0%     0%     0%     0%     0%
gen_ceab7f6a                         3     1.45    67%    67%    33%     0%     0%     0%     0%
gen_7ac562e3                         3     1.13    67%    67%     0%     0%     0%     0%     0%
gen_c0fd1d91                         3     0.14     0%     0%     0%     0%     0%     0%     0%
gen_8b91ba18                         3     0.85   100%    33%     0%     0%     0%     0%     0%
gen_f3661202                         3     0.77    67%    33%     0%     0%     0%     0%     0%
gen_35632db9                         3     0.84    67%    33%     0%     0%     0%     0%     0%
gen_f3124a14                         3     0.58    67%    33%    33%    33%     0%     0%     0%
gen_b9bf5d01                         3     0.74   100%    33%     0%     0%     0%     0%     0%
gen_af734c68                         3     0.94    67%    33%     0%     0%     0%     0%     0%

STOP LOSS divisi per come sono morti (107 su 246 trade):
  sbagliati dall'inizio (mfe < 0.25R) ..........  51   48%   -> problema di INGRESSO
  andati a favore ma sotto il 1° gradino .......  55   51%   -> problema di USCITA
  oltre il 1° gradino e poi stop ...............   1    1%   -> protezione del profitto
  fra i «quasi»: mfe mediana 0.52R, massima 1.23R; con un primo gradino a 0.52R meta' di loro avrebbe incassato
  (primo gradino GLOBALE 1.5R: per coppia vale la sua scala (registro non in mano))

R medi incassati per scala (modello semplificato, quote (0.3, 0.3, 0.4)):
gruppo                               n     1/1.5/2.5         1/2/3       1.5/3/5         2/4/6
----------------------------------------------------------------------------------------------
TOTALE (tutti i trade)             246      -0.373 *      -0.400        -0.759        -0.875  
gen_fca11c08                        14      -0.689        -0.679 *      -0.896        -0.886  
gen_bb762669                         8      -0.619 *      -0.675        -0.819        -1.000  
gen_ba3a671f                         7      -0.814 *      -0.814        -1.000        -1.000  
gen_fa304106                         7      -1.000 *      -1.000        -1.000        -1.000  
gen_cd5c842f                         7      +0.200        +0.271 *      -0.171        -0.371  
gen_2031005e                         7      -0.379 *      -0.443        -0.793        -1.000  
gen_490a90e5                         7      -0.814 *      -0.814        -1.000        -1.000  
gen_e59ad90b                         6      -0.708        -0.683 *      -0.758        -0.733  
gen_4c6df481                         6      -0.058        -0.033 *      -0.758        -0.733  
gen_4465723e                         6      -0.275 *      -0.350        -0.758        -1.000  
gen_6d06dca0                         6      -0.200 *      -0.350        -0.517        -1.000  
gen_18c839a0                         5      -0.390        -0.360 *      -0.710        -0.680  
gen_f238d283                         5      -0.040        +0.020 *      -0.420        -0.360  
gen_c5194ce4                         4      -0.675 *      -0.675        -1.000        -1.000  
gen_771790b1                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_a640dfa5                         4      +0.412 *      +0.300        -0.637        -1.000  
gen_658b2edb                         4      +0.087 *      -0.025        -0.637        -1.000  
gen_e50a9211                         4      -0.237 *      -0.350        -0.637        -1.000  
gen_b31d8b93                         4      -0.237        -0.200 *      -0.637        -0.600  
gen_bf1e00d4                         4      -0.312        -0.225 *      -0.413        -0.300  
gen_d606fde3                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_fb7d035a                         3      -1.000 *      -1.000        -1.000        -1.000  
gen_ceab7f6a                         3      +0.017 *      -0.133        -0.517        -1.000  
gen_7ac562e3                         3      -0.133 *      -0.133        -1.000        -1.000  
gen_c0fd1d91                         3      -1.000 *      -1.000        -1.000        -1.000  
gen_8b91ba18                         3      -0.567 *      -0.567        -1.000        -1.000  
gen_f3661202                         3      -0.567 *      -0.567        -1.000        -1.000  
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
[backtest] cache ESTESA di 121 candele (invece di riscaricarne 1465) (USELESSUSDT 15m)
[backtest] cache ESTESA di 697 candele (invece di riscaricarne 1081) (SAHARAUSDT 15m)
[backtest] dati da binance: 409 candele
[backtest] cache ESTESA di 409 candele (invece di riscaricarne 793) (STEEMUSDT 15m)
[backtest] dati da binance: 409 candele
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 793) (UBUSDT 15m)
[backtest] dati da binance: 385 candele
[backtest] dati da binance: 385 candele
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 1729) (GPSUSDT 15m)
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 769) (FLOCKUSDT 15m)
[backtest] cache ESTESA di 481 candele (invece di riscaricarne 1729) (VETUSDT 15m)
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 865) (BANKUSDT 15m)
[backtest] cache ESTESA di 289 candele (invece di riscaricarne 1921) (SPXUSDT 15m)
[backtest] cache ESTESA di 193 candele (invece di riscaricarne 961) (CROSSUSDT 15m)
[backtest] cache riusata (tagliata da 2026-10-02): 961 candele (ENAUSDT 15m)
[backtest] cache ESTESA di 169 candele (invece di riscaricarne 865) (HEMIUSDT 15m)
[backtest] cache riusata (tagliata da 2026-10-02): 385 candele (SUPERUSDT 15m)
[backtest] cache riusata (tagliata da 2026-10-02): 1057 candele (XPLUSDT 15m)
[backtest] dati da cache: 981 candele (ZORAUSDT 15m)
[backtest] cache ESTESA di 385 candele (invece di riscaricarne 769) (EPICUSDT 15m)
[backtest] dati da cache: 1749 candele (SYRUPUSDT 15m)
[backtest] dati da cache: 985 candele (HUMAUSDT 15m)
[backtest] dati da cache: 505 candele (AIOUSDT 15m)
[backtest] dati da cache: 1081 candele (BULLAUSDT 15m)
[backtest] dati da cache: 1365 candele (QUSDT 15m)
[backtest] dati da cache: 769 candele (JUPUSDT 15m)
[backtest] dati da cache: 385 candele (SCRUSDT 15m)
[backtest] dati da cache: 865 candele (TAUSDT 15m)
[backtest] dati da cache: 577 candele (BTRUSDT 15m)
[backtest] dati da cache: 865 candele (TSTUSDT 15m)
[backtest] dati da cache: 385 candele (JASMYUSDT 15m)
[backtest] dati da cache

[... 1447 caratteri omessi (testa e coda conservate) ...]

dele (HEIUSDT 15m)
[backtest] dati da cache: 385 candele (ZKUSDT 15m)
[backtest] dati da cache: 577 candele (BICOUSDT 15m)

coin        strategia               dir       r1  lvl_r  mfe_r  TP1?  liv?  min?
--------------------------------------------------------------------------------
JASMYUSDT   gen_b2f350ff            short   2.00   2.89   0.17   no    no    no 
ORCAUSDT    gen_cb8176f2            short   1.50   6.17   0.41   no    no    no 
BTRUSDT     gen_8981d5f2            long    1.50   2.96   1.31   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   2.17   0.00   no    no    no 
XPLUSDT     gen_e59ad90b            short   1.50   2.49   0.80   no    no    no 
ENAUSDT     gen_bb762669            long    1.50   1.85   0.44   no    no    no 
USELESSUSDT gen_c0fd1d91            long    1.50   3.35   0.40   no    no    no 
SUPERUSDT   gen_0eb999b7            short   1.50   1.11   0.49   no    no    no 
BTRUSDT     gen_8981d5f2            short   1.50   2.10   0.80   no    no    no 
CROSSUSDT   gen_d606fde3            long    2.00   1.50   0.44   no    no    no 
QUSDT       gen_85fadf54            long    1.50   3.54   0.38   no    no    no 
JUPUSDT     gen_bb762669            short   1.50   1.81   0.87   no    no    no 
TAUSDT      gen_4e6e1ae0            long    2.00   2.50   0.00   no    no    no 
ZORAUSDT    gen_ceab7f6a            long    1.50   2.22   1.65   si    no    si 
SCRUSDT     gen_bd8f158b            short   2.00   4.71   2.11   si    no    si 
SYRUPUSDT   gen_4c6df481            long    2.00   1.56   1.01   no    no    no 
HEMIUSDT    gen_f001d778            short   2.00   1.82   1.07   no    no    no 
ENAUSDT     gen_bb762669            short   1.50   1.23   0.81   no    no    no 
AIOUSDT     gen_581d4a68            long    2.00   2.04   0.13   no    no    no 
BULLAUSDT   gen_7ac562e3            short   1.50   6.16   0.11   no    no    no 
HUMAUSDT    gen_771790b1            short   2.00   4.64   0.73   no    no    no 
SYRUPUSDT   gen_4c6df481            long    2.00   1.26   1.27   no    si    si 
ZORAUSDT    gen_ceab7f6a            long    1.50   1.30   1.45   no    si    si 
EPICUSDT    gen_dfb554f7            long    1.50   5.19   0.87   no    no    no 
UBUSDT      gen_fb7d035a            long    1.50   3.99   0.05   no    no    no 
XPLUSDT     gen_e59ad90b            short   1.50   2.48   0.08   no    no    no 
SUPERUSDT   gen_0eb999b7            short   1.50   3.33   0.77   no    no    no 
BANKUSDT    gen_fb3d971f            long    2.00   2.90   0.14   no    no    no 
SPXUSDT     gen_ba3a671f            long    0.75   3.24   0.37   no    no    no 
VETUSDT     gen_b9c251a1            long    1.00   3.23   0.00   no    no    no 
PENGUUSDT   gen_a32bee42            long    2.00   4.86   1.39   no    no    no 
USELESSUSDT gen_194e2514            long    2.00   3.75   0.40   no    no    no 
SAHARAUSDT  gen_95aff747            long    1.50   5.23   2.21   si    no    si 
ARCUSDT     gen_96c1ed1b            long    2.00   5.93   1.35   no    no    no 
XPINUSDT    gen_c60cc1b9            long    2.00   4.80   1.06   no    no    no 
HOMEUSDT    gen_116faa2d            long    1.00   2.81   0.80   no    no    no 
GPSUSDT     gen_871647b8            long    2.00   2.11   1.32   no    no    no 
UBUSDT      gen_5b847426            long    1.50   6.97   2.30   si    no    si 
FLOCKUSDT   gen_c5194ce4            short   0.75   2.53   0.20   no    no    no 
STEEMUSDT   gen_4508a416            short   2.00   1.37   1.09   no    no    no 
(mostrati i 40 piu' recenti su 238)

  trade misurati: 238 · saltati: 8 (senza stop (o stop = ingresso): 8)
  livello strutturale mediano: 3.08R (primo gradino mediano 1.50R)
  raggiunto il primo gradino (TP1) ........  24   10%
  raggiunto il livello strutturale ........  17    7%
  raggiunto il piu' vicino dei due ........  36   15%
  Lettura: il livello strutturale sta in mediana a 3.08R (primo gradino mediano 1.50R) e viene raggiunto nel 7% dei trade contro il 10% del primo gradino: meno spesso del TP1. Prendendo il piu' vicino dei due si arriverebbe nel 15% dei casi; il livello e' piu' vicino del TP1 in 51 trade su 238.

==============================================================================
I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)
==============================================================================
Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta (ultimi 90 giorni, cache del gate in sola lettura), da OGNI candela come ingresso casuale: quante volte quel TP e' arrivato entro 96 candele PRIMA dello stop (stessa distanza dello stop vero), e quante volte comunque.

  BANKUSDT LONG (gen_87fce2d2, 15m): stop 0.8% · TP1 1.5R = 1.2% · TP2 3R = 2.5% · TP3 5R = 4.1%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.6%
    TP prima dello stop: TP1   35% · TP2   20% · TP3   13%
    TP comunque entro l'orizzonte: TP1   77% · TP2   60% · TP3   46%

  BMTUSDT LONG (gen_571cdda2, 15m): stop 1.6% · TP1 1.5R = 2.4% (preso) · TP2 3R = 4.9% · TP3 5R = 8.1%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 3.3%
    TP prima dello stop: TP1   39% · TP2   21% · TP3   10%
    TP comunque entro l'orizzonte: TP1   61% · TP2   34% · TP3   19%

  DOTUSDT LONG (gen_9588ad8e, 15m): stop 2.3% · TP1 2R = 4.6% · TP2 4R = 9.3% · TP3 6R = 13.9%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.1%
    TP prima dello stop: TP1   22% · TP2    5% · TP3    2%
    TP comunque entro l'orizzonte: TP1   24% · TP2    6% · TP3    2%

  JUPUSDT SHORT (gen_bb762669, 15m): stop 1.8% · TP1 1.5R = 2.8% (preso) · TP2 3R = 5.5% (preso) · TP3 5R = 9.2%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 2.9%
    TP prima dello stop: TP1   37% · TP2   12% · TP3    3%
    TP comunque entro l'orizzonte: TP1   52% · TP2   18% · TP3    5%

  QUSDT LONG (gen_bf2be656, 15m): stop 4.3% · TP1 1.5R = 6.4% · TP2 3R = 12.8% · TP3 5R = 21.3%
    su 8640 ingressi casuali: massimo a favore mediano in 96 candele 4.0%
    TP prima dello stop: TP1   28% · TP2    9% · TP3    3%
    TP comunque entro l'orizzonte: TP1   34% · TP2   12% · TP3    5%

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

  trade chiusi letti: 246 · a 15m: 246 (esplorativi: 8) · altri timeframe, fuori dalla curva: 0
  misurati: 207 su 16 giornate (esplorativi fra i misurati: 8) · saltati: 39 (nessuna candela chiusa subito prima dell'ingresso: 16, orizzonte oltre i dati (o buco nella serie): 23)
  ingressi a caso per segnale: mediana 20, minimo 2
  Scelte: prezzo d'ingresso = chiusura dell'ultima candela da 15m gia' chiusa all'ingresso
  (niente sguardo avanti); mossa tipica = mediana di |mossa di 24 ore| nei 30 giorni prima;
  caso = 20 ingressi per segnale, stessa moneta e direzione, nelle 12 ore DOPO il segnale (non
  prima: la direzione e' decisa col passato), solo se il loro futuro c'e' nei dati; margine =
  2000 ricampionamenti delle giornate (UTC), seme fisso. Le colonne in % non sono normalizzate:
  servono solo a farsi un'idea.

  Vantaggio in mosse tipiche di 24 ore (decide) e in % (solo per farsi un'idea):
  durata     n   segnali    caso vantaggio  margine 95%       | in %:  segn.   caso  vant.  margine 95%
  1 ora    207    -0.076  -0.008    -0.068  [-0.189, +0.042]  |        -0.26  -0.04  -0.22  [-0.61, +0.16]
  4 ore    207    -0.061  -0.075    +0.014  [-0.107, +0.156]  |        -0.19  -0.27  +0.08  [-0.37, +0.58]
  12 ore   207    -0.109  -0.137    +0.028  [-0.220, +0.253]  |        -0.51  -0.46  -0.05  [-0.88, +0.68]
  24 ore   207    -0.434  -0.356    -0.078  [-0.351, +0.171]  |        -1.47  -1.17  -0.30  [-1.25, +0.56]

  Per verso (solo informativo, non decide):
  long (88 trade, 15 giornate): 1 ora -0.051 [-0.196, +0.045] · 4 ore -0.038 [-0.183, +0.062] · 12 ore -0.054 [-0.400, +0.171] · 24 ore -0.156 [-0.831, +0.276]
  short (119 trade, 15 giornate): 1 ora -0.082 [-0.292, +0.133] · 4 ore +0.052 [-0.151, +0.276] · 12 ore +0.089 [-0.195, +0.446] · 24 ore -0.021 [-0.364, +0.272]

  Parte informativa del motore (segnali delle coppie validate negli ultimi giorni): non ancora — rigirare il motore chiede di scaricare candele, questa sezione legge solo la cache.
  Limiti: 207 trade su 16 giornate di un solo mercato; le uscite non toccano la misura (si guarda il prezzo, non il trade). Su prezzi a caso (100 prove sintetiche, 220 segnali, 16 giorni) la regola dice «nessun vantaggio» ~75-81 volte su 100: un «vantaggio» o un «peggio» a una sola durata va letto con questo in mente. (calcolo: 71.6s)

ESITO (regola del 2 ott): nessun vantaggio misurabile: a tutte le durate (1 ora, 4 ore, 12 ore e 24 ore) il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si ferma: il problema e' l'ingresso (o il gate: R1).
```
