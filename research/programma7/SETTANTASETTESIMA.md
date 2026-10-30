# Programma 7 — settantasettesima prova: i grandi gestori sul Bitcoin del CME (CF)

Scritto il 30 ottobre 2026 alle 16:23 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 113 della coda (dalla ricerca nelle
pubblicazioni del 29 ottobre). Fino a qui si è solo contato quanti rapporti settimanali ci sono sul Bitcoin del CME nell'archivio pubblico
della CFTC: 446.

## 1. Perché

* **Il rapporto settimanale della CFTC** («Traders in Financial Futures») divide le posizioni sui future del Bitcoin del CME fra
  intermediari, **gestori di patrimoni** (fondi pensione, fondi comuni, i fondi quotati), fondi a leva e gli altri. I gestori di patrimoni
  sono la domanda istituzionale vera, quella lenta.
* **L'ipotesi**: se i gestori aumentano la posizione netta in una settimana, la domanda istituzionale sta entrando e continua per qualche
  settimana; il Bitcoin dovrebbe salire nella settimana dopo.
* **I dubbi scritti prima**:
  * le fonti sono deboli (commenti, non studi);
  * i flussi dei fondi quotati (prova 99) inseguivano il prezzo e il giorno dopo il Bitcoin tornava un po' indietro;
  * le prove sul solo Bitcoin non hanno mai battuto il Bitcoin tenuto;
  * molti gestori sul CME sono l'altro lato delle operazioni dei fondi a leva (il carry fra CME e pronti), non scommesse sul prezzo.

## 2. La regola (fissata qui)

* **Dati**: l'archivio pubblico della CFTC (`publicreporting.cftc.gov`, rapporto «Traders in Financial Futures», solo future, codice del
  mercato 133741, Bitcoin del CME), salvato in `research/data/cftc/` fuori da git. Il rapporto fotografa il martedì ed esce il venerdì
  alle 15:30 di New York.
* **Il segnale**: la posizione netta dei gestori di patrimoni (long meno short) del martedì meno quella del martedì prima.
* **L'operazione**: dall'apertura (00:00 UTC) del **lunedì dopo l'uscita** del rapporto, per 7 giorni: **long** il perpetuo del Bitcoin
  se la posizione netta è salita, **short** se è scesa, fuori se è uguale. Costi a mercato del Bitcoin (`ventunesima.COSTO_BTC` diviso
  per due a ogni lato che si apre o si chiude) e funding.
* **Periodo**: dal 6 gennaio 2020 (il perpetuo nel pannello) al 28 settembre 2026.
* **Una variante**: nel conto delle prove diventano **237**.

## 3. L'esame

* **Come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento: deve dare qualcosa in più del Bitcoin
  tenuto): lo Sharpe corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **Se regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**: il Bitcoin tenuto; solo il lato long; il segnale dei fondi a leva al contrario; per anno; le
  settimane long e short.
