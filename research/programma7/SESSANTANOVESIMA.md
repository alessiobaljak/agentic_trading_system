# Programma 7 — sessantanovesima prova: la diluizione, vendere le monete che stampano di più (DI)

Scritto il 29 ottobre 2026 alle 21:00 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 106 della coda: riapre l'idea
82 (scartata il 27 ottobre perché CoinMetrics non ha gli sblocchi), dopo che la ricerca nelle pubblicazioni del 29 ottobre ha trovato
che il file dei calendari degli sblocchi scaricato per la prova 74 contiene già l'offerta in circolazione giorno per giorno. Fino a qui
si è solo contato quanti calendari hanno un perpetuo (173), senza guardare nessun prezzo.

## 1. Perché

* **Chi compra una moneta con poca offerta in circolazione paga anche le monete che arriveranno.** La squadra, i fondi e chi ha
  ricevuto gli airdrop vendono man mano che le monete si sbloccano. È la famiglia che regge, «chi paga la novità perde», misurata
  sull'offerta invece che sull'età.
* **La fonte**: Guo, «Token Dilution and the Cross-Section of Cryptocurrency Returns» (SSRN 6636258, 2026; letto solo il riassunto):
  su 404 monete, 2020-2026, la diluizione delle 12 settimane e il rapporto fra valore diluito e valore in circolazione prevedono i
  rendimenti; l'effetto vive soprattutto nel primo anno di scambi. Binance Research (maggio 2024): le monete lanciate nel 2024 hanno in
  circolazione in media il 12,3% dell'offerta totale.
* **I dubbi scritti prima**:
  * la prova 74 (lo short prima dei singoli sblocchi a gradino) ha visto poco;
  * le monete che diluiscono di più sono spesso le più giovani: una parte è il calo delle monete nuove (N3), già noto;
  * **i calendari sono quelli di oggi** (DefiLlama): un progetto che ha cambiato il calendario dopo compare con quello nuovo. Il rischio
    è scritto qui, come per la prova 74;
  * le monete con il calendario e il perpetuo sono poche nel 2021-2022.

## 2. La regola (fissata qui)

* **Dati**: i calendari di DefiLlama in `research/data/sblocchi/sblocchi.json.gz` (fuori da git, gli stessi della prova 74), con
  l'offerta in circolazione di ogni giorno (le parti già sbloccate, senza quelle non in circolazione). La moneta si abbina al perpetuo
  con la sigla (`annunci.perpetuo`); si tiene solo se il prezzo di DefiLlama in un giorno di prova è entro il 20% del prezzo del
  perpetuo (come la prova 74).
* **DA, la diluizione**: ogni lunedì l, la crescita dell'offerta in circolazione dal giorno l − 86 al giorno l − 2 (12 settimane, due
  giorni di ritardo come la prova 116).
* **DB, l'offerta che resta da sbloccare**: ogni lunedì l, l'offerta finale del calendario divisa per quella in circolazione al giorno
  l − 2.
* **Il portafoglio**, per tutte e due, come F5 (`ventiquattresima.pesi_banda`): fra le monete dell'universo di G1 della settimana con il
  segnale, **short il quinto che diluisce di più, long il quinto che diluisce meno**, banda 20/40, pesi secondo l'inverso della
  volatilità, almeno 20 monete con il segnale (altrimenti la settimana è ferma); fuori le monete con il perpetuo nato da meno di 37
  giorni (i giorni della regola delle monete nuove). Costi a mercato e funding come F5 (`terza.conto`).
* **Periodo**: dal 4 gennaio 2021 (`sesta.INIZIO`) a fine settembre 2026.
* **Due varianti**: nel conto delle prove diventano **228**.

## 3. L'esame

* **Per ognuna, come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento): lo Sharpe corretto con
  l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre (corretto da 0,90, ogni anno positivo, t sopra 3).
* **Se una regge**, passa da un revisore separato.
* **Per capire, senza decidere niente**: quante monete hanno il segnale a settimana e quante settimane sono ferme; il segnale mescolato
  fra le monete della stessa settimana (20 volte); i due lati; per anno; la correlazione con F5; le monete con il perpetuo da meno di un
  anno contro le altre.
