# Programma 7 — quarantacinquesima prova: vendere i perpetui annunciati in chiusura, con le date vere (G13C)

Scritto il 25 ottobre 2026, alle 20:22 UTC, **prima di qualunque calcolo sui prezzi**. Idea 36 della coda di `research/REGISTRO.md`: la
prova 71 (G13) aveva solo 7 eventi perché la chiusura si ricavava dalle candele e gli annunci con più contratti si scartavano. Ora il
testo di ogni annuncio si legge dall'archivio delle notizie di Binance (come per la prova 103). Il controllo di fattibilità ha contato
soltanto: 72 annunci «Binance Futures Will Delist …» (sezione rimozioni, catalogo 161), tutti con il testo; 4 senza un'ora di chiusura dopo
l'annuncio; **85 contratti** con l'ora della chiusura (3 nel 2022, 21 nel 2024, 29 nel 2025, 32 nel 2026); fra l'annuncio e la chiusura
passano in mediana 115 ore (10% sotto 47, 10% sopra 196). Nessun prezzo guardato.

## 1. Perché

Il perché della prova 71, invariato: quando Binance annuncia la chiusura di un perpetuo, chi ha posizioni deve chiuderle, i market maker
si ritirano e la moneta perde un posto dove si scambia con la leva; il prezzo tende a scendere fino alla chiusura. **Il rischio opposto è
noto** (gli short affollati schiacciati dopo l'annuncio, come ALPACA nel 2025), per questo resta l'uscita a +30%. **Il dubbio scritto
prima**: nei 7 eventi della prova 71 la protezione scattava nel 57% dei casi (−13,19% a evento); molte monete chiuse sui future restano
quotate a pronti e sulle altre borse, quindi la pressione può essere piccola.

## 2. La regola (la prova 71 con le date vere)

* **Eventi**: per ogni annuncio, i contratti `…USDT` scritti nel testo o nel titolo che sono nel nostro pannello (Bitcoin ed Ether esclusi);
  la **chiusura** è l'ora più tarda «AAAA-MM-GG HH:MM (UTC)» scritta nel testo dopo l'ora dell'annuncio. Un contratto annunciato due
  volte vale una volta (il primo annuncio).
* **Operazione**: come la prova 71 (`quindicesima.operazione`): all'apertura dell'ora dopo l'annuncio, short la moneta e long il Bitcoin
  per lo stesso valore; uscita all'apertura dell'ora **prima** della chiusura, o prima se la moneta sale del **30%** dall'entrata (candele a
  1 ora, 1% di scarto). Se fra annuncio e chiusura ci sono meno di 3 ore, l'evento non si usa. Costi come N3, funding vero dei giorni di
  tenuta per le due gambe. Si riporta anche la versione senza l'uscita a +30%.
* **Controllo**: la stessa operazione, con la stessa durata, sulle stesse monete in 20 momenti presi a caso fra 30 e 365 giorni **prima**
  dell'annuncio (seme 2026).
* Una prova a eventi: nel conto **176**, le prove a eventi **32**.

## 3. L'esame

Come N3 (`trentesima.esame`, bootstrap per settimana dell'annuncio): media sopra zero con **p ≤ 0,01**, positiva nelle due metà e senza i 5
eventi migliori, e sopra il controllo; contando le 32 prove a eventi la soglia è 0,00031.
