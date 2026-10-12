# 0601-12ott-analisi-trade-autopsy.req

_eseguito: 2026-10-12 17:10 UTC_

**richiesta:** `autopsy`
**eseguito:** `.venv/bin/python -m scripts.gate_autopsy`
**esito:** codice 0 in 1.6s

```
[firebase] connesso (Firestore + RTDB)

=== STRATEGIE BASE (optimize) · 21 Sep 12:43 UTC ===
  1320 valutazioni · 0 passate (0.00%) · 1320 diagnosticate

  DOVE MUOIONO (criterio messo peggio):
    trades               6    0.5%  — pochi segnali: la strategia spara troppo poco su questo timeframe
    holdout              1    0.1%  — funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento
    pf_ex_top            3    0.2%  — regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge
    recovery            64    4.8%  — la curva scava buche troppo profonde rispetto a quanto rende
    total_return      1207   91.4%  — profittevole, ma di troppo poco per valere il rischio
    consistency         17    1.3%  — guadagna in un periodo e perde negli altri: non e' un edge stabile
    regime              22    1.7%  — in almeno un regime di mercato perde in modo conclamato

  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):
    pf_ex_top         1312   99.4% delle bocciate
    total_return      1276   96.7% delle bocciate
    consistency       1303   98.7% delle bocciate
    holdout              1    0.1% delle bocciate
    trades              11    0.8% delle bocciate
    win_rate           821   62.2% delle bocciate
    pf                1301   98.6% delle bocciate
    recovery          1304   98.8% delle bocciate
    oos_windows          4    0.3% delle bocciate
    -> pf_ex_top, total_return, consistency, pf, recovery: presente in quasi TUTTE le bocciature. Non sta
       filtrando fra candidate, sta descrivendo il terreno in cui cerchiamo.

  QUASI-PASSAGGI (un solo criterio, mancato di poco): 1
    WUSDT|mean_reversion               manca   0.0% su holdout · PF 1.681 · 124 trade · t=2.313
    (sono i semi da cui il prossimo run fa mutare le candidate)

=== STRATEGIE GENERATE (discover) · 12 Oct 16:13 UTC ===
  26986 valutazioni · 78 passate (0.29%) · 26908 diagnosticate

  DOVE MUOIONO (criterio messo peggio):
    trades             789    2.9%  — pochi segnali: la strategia spara troppo poco su questo timeframe
    holdout            122    0.5%  — funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento
    pf_ex_top          115    0.4%  — regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge
    recovery          1542    5.7%  — la curva scava buche troppo profonde rispetto a quanto rende
    total_return     21824   81.1%  — profittevole, ma di troppo poco per valere il rischio
    consistency        401    1.5%  — guadagna in un periodo e perde negli altri: non e' un edge stabile
    regime            2115    7.9%  — in almeno un regime di mercato perde in modo conclamato

  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):
    pf_ex_top        26155   97.2% delle bocciate
    total_return     25274   93.9% delle bocciate
    consistency      25435   94.5% delle bocciate
    win_rate           908    3.4% delle bocciate
    pf               25692   95.5% delle bocciate
    trades            1180    4.4% delle bocciate
    holdout            122    0.5% delle bocciate
    recovery         25600   95.1% delle bocciate
    oos_windows         25    0.1% delle bocciate
    -> pf_ex_top, total_return, consistency, pf, recovery: presente in quasi TUTTE le bocciature. Non sta
       filtrando fra candidate, sta descrivendo il terreno in cui cerchiamo.

  QUASI-PASSAGGI (un solo criterio, mancato di poco): 40
    AINUSDT|gen_c934a6f7               manca   0.0% su holdout · PF 1.346 · 11 trade · t=0.4
    TAGUSDT|gen_aa248d33               manca   0.1% su recovery · PF 1.468 · 67 trade · t=1.25
    BRETTUSDT|gen_fa304106             manca   0.1% su pf_ex_top · PF 1.388 · 117 trade · t=1.336
    EVAAUSDT|gen_51732291              manca   0.5% su pf_ex_top · PF 1.316 · 129 trade · t=1.25
    HEMIUSDT|gen_4c6df481              manca   0.7% su pf_ex_top · PF 1.316 · 179 trade · t=1.483
    VIRTUALUSDT|gen_a3088356           manca   0.8% su pf_ex_top · PF 1.342 · 84 trade · t=1.057
    MITOUSDT|gen_0919b67a              manca   0.9% su pf_ex_top · PF 1.5 · 124 trade · t=1.596
    BULLAUSDT|gen_11a02ce6             manca   1.2% su total_return · PF 1.38 · 49 trade · t=0.9
    JUPUSDT|gen_938d15dc               manca   1.4% su holdout · PF 1.434 · 15 trade · t=0.571
    ENAUSDT|gen_938d15dc               manca   1.5% su pf_ex_top · PF 1.385 · 199 trade · t=1.768
    (sono i semi da cui il prossimo run fa mutare le candidate)

  FERMATE SOLO DA pf_ex_top: 28 · miglior t = 1.92 · ne servirebbe 3.96 · le superano in 0
  La soglia NON e' il canonico 2: con 26986 test per run, a t=2 ci si aspettano
  ~614 candidate per puro caso. 3.96 e' il valore che ne lascia
  passare al massimo una. Sotto quel livello 'pf_ex_top boccia un edge vero' non e'
  una conclusione che i dati sostengono — e' la stessa lotteria vista da un'altra
  angolazione.

COSA FARSENE. Il criterio dominante dice su cosa lavorare, e NON e' mai
'abbassare quella soglia': una soglia abbassata finche' qualcosa passa
seleziona esattamente il rumore che la soglia esisteva per escludere.
```
