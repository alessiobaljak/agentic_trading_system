# Programma 6 — undicesima prova: l'affollamento misurato con le posizioni

Scritto il 19 ottobre 2026, sera, **mentre si scaricano i dati e prima di qualunque calcolo** con essi
(`scarico_metrics.py`: i file `metrics` di Binance riassunti per giorno). Vale `OTTAVA.md` (pesi secondo la volatilità,
esame sulle 100 monete, conferma sulle 101-200) dove qui non si dice altro, con una differenza: i dati sulle posizioni ci
sono **dal dicembre 2021** e solo per le 100 monete dell'universo (per le 101-200 non sono stati scaricati), quindi
l'esame parte dal **3 gennaio 2022** e la conferma sulle monete 101-200 non si può fare: al suo posto c'è la condizione
della sezione 3.

## 1. Perché

* Le prove 6-9 dicono che fra le monete liquide l'affollamento si paga (il funding alto rientra), ma che il flusso degli
  acquisti a mercato anticipa il prezzo. Le posizioni dicono **chi** è affollato.
* Binance pubblica ogni 5 minuti: l'interesse aperto (il valore di tutte le posizioni aperte), il rapporto long/short delle
  **posizioni dei conti più grandi** e quello di **tutti i conti** (in numero di conti).
* Due idee con il verso deciso **prima**, dal perché economico:
  * **P1, grandi contro piccoli**: se i conti grandi sono più long, in proporzione, dei conti in generale, i grandi sanno
    qualcosa (o hanno più forza): si **segue** chi è più grande. Segnale = log(rapporto delle posizioni dei grandi) −
    log(rapporto dei conti di tutti), media dei 7 giorni prima. Long il quinto con il segnale più **alto**, short il più
    basso.
  * **P2, la leva che entra**: un interesse aperto che cresce molto in una settimana è leva nuova, cioè affollamento: si va
    **contro**. Segnale = log(interesse aperto in USDT alla fine della domenica) − log(lo stesso 7 giorni prima). Long il
    quinto con la crescita più **bassa**, short il più alto.
* Due prove: nel conto del programma 6 diventano **32**.

## 2. Le regole

Come l'ottava prova (ogni lunedì, le 100 monete più scambiate, quinti, pesi inversamente proporzionali alla volatilità dei
30 giorni, lato long +1 e short −1, una settimana, costi e funding come la sesta). Una moneta senza il dato della settimana
non entra.

## 3. L'esame

Sulle settimane dal **3 gennaio 2022** all'ultima completa: le sei condizioni della terza prova (`TERZA.md`, sezione 4) con
lo Sharpe corretto sulle **32** prove, gli anni 2022-2026 (almeno 4 su 5) e i trimestri pieni del 2022, 2023, 2024 e 2025.
Al posto della conferma sulle monete 101-200 (senza dati) si chiede che la variante sia **positiva sia nel 2022 sia
nell'ultimo anno** (dal 2025-10-01). **Valida** solo con tutto.
