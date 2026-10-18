# E-002 — Reti di ordini limite sulla volatilità, periodo C

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezione 6bis). Solo periodo C
(2020-01-01 → 2022-12-31); le 12 monete del programma.

## Perché

Sfruttare la volatilità vuol dire anche **farsi prendere dal mercato agli estremi**: un ordine limite fermo molto sotto
(o sopra) il prezzo si esegue solo quando una vendita (o un acquisto) forzata attraversa il libro, cioè nei punti più
estremi delle code delle candele. Entrare lì costa meno (commissione da ordine limite, 0,02%, niente scarto) e parte da un
prezzo migliore della chiusura del minuto di un crollo, dove entravano I-001 e l'analisi dello scalping (rimbalzo +0,48% a
60 minuti dopo i crolli estremi, `research/scalping/risultati.md`). Il rischio è il contrario: farsi prendere proprio
quando il crollo è vero e continua (chi ci vende ha informazione). Lo dice il calcolo.

## La regola (per cella)

* All'inizio di ogni ora t si mette un ordine limite **d'acquisto** a `P·exp(−k·σ)` (o di **vendita** a `P·exp(+k·σ)`),
  con P la chiusura dell'ora prima e σ la deviazione standard dei rendimenti orari delle 720 ore prima (noti a quell'ora).
  L'ordine vale per l'ora; se non si esegue, si rimette all'ora dopo.
* **Esecuzione prudente**: solo se il prezzo **attraversa** il livello (minimo del minuto strettamente sotto il livello per
  l'acquisto, massimo strettamente sopra per la vendita); prezzo d'ingresso = il livello; commissione 0,02%, niente scarto.
* **Uscita** a mercato alla chiusura del minuto H dopo il minuto dell'esecuzione: commissione 0,05% e scarto del programma
  (doppio: si esce di solito in giornate agitate). Funding se il trade attraversa un regolamento.
* Dopo un'esecuzione, nessun ordine nuovo sulla stessa moneta e cella fino all'ora dopo l'uscita.
* **Contro il caso**: lordo meno la media, nella stessa moneta e nello stesso mese, del rendimento a H minuti (dall'apertura
  di un minuto alla chiusura del minuto H dopo) con lo stesso verso, su tutti i minuti.
* **Interesse aperto** (variante): al minuto dell'esecuzione, la variazione dell'interesse aperto dei 60 minuti prima (ultime
  rilevazioni note) nel 20% più basso («oi giù», posizioni chiuse: liquidazioni) o più alto («oi su») dei 30 giorni prima.

## Le celle (96, contando già i due versi)

Lato (acquisto sotto, vendita sopra) × k (2, 3, 4, 6) × H (15, 60, 240, 1.440 minuti) × interesse aperto (nessuna
condizione, oi giù, oi su). Il file `metrics` c'è da settembre 2020 per BTC e da dicembre 2021 per le altre: le celle con
l'interesse aperto hanno di fatto BTC 2020-2022 e le altre il 2022. Dichiarato.

## Statistica e criteri di promozione

Come E-001 (t per gruppi di giorni, per anno, per moneta). Costi di un giro qui: 0,02% + 0,05% + scarto (0,02-0,04%) =
0,09-0,11%, il doppio a costi doppi. Una cella è promossa se, tutto insieme:

1. lordo ≥ **0,25%** a trade e contro il caso ≥ **0,20%**;
2. lordo positivo in **ognuno degli anni** 2020, 2021, 2022 che hanno almeno 20 trade;
3. positivo su almeno il **70%** delle monete con almeno 10 trade, e almeno **6** monete;
4. t ≥ **3**;
5. almeno **100** trade.

Le celle promosse vicine (stesso lato) diventano **una** idea con al massimo 3 varianti, che passa dal motore a minuti del
programma con l'esecuzione prudente degli ordini limite (da aggiungere al motore, con test) e dall'esame di sempre.
