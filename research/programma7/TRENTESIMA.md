# Programma 7 — trentesima prova: il clima del mercato come regolatore di G1 e F5

Scritto il 25 ottobre 2026, alle 07:18 UTC, **prima di qualunque calcolo**. Idea 60 della coda di `research/REGISTRO.md`. Vale
`PRIMA.md` (G1) e `programma6/QUARANTUNESIMA.md` (F5) dove qui non si dice altro.

## 1. Perché

Nessuna prova finora ha modulato l'esposizione di G1 o di F5 con una misura del **mercato intero**: la 45 usa solo il funding medio,
la 86 e la 88 solo il beta dei due lati. La skill «crypto-regime-analyzer» (installata il 25 ottobre, MIT) riassume il clima in un
punteggio da 0 a 100 con sei ingredienti; cinque si ricostruiscono giorno per giorno dal nostro pannello senza dati nuovi (il peso di
Bitcoin sul totale no: non abbiamo le capitalizzazioni). La skill stessa dice che le soglie sono «euristiche scelte per la leggibilità,
non ottimizzate»: qui si prendono **com'è scritte nel suo metodo**, non si cercano. **La riserva, scritta prima**: G1 e F5 sono
long/short e quasi neutre al mercato; è probabile che il clima non cambi il loro rendimento e che il regolatore tolga solo metà
esposizione nei giorni di paura, cioè rendimento. Probabilità bassa-media.

## 2. Il punteggio del clima (valori fissati qui, copiati dal metodo della skill)

Si calcola **ogni giorno alle 00:00 UTC con i dati fino alla chiusura del giorno prima** (nessuno sguardo al futuro). Universo:
quello del giorno di G1 (le 100 del lunedì della settimana).

| Ingrediente | Peso | Regola |
|---|---|---|
| Tendenza di Bitcoin | 25 | prezzo, media a 50 e a 200 giorni: prezzo > m50 > m200 → 90; m200 < prezzo < m50 con m50 > m200 → 65; prezzo sotto entrambe con m50 > m200 → 55; prezzo > m50 con m50 ≤ m200 → 45; prezzo < m50 < m200 → 15. Più la pendenza della m200 sui 20 giorni prima: > +0,5% → +10, < −0,5% → −10 (la fascia piatta ±0,5% la fisso io: la skill dice «salita/piatta/discesa» senza numero). Fra 0 e 100. |
| Ampiezza delle monete minori | 20 | quota dell'universo (senza Bitcoin, monete con almeno 200 chiusure) sopra la media a 200 giorni: ≥ 80% → 95, ≥ 65% → 80, ≥ 50% → 65, ≥ 35% → 45, ≥ 20% → 25, altrimenti 10. Se la quota sopra la m50 supera quella sopra la m200 di 15 punti o più → +5; se è sotto di 15 o più → −5. Servono almeno 5 monete. |
| Funding dei perpetui | 15 | media sull'universo del funding del giorno prima diviso 3 (equivalente a 8 ore): ≤ −0,010% → 80; fino a 0 → 65; fino a +0,010% → 75; fino a +0,030% → 55; fino a +0,060% → 30; oltre → 10. Servono almeno 2 monete. |
| Discesa e volatilità di Bitcoin | 15 | discesa dal massimo dei 365 giorni prima: ≤ 10% → 90, ≤ 20% → 75, ≤ 35% → 55, ≤ 50% → 35, ≤ 65% → 20, oltre → 10. Volatilità a 30 giorni (rendimenti logaritmici, annualizzata) rispetto ai suoi 52 valori settimanali dell'anno prima: terzo basso → +10, terzo alto → −10; se la discesa supera il 65% e la volatilità è nel terzo alto, il punteggio non scende sotto 15. |
| Slancio a 30 giorni | 10 | quota dell'universo (con Bitcoin) con il prezzo sopra quello di 30 giorni prima: ≥ 85% → 90, ≥ 65% → 75, ≥ 45% → 55, ≥ 25% → 35, ≥ 10% → 20, sotto il 10% → 35 (resa, controcorrente). Servono almeno 5 monete. |

Il punteggio è la media pesata degli ingredienti disponibili, con i pesi ridistribuiti in proporzione (la convenzione della skill);
il peso di Bitcoin sul totale manca sempre, quindi di norma si divide per 85. Se i pesi disponibili sono meno di 55 (il 65% di 85) il
punteggio **manca** e quel giorno il regolatore non agisce (esposizione piena); i giorni mancanti si contano.

## 3. Il regolatore (una sola soglia, fissata qui)

* Punteggio **≥ 40** (le fasce «neutra» e «propensa» della skill) → esposizione piena, pesi di G1 o F5 come sono.
* Punteggio **< 40** (la fascia «avversa» della skill) → **tutti i pesi × 0,5**, long e short insieme.
* Per G1 il punteggio è quello del giorno; per F5 è quello del lunedì (dati fino alla domenica) e vale per tutta la settimana.
* Tutto il resto identico a G1 (`prima.py`: banda 20/40, pesi 1/volatilità, ordini limite, funding vero, dal 4 gennaio 2021 al 5 ottobre
  2026) e a F5 (`programma7/ventiquattresima.py`, serie «F5»).
* Due serie nel conto: **G1 clima** e **F5 clima**: nel conto diventano **162**.

## 4. L'esame

Come la 88: `terza.esame` dal 4 gennaio 2021, Sharpe corretto con l'aggiunta e il t, la decisione del proprietario del 24 ottobre;
confronto con G1 e con F5 sulle stesse settimane (Sharpe, discesa massima, rendimento l'anno). **Si decide sullo Sharpe corretto e sulla
discesa insieme**: il regolatore vale se non abbassa lo Sharpe e taglia la discesa, come per la neutralità. Dopo, per capire: quanti
giorni in ogni fascia, il rendimento netto di G1 e di F5 nei giorni «avversi» contro gli altri (descrittivo, non decide), la
correlazione fra la serie regolata e quella di base.
