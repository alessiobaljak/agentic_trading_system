# Programma 6 — dodicesima prova: denaro che entra, leva che costa poco (K1)

Scritto il 19 ottobre 2026, sera, **prima del calcolo**. Vale `OTTAVA.md` e `UNDICESIMA.md` dove qui non si dice altro.

## 1. Perché, e perché il passato qui non è una prova

* Fra le 100 monete più scambiate tre misure dicono cose coerenti: il **funding alto** (leva cara) rientra (F3, prova 8,
  verso scritto prima); gli **acquisti a mercato** (G1, prova 9) e la **crescita dell'interesse aperto** (P2, prova 11)
  vanno nel verso della moneta, al **contrario** di come li avevo scritti.
* Due versi su tre li ho visti dopo il calcolo. Quindi su 2022-2026 K1 è **costruzione**, non prova: il numero sul passato
  si riporta (e conta nello Sharpe corretto, prove **33**), ma **la prova vera di K1 è il paper**, sui dati dal 26 ottobre
  2026 (`paper/REGOLE.md`, con le stesse condizioni delle altre candidate).

## 2. La regola

* Ogni lunedì, fra le 100 monete dell'universo della terza prova, per ogni moneta tre ranghi fra −0,5 e +0,5:
  **−funding dei 7 giorni prima** (`sesta.py`), **+quota di acquisti a mercato dei 7 giorni prima** (`nona.py`, G1),
  **+crescita dell'interesse aperto dei 7 giorni prima** (`undicesima.py`, P2). Il segnale è la **media dei ranghi
  disponibili** (servono il funding e almeno uno degli altri due).
* Long il quinto con il segnale più alto, short il più basso; pesi secondo la volatilità dei 30 giorni prima; lato long +1
  e short −1; una settimana; costi e funding come la sesta prova.

## 3. Cosa si riporta

Sul passato dal 3 gennaio 2022 (i dati sulle posizioni partono da dicembre 2021): le sei condizioni della terza prova con
lo Sharpe corretto sulle 33 prove, **per informazione**. Poi K1 entra nel paper.
