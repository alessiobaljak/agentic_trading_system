# Prova 2 — la revisione separata (24 ottobre 2026)

Fatta da un agente che non ha scritto il codice e non conosceva il risultato prima di rifarlo; ha lavorato in sola lettura. Ha
rifatto il calcolo di QQQ con i costi e ha ottenuto gli stessi numeri (valore finale 202'844 dollari, 3973 ordini, Sharpe 1,05).

**Esito: nessun errore bloccante.** Verificati: l'orario delle barre di Alpaca (il tempo è l'INIZIO della barra: volume mediano di QQQ
circa 13'000 alle 9:29 e 531'000 alle 9:30, l'asta di apertura), nessun uso del futuro nella fascia, nell'apertura, nella chiusura di
ieri e nel VWAP (il VWAP di una barra non esce mai dal suo minimo e massimo in 879'605 barre), l'esecuzione all'apertura della barra
dopo, i costi su tutta la quantità anche quando la posizione si gira, l'uscita di fine giornata, la coerenza con le regole scritte, i
rendimenti giornalieri, il comprare e tenere, lo Sharpe corretto secondo Bailey e López de Prado.

## Cosa ha trovato, e cosa è stato fatto

| # | Trovato | Peso | Cosa è stato fatto |
|---|---|---|---|
| 1 | QQQ passa solo con un margine di circa il 20% sui costi (Sharpe 0,93 con costi ×1,2, 0,90 con ×1,25 contro 0,92 del tenere QQQ); e lo scarto era misurato in momenti calmi, mentre la regola entra quando il prezzo si muove | importante | **Misurato lo scarto vero** in 400 ordini eseguiti scelti a caso (`P002_scarto_vero.md`): media 0,57 punti base contro 0,56 usati (rapporto 1,01), 90° percentile 0,92. Il dubbio non si conferma. Il margine stretto resta e va detto |
| 2 | La regola viene da un lavoro che usa dati fino al 2024: il 2016-2024 è dentro il periodo su cui gli autori l'hanno costruita; N = 2 gruppi non conta questa scelta (con 4 prove lo Sharpe corretto sarebbe circa 0,98) | importante | Non è un errore del codice: è il motivo per cui il periodo chiuso (2025-2026, dopo il lavoro) è la prova vera |
| 3 | Le piccole tasse americane sulle vendite non sono contate (stima del revisore: circa −0,05 di Sharpe) | piccolo | Le regole, scritte prima, dicevano che le copre la versione con i costi raddoppiati (che dà 0,48). Si lascia l'esito com'è e si scrive il margine |
| 4 | Due righe della tabella sbagliate: i giorni con un'operazione erano 1320, non 681; 3,0 ordini per giorno, non 5,8 | minore | Corrette e ricalcolate (`P002_risultati.md`); l'esito non cambia |
| 5 | Il test sul futuro confrontava solo il limite alto | minore | Rinforzato: limite basso, VWAP, decisioni e il giorno tagliato (`tests/test_strategie.py`) |
| 6 | Un giorno vale solo se esistono tutte le sue barre di decisione, anche quelle dopo | minore | Scritto nelle regole; su QQQ toglie 1 giorno |
| 7 | Guadagno concentrato: i 10 giorni migliori fanno il 42% del rendimento; senza il 2018 lo Sharpe è 0,79; 0,91 nel 2016-2019, 1,14 nel 2020-2024 | minore | Tipico delle regole che seguono il movimento; è un'altra ragione di fragilità |
| 8 | Il comprare e tenere comprende 3 settimane di gennaio 2016 in cui la regola non poteva operare; la regola sulle vendite allo scoperto del marzo 2020 non è simulata | minore | Non cambiano l'esito |

## In una riga

Il calcolo è giusto e QQQ passa la ricerca con le regole scritte prima, **con margini stretti** (circa il 20% sui costi, 0,05 sullo
Sharpe corretto) e su un periodo che gli autori della regola conoscevano. Il periodo chiuso decide.
