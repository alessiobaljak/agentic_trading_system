# Programma 7 — cinquantaquattresima prova: il valore misurato con gli utenti, a settimana (VU)

Scritto il 28 ottobre 2026 alle 00:43 UTC (ora dell'orologio), **prima di scaricare i dati sugli utenti e prima di qualunque calcolo**.
Fino a qui si è contato solo quante monete hanno i dati. CoinMetrics community dà gratis gli indirizzi attivi e il valore di mercato per
92 monete, e 53 hanno un perpetuo su Binance. Nell'universo di ogni settimana ne entrano fra 16 e 38, 27 di mediana. È l'idea 85 della
coda, la prima della ricerca nella letteratura del 28 ottobre (`research/letture/letteratura_28ott2026.md`). È una prova a settimana.

## 1. Perché

* **Gli utenti sono il fondamentale di una moneta.** Una rete vale più se la usano in tanti. Se il prezzo corre oltre l'uso vero, è
  entusiasmo e poi rientra; chi compra la storia senza gli utenti paga troppo.
* **Cosa dice la letteratura**:
  * Liu, Tsyvinski e Wu 2021 (prezzo diviso per gli indirizzi nuovi): +1,9% a settimana fra i quartili, 2018-2021;
  * Liebi 2022, *Economic Modelling* (indirizzi attivi divisi per la capitalizzazione): +3,7 punti a settimana, 2017-2020;
  * Borri, Liu, Tsyvinski e Wu 2026, *Annual Review of Financial Economics*: la stessa direzione anche dal 2020.
* **La direzione scritta prima**: long le monete con più utenti attivi per dollaro di valore, short quelle con meno.
* **I dubbi scritti prima**:
  * i risultati pubblicati sono quasi tutti prima del 2021 e nelle monete piccole, mentre qui ci sono solo monete vecchie e grandi;
  * il valore di CoinMetrics conta tutte le monete create, non solo quelle in circolazione: per i gettoni con molte monete ancora
    bloccate il valore è più alto e la moneta sembra «cara»;
  * gli indirizzi attivi si possono gonfiare (operazioni automatiche, spam).

## 2. Dati e periodo (fissati qui)

* **Periodo**: dal 4 gennaio 2021 (l'inizio di F5 e G1, `sesta.INIZIO`) all'ultima settimana intera con i dati, fino al 19 ottobre 2026.
* **Universo**: ogni settimana, le monete delle 100 più scambiate (l'universo U di `terza.pannello_settimane`) che hanno i dati di
  CoinMetrics.
  * Le monete con i dati sono 92 su CoinMetrics community, e di queste 53 sono abbinate a un perpetuo con `annunci.perpetuo`; si
    scartano le sigle con il trattino basso, che sono le copie di un gettone su un'altra catena.
  * Almeno 20 monete con il segnale, altrimenti quella settimana nessuna posizione.
* **Dati**: `AdrActCnt` (indirizzi attivi del giorno) e `CapMrktCurUSD` (valore di mercato) di CoinMetrics community, giornalieri, salvati
  in `research/data/coinmetrics/` fuori da git.
* **Il segnale del lunedì l**: la media degli indirizzi attivi dai giorni l − 8 a l − 2, divisa per il valore di mercato del giorno l − 2.
  I due giorni di ritardo servono a non usare dati che il lunedì non erano ancora pubblicati.

## 3. La regola

* **I pesi**: come F5 (`ventiquattresima.pesi_banda`), con il segnale al posto del funding.
  * Long il quinto con più utenti per dollaro, short il quinto con meno.
  * Banda 20/40: una moneta già dentro resta finché non esce dal 40% del suo lato.
  * Pesi secondo l'inverso della volatilità dei 30 giorni, lati uguali in dollari.
* **Cambio delle posizioni**: ogni lunedì alle 00:00 UTC, con i costi a mercato e il funding (`terza.conto`).
* **Una prova a portafoglio**: nel conto delle prove diventano **211**.

## 4. L'esame

* **Come F5 e G1** (`terza.esame`, `terza.esito`): lo Sharpe corretto con l'aggiunta sopra la soglia 0,95, e il t dello Sharpe contro 3.
* **La regola del proprietario del 24 ottobre**: con lo Sharpe corretto da 0,90 in su, ogni anno positivo e il t sopra 3, non si boccia.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: il verso opposto; per anno; la correlazione con F5; quante monete hanno il segnale ogni
  settimana.
