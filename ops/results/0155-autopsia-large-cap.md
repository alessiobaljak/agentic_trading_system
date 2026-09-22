# 0155-autopsia-large-cap.req

_eseguito: 2026-09-22 20:14 UTC_

**richiesta:** `autopsy`
**eseguito:** `.venv/bin/python -m scripts.gate_autopsy`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)

=== STRATEGIE BASE (optimize) · 21 Sep 12:43 UTC ===
  1320 valutazioni · 0 passate (0.00%) · 1320 diagnosticate

  DOVE MUOIONO (criterio messo peggio):
    recovery            64    4.8%  — la curva scava buche troppo profonde rispetto a quanto rende
    consistency         17    1.3%  — guadagna in un periodo e perde negli altri: non e' un edge stabile
    holdout              1    0.1%  — funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento
    trades               6    0.5%  — pochi segnali: la strategia spara troppo poco su questo timeframe
    total_return      1207   91.4%  — profittevole, ma di troppo poco per valere il rischio
    pf_ex_top            3    0.2%  — regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge
    regime              22    1.7%  — in almeno un regime di mercato perde in modo conclamato

  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):
    oos_windows          4    0.3% delle bocciate
    consistency       1303   98.7% delle bocciate
    regime             933   70.7% delle bocciate
    total_return      1276   96.7% delle bocciate
    trades              11    0.8% delle bocciate
    pf_ex_top         1312   99.4% delle bocciate
    recovery          1304   98.8% delle bocciate
    win_rate           821   62.2% delle bocciate
    pf                1301   98.6% delle bocciate
    -> consistency, total_return, pf_ex_top, recovery, pf: presente in quasi TUTTE le bocciature. Non sta
       filtrando fra candidate, sta descrivendo il terreno in cui cerchiamo.

  QUASI-PASSAGGI (un solo criterio, mancato di poco): 1
    WUSDT|mean_reversion               manca   0.0% su holdout · PF 1.681 · 124 trade · t=2.313
    (sono i semi da cui il prossimo run fa mutare le candidate)

=== STRATEGIE GENERATE (discover) · 22 Sep 18:13 UTC ===
  129648 valutazioni · 277 passate (0.21%) · 129371 diagnosticate

  DOVE MUOIONO (criterio messo peggio):
    recovery         11129    8.6%  — la curva scava buche troppo profonde rispetto a quanto rende
    consistency       3357    2.6%  — guadagna in un periodo e perde negli altri: non e' un edge stabile
    regime           15204   11.8%  — in almeno un regime di mercato perde in modo conclamato
    trades            1920    1.5%  — pochi segnali: la strategia spara troppo poco su questo timeframe
    total_return     96008   74.2%  — profittevole, ma di troppo poco per valere il rischio
    pf_ex_top         1030    0.8%  — regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge
    holdout            723    0.6%  — funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento

  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):
    oos_windows        223    0.2% delle bocciate
    consistency     122639   94.8% delle bocciate
    holdout            723    0.6% delle bocciate
    total_return    115185   89.0% delle bocciate
    pf              118563   91.6% delle bocciate
    trades            6867    5.3% delle bocciate
    win_rate          2490    1.9% delle bocciate
    pf_ex_top       124381   96.1% delle bocciate
    recovery        122732   94.9% delle bocciate
    -> consistency, pf, pf_ex_top, recovery: presente in quasi TUTTE le bocciature. Non sta
       filtrando fra candidate, sta descrivendo il terreno in cui cerchiamo.

  QUASI-PASSAGGI (un solo criterio, mancato di poco): 40
    ADAUSDT|gen_4e6e1ae0               manca   0.0% su pf_ex_top · PF 1.405 · 166 trade · t=1.627
    IDUSDT|gen_4508a416                manca   0.0% su pf_ex_top · PF 1.481 · 109 trade · t=1.413
    IDUSDT|gen_addf82da                manca   0.0% su pf_ex_top · PF 1.481 · 109 trade · t=1.413
    CATIUSDT|gen_c647ead7              manca   0.1% su pf_ex_top · PF 1.576 · 82 trade · t=1.38
    XPINUSDT|gen_b2f350ff              manca   0.1% su recovery · PF 1.592 · 42 trade · t=1.206
    KASUSDT|gen_4c4dac5f               manca   0.1% su pf_ex_top · PF 1.586 · 87 trade · t=1.453
    KASUSDT|gen_cb4d9121               manca   0.1% su pf_ex_top · PF 1.586 · 87 trade · t=1.453
    SUSDT|gen_389461de                 manca   0.1% su pf_ex_top · PF 1.416 · 258 trade · t=2.069
    B2USDT|gen_1f7ead60                manca   0.2% su pf_ex_top · PF 1.394 · 65 trade · t=0.964
    B2USDT|gen_dfec940a                manca   0.2% su pf_ex_top · PF 1.394 · 65 trade · t=0.964
    (sono i semi da cui il prossimo run fa mutare le candidate)

  FERMATE SOLO DA pf_ex_top: 34 · miglior t = 2.07 · ne servirebbe 4.32 · le superano in 0
  La soglia NON e' il canonico 2: con 129648 test per run, a t=2 ci si aspettano
  ~2950 candidate per puro caso. 4.32 e' il valore che ne lascia
  passare al massimo una. Sotto quel livello 'pf_ex_top boccia un edge vero' non e'
  una conclusione che i dati sostengono — e' la stessa lotteria vista da un'altra
  angolazione.

COSA FARSENE. Il criterio dominante dice su cosa lavorare, e NON e' mai
'abbassare quella soglia': una soglia abbassata finche' qualcosa passa
seleziona esattamente il rumore che la soglia esisteva per escludere.
```
