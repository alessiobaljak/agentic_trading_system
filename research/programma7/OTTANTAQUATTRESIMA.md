# Programma 7 — ottantaquattresima prova: vendere dopo un attacco informatico al protocollo (AT)

Scritto il 1° novembre 2026 alle 00:22 UTC (ora dell'orologio), **prima di qualunque calcolo sui prezzi**. È l'idea 128 della coda:
riapre l'idea 93 (scartata perché lo studio aveva solo 22 casi) con una fonte nuova, l'elenco pubblico degli attacchi di DefiLlama
(`api.llama.fi/hacks`, scaricato il 1° novembre 2026: 1.333 attacchi). Fino a qui si sono solo contati gli eventi abbinabili a un
perpetuo di Binance (78 dal 2020, mediana 3 milioni di dollari rubati), senza guardare nessun prezzo.

## 1. Perché

* **Dopo un attacco la gente se ne va piano.** Il giorno dell'attacco il prezzo del gettone del protocollo crolla, ma i depositi escono
  per giorni, si scopre quanto è stato preso davvero, si discute di rimborsi e di voti: chi tiene il gettone vende a rate. Se il prezzo
  reagisce in ritardo, la discesa continua nella settimana dopo.
* **È un'informazione diversa dai prezzi** messa insieme ai prezzi (il proprietario: «leggere informazioni diverse e metterle insieme»),
  e un evento di tipo nuovo per noi.
* **I dubbi scritti prima**:
  * la data di DefiLlama è il giorno, non l'ora: l'attacco può essere delle 23 e la notizia del giorno dopo, quindi si entra solo
    all'apertura del **secondo** giorno (g + 1, dove g è il giorno dell'attacco);
  * dopo il crollo può arrivare il rimbalzo (fondi restituiti, rimborsi): il verso potrebbe essere l'opposto;
  * gli eventi sono pochi (78 prima del controllo dei prezzi), quindi la soglia di tutte le prove a eventi sarà difficile da passare;
  * l'abbinamento fra protocollo e gettone passa dalla sigla: per questo c'è il controllo del prezzo qui sotto.

## 2. La regola (fissata qui)

* **Gli eventi**: gli attacchi dell'elenco di DefiLlama dal 4 gennaio 2021 al 20 settembre 2026; il protocollo (`defillamaId`) dà la
  sigla e l'identificativo di CoinGecko (`api.llama.fi/protocols`); la sigla si abbina al perpetuo di Binance con `annunci.perpetuo`; il
  perpetuo deve esistere da almeno 30 giorni prima dell'attacco. Fuori il Bitcoin.
* **Il controllo del prezzo**: il prezzo di CoinGecko del gettone il giorno dell'attacco (servizio storico dei prezzi di DefiLlama,
  `coingecko:<id>`) deve stare entro il 20% della chiusura del perpetuo dello stesso giorno (diviso il multiplo, come 1000PEPE); senza
  l'identificativo o senza il prezzo l'evento resta fuori.
* **Un evento per moneta ogni 14 giorni** (gli attacchi ripetuti allo stesso protocollo si contano una volta).
* **L'operazione** (come le prove 105 e 140, `quarantatreesima.operazione`): short il perpetuo della moneta e long il Bitcoin per lo
  stesso valore dall'apertura del giorno g + 1, uscita a +30% contro (massimo orario) o dopo 7 giorni; costi a mercato e funding.
* **Il controllo**: le stesse monete in 20 giorni a caso fra 60 e 365 giorni dopo l'attacco (fuori dai 14 giorni di altri attacchi); la
  differenza fra eventi e controllo, moneta per moneta.
* **Una prova a eventi**: nel conto delle prove diventano **244**, e le prove a eventi **45**.

## 3. L'esame (scritto prima)

* Lo stesso delle prove a eventi (`trentesima.esame`): media sopra zero con p ≤ 0,01, le due metà positive, positiva anche senza le 5
  migliori; in più la differenza con il controllo con p ≤ 0,05; **valida** solo con p sotto 0,01 diviso le 45 prove a eventi.
* **Per capire, senza decidere niente**: il crollo già fatto dal giorno dell'attacco all'entrata (contro il Bitcoin); gli attacchi sopra i
  10 milioni di dollari da soli; le tenute di 3 e di 14 giorni.
