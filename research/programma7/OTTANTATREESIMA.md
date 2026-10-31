# Programma 7 — ottantatreesima prova: le notizie nuove contro le notizie ripetute (NV)

Scritto il 31 ottobre 2026 alle 20:22 UTC (ora dell'orologio), **prima di qualunque calcolo sui prezzi e sui testi**. È l'idea 127 della
coda, scritta oggi dalla ricerca nelle pubblicazioni del 2026. Usa lo stesso archivio degli articoli della prova 138 (GA), di cui finora
si sono usati solo le date e le monete citate, mai i testi.

## 1. Perché

* **Le notizie ripetute muovono il prezzo più del dovuto, quelle nuove meno.** Tetlock («All the News That's Fit to Reprint», *Review of
  Financial Studies*, 2011): nelle azioni, chi compra sulle notizie già uscite (ripetute da altri giornali o riscritte) esagera, e il
  prezzo poi torna indietro; le notizie davvero nuove portano informazione e il prezzo continua nella loro direzione.
* **Nelle monete**: Chu e Tsiakas («Media Coverage and the Cross-Section of Cryptocurrency Returns», SSRN 6805101, maggio 2026; **letto
  solo il breve riassunto dei risultati di una ricerca**): l'ampiezza della copertura passa per l'attenzione e prevede rendimenti più
  bassi, la novità delle notizie passa per l'informazione e prevede rendimenti più alti.
* **Che cosa abbiamo già**: la prova 138 ha misurato quanto si parla di una moneta (l'ampiezza): GA1, l'attenzione che sale, ha fatto
  −0,07. La novità non è mai stata misurata.
* **I dubbi scritti prima**:
  * l'archivio cambia nel tempo (da 83 a 13.110 articoli al mese) e ha molte fonti che riprendono la stessa storia: per questo il
    confronto si fa solo con gli articoli dei **giorni prima** (non dello stesso giorno), e sempre con lo stesso numero di articoli;
  * le monete grandi hanno più articoli e più ripetizioni: il segnale può diventare una scommessa sulle piccole contro le grandi (la
    prova 49 l'ha già bocciata); si misura e si scrive la correlazione fra il segnale e il volume;
  * l'archivio finisce il 1° febbraio 2025, quindi la prova va dal 2021 al gennaio 2025 come la 138;
  * il testo è il titolo più il riassunto dato dalla fonte, non l'articolo intero.

## 2. La regola (fissata qui)

* **Dati**: `research/data/notizie_coindesk/coindesk.csv` (fuori da git), le monete citate e l'abbinamento ai perpetui come la prova 138
  (il campo `categories`, `annunci.perpetuo`).
* **Il testo di un articolo**: titolo e riassunto (`title`, `body`), con i caratteri speciali dell'HTML tradotti, in minuscolo; parole
  singole e coppie di parole senza le parole comuni dell'inglese, contate con una tabella fissa (`HashingVectorizer` di scikit-learn,
  2^20 caselle, nessun vocabolario imparato dai dati, quindi nessuna informazione dal futuro), vettore di lunghezza 1.
* **Quanto è ripetuto un articolo per una moneta** (Tetlock 2011): la somiglianza più alta (coseno) fra il suo testo e quello dei **20
  articoli precedenti sulla stessa moneta pubblicati nei giorni prima** (dal giorno prima fino a 90 giorni prima). Se ce ne sono meno di 5,
  l'articolo non conta. **La novità** = 1 − la somiglianza più alta.
* **Il segnale del lunedì l**: la media della novità degli articoli sulla moneta pubblicati nei 28 giorni fino alla fine del giorno l − 2
  (un giorno di margine, come la prova 138); servono **almeno 3 articoli** che contano.
* **Il portafoglio, come F5** (`ventiquattresima.pesi_banda`): fra le monete dell'universo della settimana con il segnale, **long il
  quinto con le notizie più nuove, short il quinto con le più ripetute**, banda 20/40, pesi secondo l'inverso della volatilità, almeno 20
  monete (altrimenti la settimana è ferma); costi a mercato e funding come F5 (`terza.conto`).
* **Periodo**: dal 4 gennaio 2021 al 27 gennaio 2025, con l'esame adattato alla fine dell'archivio come nella prova 138.
* **Una prova**: nel conto delle prove diventano **243**.

## 3. L'esame (scritto prima)

* Lo stesso delle prove a portafoglio (`terza.esame`, `terza.esito`), sugli anni pieni 2021-2024, con lo Sharpe corretto rivisto per
  tutte le prove (`asticella.corretto_rivisto`) e la regola del proprietario del 24 ottobre.
* **Il controllo del segnale mescolato**: 20 volte, il segnale si rimescola a caso fra le monete della stessa settimana; lo Sharpe vero
  deve stare sopra almeno 19 dei 20.
* **Per capire, senza decidere niente**: il verso opposto; la correlazione di rango media fra il segnale e il volume dei 28 giorni; quante
  monete hanno il segnale a settimana; la correlazione con F5.
* **Se passa**, i dati recenti non ci sono (l'archivio finisce a gennaio 2025): la prova in avanti si fa con le notizie che raccogliamo
  dal 30 ottobre 2026 (`research/notizie/`), con la stessa regola.
