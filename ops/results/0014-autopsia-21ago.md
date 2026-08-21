# 0014-autopsia-21ago.req

_eseguito: 2026-08-21 04:58 UTC_

**richiesta:** `autopsy`
**eseguito:** `.venv/bin/python -m scripts.gate_autopsy`
**esito:** codice 0 in 1.1s

```
[firebase] connesso (Firestore + RTDB)

=== STRATEGIE BASE (optimize) · 21 Aug 03:40 UTC ===
  1144 valutazioni · 0 passate (0.00%) · 1144 diagnosticate

  DOVE MUOIONO (criterio messo peggio):
    regime              32    2.8%  — in almeno un regime di mercato perde in modo conclamato
    consistency         21    1.8%  — guadagna in un periodo e perde negli altri: non e' un edge stabile
    recovery            78    6.8%  — la curva scava buche troppo profonde rispetto a quanto rende
    total_return       991   86.6%  — profittevole, ma di troppo poco per valere il rischio
    trades               8    0.7%  — pochi segnali: la strategia spara troppo poco su questo timeframe
    pf_ex_top           12    1.0%  — regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge
    holdout              2    0.2%  — funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento

  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):
    total_return      1064   93.0% delle bocciate
    win_rate           719   62.8% delle bocciate
    trades              22    1.9% delle bocciate
    pf_ex_top         1135   99.2% delle bocciate
    consistency       1110   97.0% delle bocciate
    oos_windows          4    0.3% delle bocciate
    recovery          1122   98.1% delle bocciate
    holdout              2    0.2% delle bocciate
    regime             758   66.3% delle bocciate
    -> total_return, pf_ex_top, consistency, recovery, pf: presente in quasi TUTTE le bocciature. Non sta
       filtrando fra candidate, sta descrivendo il terreno in cui cerchiamo.

  QUASI-PASSAGGI (un solo criterio, mancato di poco): 3
    OPUSDT|mean_reversion              manca   8.5% su pf_ex_top · PF 1.537 · 269 trade · t=2.167
    FARTCOINUSDT|mean_reversion        manca   0.0% su holdout · PF 1.563 · 174 trade · t=1.788
    MUBARAKUSDT|mean_reversion         manca   0.0% su holdout · PF 4.447 · 47 trade · t=1.415
    (sono i semi da cui il prossimo run fa mutare le candidate)

  FERMATE SOLO DA pf_ex_top: 1 · miglior t = 2.17 · ne servirebbe 3.13 · le superano in 0
  La soglia NON e' il canonico 2: con 1144 test per run, a t=2 ci si aspettano
  ~26 candidate per puro caso. 3.13 e' il valore che ne lascia
  passare al massimo una. Sotto quel livello 'pf_ex_top boccia un edge vero' non e'
  una conclusione che i dati sostengono — e' la stessa lotteria vista da un'altra
  angolazione.

=== STRATEGIE GENERATE (discover) · 21 Aug 04:31 UTC ===
  35178 valutazioni · 25 passate (0.07%) · 35153 diagnosticate

  DOVE MUOIONO (criterio messo peggio):
    total_return     25404   72.3%  — profittevole, ma di troppo poco per valere il rischio
    pf_ex_top          557    1.6%  — regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge
    win_rate             2    0.0%  — vince troppo di rado perche' i guadagni ripaghino le perdite
    trades            1361    3.9%  — pochi segnali: la strategia spara troppo poco su questo timeframe
    consistency        704    2.0%  — guadagna in un periodo e perde negli altri: non e' un edge stabile
    recovery          2817    8.0%  — la curva scava buche troppo profonde rispetto a quanto rende
    holdout            119    0.3%  — funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento
    regime            4189   11.9%  — in almeno un regime di mercato perde in modo conclamato

  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):
    total_return     29921   85.1% delle bocciate
    win_rate         17662   50.2% delle bocciate
    pf_ex_top        34608   98.4% delle bocciate
    trades            2505    7.1% delle bocciate
    consistency      32368   92.1% delle bocciate
    oos_windows        387    1.1% delle bocciate
    recovery         32603   92.7% delle bocciate
    holdout            119    0.3% delle bocciate
    regime           26045   74.1% delle bocciate
    -> pf_ex_top, consistency, recovery, pf: presente in quasi TUTTE le bocciature. Non sta
       filtrando fra candidate, sta descrivendo il terreno in cui cerchiamo.

  QUASI-PASSAGGI (un solo criterio, mancato di poco): 40
    AEROUSDT|gen_43cef74b              manca   0.1% su pf_ex_top · PF 1.369 · 130 trade · t=1.44
    TREEUSDT|gen_1705084b              manca   0.2% su recovery · PF 1.816 · 31 trade · t=0.968
    AEROUSDT|gen_1837e26a              manca   0.4% su recovery · PF 1.472 · 33 trade · t=0.974
    ORDIUSDT|gen_a640dfa5              manca   0.5% su pf_ex_top · PF 1.453 · 126 trade · t=1.629
    QTUMUSDT|gen_96c1ed1b              manca   0.7% su pf_ex_top · PF 1.721 · 196 trade · t=2.177
    REDUSDT|gen_8dfa2442               manca   1.0% su pf_ex_top · PF 1.572 · 85 trade · t=1.404
    HEIUSDT|gen_e6ddc613               manca   1.1% su pf_ex_top · PF 2.32 · 86 trade · t=1.31
    1000LUNCUSDT|gen_43cef74b          manca   1.2% su pf_ex_top · PF 1.52 · 204 trade · t=2.154
    USELESSUSDT|gen_ddb3def9           manca   1.4% su recovery · PF 1.268 · 76 trade · t=0.916
    MUBARAKUSDT|gen_fb7d035a           manca   1.6% su pf_ex_top · PF 1.388 · 187 trade · t=1.743
    (sono i semi da cui il prossimo run fa mutare le candidate)

  FERMATE SOLO DA pf_ex_top: 29 · miglior t = 2.66 · ne servirebbe 4.03 · le superano in 0
  La soglia NON e' il canonico 2: con 35178 test per run, a t=2 ci si aspettano
  ~800 candidate per puro caso. 4.03 e' il valore che ne lascia
  passare al massimo una. Sotto quel livello 'pf_ex_top boccia un edge vero' non e'
  una conclusione che i dati sostengono — e' la stessa lotteria vista da un'altra
  angolazione.

COSA FARSENE. Il criterio dominante dice su cosa lavorare, e NON e' mai
'abbassare quella soglia': una soglia abbassata finche' qualcosa passa
seleziona esattamente il rumore che la soglia esisteva per escludere.
```
