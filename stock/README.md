# Le azioni (stock)

Area nata il 24 ottobre 2026 su richiesta del proprietario: «apri un'altra sessione che dovrai chiamare trading stock, all'interno di
GitHub crea una cartella dedicata alle stock che ovviamente non si mischi con tutto quello che stiamo facendo lato crypto, solo la
dashboard sarà condivisa [...] stock è qualcosa di nuovo su cui non abbiamo dati, ma il modello e l'approccio li creiamo sulla base
di quello che abbiamo imparato nella sessione crypto; unica differenza è che il paper lo voglio fare su un reale conto live demo di
una piattaforma (che mi dovrai consigliare tu per il mercato svizzero)».

## Chi lavora qui

La sessione **«trading stock»**. La sessione delle crypto non tocca questa cartella; la sessione delle azioni non tocca le cartelle
delle crypto (`bot/`, `research/`, `ops/`, `scripts/`, `tests/` delle crypto, `docs/` delle crypto). **In comune c'è solo la
dashboard** (`dashboard/`): le azioni vi entrano con una scheda loro e componenti loro (`dashboard/app/components/stock/`),
toccando il resto della dashboard il meno possibile (solo per aggiungere la scheda).

## Cosa c'è (e cosa no)

* Si parte da zero: niente dati, niente codice, niente strategie. Si porta dalle crypto solo il **metodo** e le **lezioni**
  (`LEZIONI_DALLE_CRYPTO.md`).
* Il registro unico delle prove sulle azioni è `stock/REGISTRO.md` (un conto delle prove suo, che parte da zero).
* Il paper si fa su un **conto demo vero** di una piattaforma (da scegliere: è il primo compito della sessione, con il proprietario).

## Regole che non si negoziano (le stesse delle crypto)

* **Niente soldi veri.** Solo il conto demo, finché il proprietario non chiede altro in modo esplicito, ripetuto e consapevole.
* **Mai un segreto in un commit**: le chiavi o le password del conto demo non entrano mai nel repository (che è pubblico).
* **Regole scritte prima del calcolo**, ogni prova nel conto, un revisore separato prima del paper, nessun numero senza la sua fonte.
* **Il paper non si usa mai per scegliere le regole**: serve a confermare.
