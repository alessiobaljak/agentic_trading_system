# Programma 7 — sessantasettesima prova: l'inizio del mese sul Bitcoin (IM)

Scritto il 29 ottobre 2026 alle 20:23 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 105 della coda. Nel registro
non c'è nessuna prova sui giorni del mese: la prova 68 (il buco del CME) e il controllo dei giorni della settimana (`CALENDARIO.md`)
guardavano altro, e gli effetti di calendario del programma 5 erano a ore (le sessioni del giorno).

## 1. Perché

* **I flussi di ogni mese**: gli stipendi, gli acquisti a rate fissi (i piani che comprano ogni mese) e i fondi che ribilanciano a fine
  mese comprano negli ultimi e nei primi giorni del mese. Nelle azioni è l'effetto del «cambio del mese» (Ariel 1987; Lakonishok e
  Smidt 1988: l'ultimo giorno di borsa e i primi tre del mese dopo).
* **Dal 2024** i fondi quotati sul Bitcoin portano nel mercato i flussi dei risparmiatori americani, che seguono proprio il calendario
  degli stipendi.
* **I dubbi scritti prima**:
  * gli effetti di calendario sono stati cercati da tanti e quasi sempre spariscono dopo la pubblicazione;
  * sono circa 80 mesi dal 2020: con la volatilità del Bitcoin in 4 giorni (circa il 7%) serve una media vicina al 2% a operazione per
    passare l'esame; la prova ha poca forza, e va detto prima;
  * gli effetti di calendario del programma 5 non hanno retto.

## 2. La regola (fissata qui)

* **Mercato**: il perpetuo del Bitcoin di Binance, candele giornaliere (`seconda.pannello`), dal gennaio 2020 al settembre 2026.
* **L'operazione**: long il Bitcoin dall'apertura (00:00 UTC) dell'ultimo giorno del mese all'apertura del quarto giorno del mese dopo:
  quattro giorni, l'ultimo del mese e i primi tre. Costi a mercato del Bitcoin (`ventunesima.COSTO_BTC`, 0,12% andata e ritorno),
  funding dei quattro giorni.
* **Una prova a eventi**: nel conto delle prove diventano **225**, le prove a eventi **38**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per evento sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le 38 prove a eventi la
  soglia è **0,00026**.
* **Il controllo**: la stessa operazione di quattro giorni, con gli stessi costi, aperta in ogni altro giorno del periodo la cui
  tenuta non tocca nessuna finestra del cambio del mese. La differenza si misura come media degli eventi meno media del controllo, con
  il ricampionamento degli eventi.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: per anno; l'ultimo giorno da solo e i primi tre da soli; il 2020-2023 contro il 2024-2026
  (prima e dopo i fondi quotati); lo stesso sulle altcoin (l'indice a pesi uguali dell'universo di G1, contro il Bitcoin).
