# Programma 7 — trentacinquesima prova: la vendita coperta del funding su Binance (CC)

Scritto il 25 ottobre 2026, alle 07:55 UTC, **prima di scaricare i prezzi a pronti e prima di qualunque calcolo**. Idea 65 della coda di
`research/REGISTRO.md`. Il controllo di fattibilità fatto prima ha contato soltanto: nel lato venduto di F5 (i pesi dipendono da funding,
volume e volatilità, non dai rendimenti) entrano nel tempo 373 monete, in media 21,8 a settimana su 354 settimane; i prezzi a pronti
giornalieri stanno sull'archivio pubblico di Binance (file mensili, dal 2020). Nessun rendimento guardato.

## 1. Perché, e il dubbio

Il lato venduto di F5 incassa il funding delle monete dove i long sono affollati: è il pezzo più sicuro di «chi paga la leva perde», ma da
solo ha il rischio del prezzo. Coprendolo con l'acquisto a pronti della stessa moneta per lo stesso valore, il prezzo si annulla e resta
**il funding meno i costi, più le variazioni della base** (quanto il perpetuo si scosta dal pronti). È il modo di raccogliere il funding
senza direzione, con una discesa che per costruzione dovrebbe essere piccola; nel 2021-2026 il funding incassato da F5 vale circa il 45%
del suo netto (prova 89). **Il dubbio scritto prima**: le commissioni a pronti sono più alte di quelle dei perpetui e si pagano su un
secondo giro; la base può muoversi contro per settimane; molte monete piccole non hanno il pronti su Binance (restano fuori); e non è
trading nel senso del proprietario (lo accetta solo se profittevole). Probabilità media per il segno, bassa per il rendimento.

## 2. La regola (valori fissati qui)

* **Il lato venduto di F5**, identico (`programma6/ventiquattresima.pesi_banda` sul funding dei 7 giorni, banda 20/40, pesi inversi alla
  volatilità): ogni lunedì i pesi negativi, normalizzati a somma 1 del valore nozionale. **Ogni moneta venduta sul perpetuo è comprata a
  pronti per lo stesso valore** (coppia `BASE USDT` a pronti; i perpetui con il prefisso 1000, 1000000 o 1M corrispondono alla base senza
  prefisso). Le monete senza il pronti su Binance quella settimana restano fuori da entrambe le gambe, e la quota del nozionale che resta
  fuori si riporta (non si ridistribuisce).
* **Conto della settimana, per unità di nozionale**: somma sui pesi di [rendimento a pronti − rendimento del perpetuo + funding incassato]
  (rendimenti da apertura del lunedì ad apertura del lunedì dopo, i file giornalieri), meno i costi del giro: sul perpetuo il costo delle
  monete di `seconda.costi_moneta`, a pronti **0,15% per lato** (0,10% di commissione più 0,05% di scarto), sul cambio dei pesi da una
  settimana all'altra (senza la deriva dei pesi col prezzo, per semplicità: dichiarato).
* **Capitale**: il nozionale a pronti più il margine del perpetuo a leva 2 (metà del nozionale): **1,5 volte il nozionale**. Il rendimento
  si riporta per capitale (il numero che conta) e per nozionale.
* **Periodo**: dal 4 gennaio 2021 al 5 ottobre 2026, come F5. Nessuna variante, nessun parametro nuovo oltre il costo a pronti.
* Una prova nel conto (CC): **167**.

## 3. L'esame e cosa si riporta

`terza.esame` sulla serie settimanale per capitale dal 4 gennaio 2021 (anni pieni 2021-2025), Sharpe corretto rivisto per gruppi e t,
`terza.esito`, la regola del proprietario del 24 ottobre. Si riportano per anno: funding incassato, variazione della base, costi, quota del
nozionale senza pronti, discesa massima; e il confronto con il lato venduto di F5 scoperto (lo stesso lato senza la copertura).
