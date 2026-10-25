# Programma 7 — trentaduesima prova: G1 neutra al mercato con l'interruttore sulle perdite (G1N-S)

Scritto il 25 ottobre 2026, alle 07:37 UTC, **prima di qualunque calcolo**. Idea 62 della coda di `research/REGISTRO.md`. Vale
`VENTISEIESIMA.md` (G1N, prova 88) e `TRENTUNESIMA.md` (l'interruttore, prova 93) dove qui non si dice altro.

## 1. Perché, e il dubbio

Le due protezioni misurate su G1 sono la neutralità al beta (prova 88: discesa massima da −28,8% a −23,1%, Sharpe 1,94 contro 1,96) e
l'interruttore sulle perdite (prova 93: −26,2% con Sharpe 1,98). Se si sommano, G1 avrebbe la discesa che serve per i soldi veri
(`docs/backlog.md`, P26) senza perdere rendimento. **Il dubbio scritto prima**: le due protezioni possono sovrapporsi: la neutralità
taglia proprio le settimane peggiori (i rally delle monete piccole), quindi sulla serie neutra l'interruttore potrebbe scattare meno
volte o in momenti diversi, e portare poco o niente. Probabilità media-bassa.

## 2. La regola (valori fissati qui)

* **G1N** come nella prova 88: i pesi giornalieri di G1 scalati perché la somma dei beta dei due lati (90 giorni prima, verso la media
  dell'universo del giorno) sia zero, con i limiti 0,5-1,5 sulla scalatura; ordini limite; dal 4 gennaio 2021 al 5 ottobre 2026.
* **L'interruttore** come nella prova 93, applicato al conto di G1N: il giorno d, se il conto a mercato alla fine di d−1 è sceso di almeno
  il **15%** dal massimo, pesi a zero per **7 giorni**, poi si riparte e il massimo si azzera al conto. Nessun altro valore.
* **Controllo**: G1N con lo stesso numero di pause di 7 giorni messe a caso (20 estrazioni, seme 2026), a mercato.
* Una prova nel conto (G1N-S): **164**.

## 3. L'esame e cosa si riporta

Come la 93: `terza.esame` dal 4 gennaio 2021, Sharpe corretto rivisto per gruppi, t, la regola del proprietario. G1N-S «aggiunge
qualcosa» a G1N se la discesa massima è minore di quella di G1N senza che lo Sharpe scenda sotto quello di G1N, e meglio delle pause a
caso; **le due protezioni si sommano** se la discesa di G1N-S è minore sia di quella di G1N (−23,1%) sia di quella di G1-S (−26,2%). Si
riportano: le pause (quante, quando, se coincidono con quelle della prova 93), cosa avrebbe fatto G1N nei giorni fermi, le 15 settimane
peggiori di G1 rifatte con G1N, G1-S e G1N-S, discesa e Sharpe a confronto fra le quattro versioni.
