# Programma 6 — cinquantaseiesima prova: F5 fra le 100 con gli ordini limite (F9)

Scritto il 23 ottobre 2026, mattina, **prima del calcolo**. Idea 23 della coda di `research/REGISTRO.md`.

## 1. Perché, e cosa può dire

F5 paga il 4,9% l'anno di spese a mercato (prova 24). Con gli ordini limite all'apertura del lunedì il 98% delle variazioni di F3
fra le 100 si esegue entro un'ora e il costo per unità scende da 0,070% a 0,048% (`ESECUZIONE.md`, descrittivo); sulle 101-150 le
spese di F5 scendevano dall'11,8% al 5,5% (prova 51). Il bot oggi esegue F5 a mercato (`bot/portafoglio/f5.py`) e la voce P17 del
backlog chiede se passare agli ordini limite.

**Cosa può dire, fissato qui.** F9 è F5 con un'altra esecuzione, e F5 è stata vista prima dell'aggiunta del 23 ottobre
all'asticella: per la riserva di `ASTICELLA.md` (sezione 5) **F9 non può diventare «validata sul passato»**, qualunque sia il suo
Sharpe corretto. La prova serve a misurare se l'esecuzione a limite toglie una parte del vantaggio (gli ordini eseguiti sono
quelli in cui il prezzo è venuto contro) o lo aumenta, e quanto: decide la voce P17. È comunque nel conto: **119**.

## 2. La regola (valori fissati qui)

* F5 com'è (prova 24): le 100 monete più scambiate di ogni settimana, −funding dei 7 giorni, banda 20%/40%, pesi secondo
  l'inverso della volatilità dei 30 giorni, ogni lato al 100%.
* **Ogni variazione di peso** del lunedì (con i pesi che derivano col prezzo durante la settimana, `cinquantunesima.variazioni`):
  un **ordine limite al prezzo d'apertura del lunedì**, valido per la prima ora; eseguito se in quell'ora il prezzo va oltre il
  livello (minimo sotto per chi compra, massimo sopra per chi vende): costo **0,02%**. Se non è eseguito, a mercato
  all'apertura dell'ora dopo: il costo a mercato della moneta come in F5 (`seconda.costi_moneta`: 0,05% più lo scarto) più il
  movimento del prezzo in quell'ora, contro di noi.
* Senza le candele a 1 ora per quella moneta e quel lunedì: a mercato come F5.
* Funding come F5. Dal 4 gennaio 2021 al 5 ottobre 2026.

## 3. L'esame

`terza.esame` e `terza.esito` con lo Sharpe corretto rivisto con l'aggiunta del 23 ottobre (`asticella.corretto_rivisto`,
valore `corretto_con_aggiunta`), soglia 0,95, con il valore della sezione 3 accanto; si riportano la quota di variazioni eseguite
con il limite, il costo medio per unità, le spese l'anno e F5 a mercato sulle stesse settimane.

**Per la voce P17, fissato qui:** se F9 ha spese più basse **e** Sharpe non più basso di F5 sulle stesse settimane, il bot passa
F5 agli ordini limite simulati (con la misura della quota eseguita) senza aspettare le 4 settimane; altrimenti resta a mercato.
