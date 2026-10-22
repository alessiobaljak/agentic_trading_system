# Programma 6 — cinquantunesima prova: F5 sulle monete 101-150 con gli ordini limite (F7)

Scritto il 22 ottobre 2026, mezzogiorno, **prima del calcolo**. Idea 22 della coda di `research/REGISTRO.md`.

## 1. Perché

Sulle monete 101-150 F5 incassa il 27,7% l'anno dal funding e il prezzo non lo toglie (+1,2%), ma le spese a mercato sono il
15,1% l'anno e la conferma fallisce (prova 50). Con gli ordini limite il costo per F3 fra le 100 scendeva da 0,070% a 0,048%
per unità scambiata, con il 98% degli ordini eseguiti (`ESECUZIONE.md`); qui lo scarto pesa di più (0,10%), quindi il
risparmio può essere maggiore. **Non è una conferma** (cambia l'esecuzione dopo aver visto la prova 50): è una prova nel conto.

## 2. La regola (valori fissati qui)

* F5 com'è (prova 50) sulle monete dalla 101ª alla 150ª.
* **Ogni variazione di peso** del lunedì (entrate, uscite, cambi di peso, come in `esecuzione.py`): un **ordine limite al prezzo
  d'apertura del lunedì**, valido per la prima ora; eseguito se in quell'ora il prezzo va oltre il livello (minimo sotto per
  chi compra, massimo sopra per chi vende): costo **0,02%**. Se non è eseguito, si fa a mercato all'apertura dell'ora dopo:
  commissione 0,05% più scarto **0,10%** più il movimento del prezzo in quell'ora, contro di noi.
* Senza le candele a 1 ora per quella moneta e quel lunedì: a mercato (0,05% + 0,10%), come la prova 50.
* Funding come F5. Dal 4 gennaio 2021 al 5 ottobre 2026. Una prova: nel conto diventano **110**.

## 3. L'esame

`terza.esame` e `terza.esito` con lo Sharpe corretto rivisto (`asticella.py`), soglia 0,95; si riportano anche la quota di
ordini eseguiti con il limite, il costo medio per unità e le spese l'anno, e la prova 50 sulle stesse settimane.
