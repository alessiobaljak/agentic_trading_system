# Programma 7 — settantaseiesima prova: quanto i giornali crypto parlano di una moneta (GA)

Scritto il 30 ottobre 2026 alle 12:24 UTC (ora dell'orologio), **prima di qualunque calcolo sui prezzi**. È l'idea 115 della coda, nata
da una domanda del proprietario («recupero di info da siti di informazioni che trattano argomenti di crypto [...] valutare quali crypto
comprare per poi tenere per xx settimane o mesi»). Fino a qui si sono solo contati gli articoli: 229.172 dal 29 ottobre 2019 al 1° febbraio
2025, 127 monete con il perpetuo citate almeno una volta, ogni mese in mediana 63 con almeno un articolo e 28 con almeno cinque.

## 1. Perché

* **Chi compra quello di cui parlano tutti paga troppo.** È la famiglia che regge nei nostri conti (la vendita delle monete appena quotate,
  l'effetto Coinbase): l'attenzione porta compratori che non guardano il prezzo, e il prezzo poi torna indietro.
* **Nelle azioni**: Fang e Peress («Media Coverage and the Cross-section of Stock Returns», *Journal of Finance*, 2009) trovano che le
  azioni senza articoli sui giornali rendono più di quelle molto citate; Barber e Odean (2008) che i piccoli risparmiatori comprano le
  azioni che attirano l'attenzione.
* **Si tiene per settimane**, come F5: si decide il lunedì, e con la banda una moneta resta dentro in media qualche settimana.
* **I dubbi scritti prima**:
  * le monete grandi (Bitcoin, Ether) sono sempre sui giornali: per questo si misura l'attenzione rispetto alla moneta stessa (variante
    GA1) o rispetto al volume (variante GA2);
  * l'archivio raccoglie fonti diverse nel tempo (da 83 a 13.110 articoli al mese): per questo si conta la quota della moneta sul totale
    del periodo, non il numero;
  * l'attenzione può anche essere notizia vera (una partnership, un aggiornamento) e far salire il prezzo per settimane: la prova 9 e la
    prova 22 hanno trovato che la domanda che entra a volte continua;
  * l'archivio finisce il 1° febbraio 2025: mancano gli ultimi 20 mesi.

## 2. La regola (fissata qui)

* **Dati**: l'archivio pubblico degli articoli raccolti da CoinDesk Data tramite CryptoCompare (Hugging Face,
  `maryamfakhari/crypto-news-coindesk-2020-2025`, licenza per la ricerca), salvato in `research/data/notizie_coindesk/` fuori da git. Una
  moneta è citata in un articolo se la sua sigla è nelle categorie dell'articolo (il campo `categories`, assegnato dalla fonte); la sigla si
  abbina al perpetuo di Binance con `annunci.perpetuo`.
* **Il ritardo**: la decisione del lunedì l usa solo gli articoli pubblicati fino alla fine del giorno l − 2 (un giorno di margine).
* **GA1, l'attenzione che sale**: per ogni moneta, la quota degli articoli dei 28 giorni prima che la citano diviso la quota negli 84 giorni
  ancora prima, in logaritmo, con 1 articolo in più sopra per non dividere per zero: log((n28 + 1) / N28) − log((n84 + 1) / N84).
* **GA2, l'attenzione per dollaro scambiato**: il numero degli articoli dei 28 giorni prima (più uno) diviso il volume in dollari del
  perpetuo negli stessi giorni, in logaritmo.
* **Il portafoglio, per tutte e due, come F5** (`ventiquattresima.pesi_banda`): fra le monete dell'universo di G1 della settimana con
  almeno 3 articoli nei 112 giorni prima, **short il quinto con l'attenzione più alta, long il quinto con la più bassa**, banda 20/40, pesi
  secondo l'inverso della volatilità, almeno 20 monete (altrimenti la settimana è ferma); costi a mercato e funding come F5
  (`terza.conto`).
* **Periodo**: dal 4 gennaio 2021 (`sesta.INIZIO`) al 27 gennaio 2025 (l'ultimo lunedì con i 28 giorni di articoli dentro l'archivio).
* **Due varianti**: nel conto delle prove diventano **236**.

## 3. L'esame

* **Per ognuna, come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento; anni pieni 2021-2024): lo
  Sharpe corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **Se una regge**, passa da un revisore separato; poi, siccome l'archivio finisce nel 2025, serve una fonte di articoli per i mesi dopo
  prima di qualunque paper.
* **Per capire, senza decidere niente**: quante monete hanno il segnale a settimana e quante settimane sono ferme; il segnale mescolato fra
  le monete della stessa settimana (20 volte); i due lati; per anno; la correlazione con F5; il verso opposto.
