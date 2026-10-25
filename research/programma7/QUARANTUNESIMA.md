# Programma 7 — quarantunesima prova: i tagli della leva massima annunciati da Binance (LV)

Scritto il 25 ottobre 2026, alle 08:46 UTC, **prima di leggere le tabelle e prima di qualunque calcolo sui prezzi**. Idea 73 della coda
di `research/REGISTRO.md`. Il controllo di fattibilità ha guardato solo la forma: l'archivio delle notizie di Binance dà 217 annunci sui
margini dei perpetui con il codice dell'articolo; il testo di ogni annuncio ha, per ogni contratto (o gruppo di contratti), la tabella
«prima» e «dopo» con la leva massima della prima fascia e l'ora in cui il cambio vale. Nessun prezzo guardato.

## 1. Perché, e il dubbio

Quando Binance taglia la leva massima di un contratto, chi tiene posizioni a leva alta deve aggiungere margine o ridurre, e i nuovi
ingressi a leva alta spariscono: chi paga la leva (i long affollati) viene costretto a uscire, la stessa famiglia di F5 e G1 ma come evento
datato e annunciato prima. **Il dubbio scritto prima**: Binance taglia la leva dopo che una moneta si è agitata (spesso dopo una fiammata:
il ritorno indietro sarebbe quello delle prove 75-78, non l'effetto della leva); molti tagli riguardano solo le posizioni nuove («existing
positions will not be affected»); dal 2024 i cambi sono settimanali e di routine. Probabilità bassa-media.

## 2. La regola (valori fissati qui)

* **Eventi**: i 217 annunci della sezione notizie (catalogo 49) con «leverage and margin tiers», «margin tiers» o «adjust … leverage» nel
  titolo. In ogni testo, ogni riga che nomina contratti `…USDT` seguita da «(USDⓈ-M Perpetual Contract/Contracts)» apre un gruppo; la
  **leva massima prima** è il numero più alto della prima riga «Leverage Before Change», la **leva massima dopo** quello della prima riga
  «Leverage After Change» della tabella che segue; l'**ora del cambio** è l'ultima data «AAAA-MM-GG HH:MM (UTC)» scritta prima della riga
  dei contratti, altrimenti la prima data del testo, altrimenti l'ora dell'annuncio. Un evento per contratto e ora del cambio (i doppioni
  si tengono una volta). **Taglio** = leva dopo minore di leva prima.
* **Ammessi**: i contratti del nostro pannello, Bitcoin escluso (è la copertura), con volume sopra zero il giorno prima dell'entrata.
* **Operazione** (sui tagli): **short la moneta e long il Bitcoin** per lo stesso valore, entrata all'apertura della prima ora intera dopo
  l'annuncio; uscita all'apertura di **72 ore dopo l'ora del cambio** (se il cambio è prima dell'entrata, 72 ore dopo l'entrata); candele
  orarie dei perpetui; costi come la regola delle monete nuove (`vu.COSTO_MONETA + vu.COSTO_BTC`), funding giornaliero vero dei due lati.
* **Descrittivo, non nel conto**: gli aumenti di leva (la stessa operazione, per confronto), la grandezza del taglio, la frase sulle
  posizioni esistenti.
* Una prova a eventi: nel conto **173**, le prove a eventi **29**.

## 3. L'esame

Come la regola delle monete nuove (`trentesima.esame`, bootstrap per annuncio): media sopra zero con **p ≤ 0,01**, positiva nelle due metà
e senza i 5 migliori; contando le 29 prove a eventi la soglia è 0,00034. Si riportano per anno, la quota vinta, e gli aumenti accanto.
