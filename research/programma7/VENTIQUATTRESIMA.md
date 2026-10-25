# Programma 7 — ventiquattresima prova: F5 neutra al mercato (F5N)

Scritto il 25 ottobre 2026, alle 05:10 UTC, **prima di qualunque calcolo**. Idea 49 della coda di `research/REGISTRO.md`. Vale
`programma6/VENTIQUATTRESIMA.md` (F5) dove qui non si dice altro.

## 1. Perché, e la riserva

F5 ha i due lati uguali in dollari. Il controllo `programma6/PERDITE_F5.md` (25 ottobre) ha mostrato che nelle 15 settimane
peggiori il lato venduto (le monete con i long affollati) sale più della media del mercato (short −13,7%, long +5,8%): il
portafoglio è esposto negativamente al mercato nei rally. Rendere il portafoglio **neutro al beta** (non solo ai dollari) è la pratica
normale dei portafogli fra monete e non è un parametro cercato; il beta si stima prima, sui 90 giorni precedenti. **La riserva
scritta prima**: l'idea è nata guardando le settimane peggiori sui dati di tutti gli anni usati; il beta stimato su 90 giorni è
rumoroso; e il lato long di F5 è il più redditizio (+42,8% l'anno): pesarlo di più potrebbe migliorare F5 per questo e non per la
neutralità. Per questo si riporta anche la versione «lato long sempre al 120% e short all'80%» (il peso fisso, senza beta): se F5N
non fa meglio di quella, il merito non è della neutralità.

## 2. La regola (valori fissati qui)

* Segnale, universo, banda 20/40 e pesi 1/volatilità dentro ogni lato: **identici a F5** (`ventiquattresima.pesi_banda`).
* **Beta di ogni moneta**: la pendenza dei suoi rendimenti giornalieri sulla media giornaliera dell'universo della settimana, sui
  **90 giorni** prima del lunedì (almeno 45 con tutti e due i dati); se manca, beta = 1.
* **Scalatura dei lati**: βL = media dei beta del lato long pesata con i pesi di F5, βS lo stesso per lo short; il lato long si
  moltiplica per a = 2·βS / (βL + βS) e lo short per b = 2·βL / (βL + βS), così la somma dei beta pesati è zero e l'esposizione lorda
  resta il 200% come F5; **a e b fra 0,5 e 1,5** (limite di sicurezza contro i beta rumorosi, fissato qui). Se βL + βS ≤ 0, a = b = 1.
* Costi e funding come F5 (a mercato, `seconda.costi_moneta`); dal 4 gennaio 2021.
* Due serie nel conto: **F5N** e il **peso fisso 120/80** (controllo): nel conto diventano **153**.

## 3. L'esame

`terza.esame` dal 4 gennaio 2021 (anni pieni 2021-2025), Sharpe corretto con l'aggiunta e il t, confronto con F5 sulle stesse
settimane (Sharpe 1,868 con le parità corrette) e con il peso fisso; la decisione del proprietario del 24 ottobre (da 0,90, ogni anno
positiva, t sopra 3). Si riportano anche βL e βS medi, a e b medi, e le 15 settimane peggiori di F5 rifatte con F5N.
