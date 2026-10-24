# Il metodo delle azioni (approvato il 24 ottobre 2026)

Proposta della sessione «trading stock» dopo le indicazioni del proprietario del 24 ottobre 2026: «i mercati stock direi America …
obbiettivo è di creare profitto ovviamente, sempre back testing se possibile poi paper demo live e poi soldi veri, non ho una strategia
particolare puoi vendere e comprare in giornata puoi tenere per più giorni [...] per le strategie di ingresso e uscita o indicatori da
usare scegli tu [...] direi di concentrarci per il momento sulle 10 top stock e poi capire se estendere».

Le parti segnate **(approvato)** sono state **approvate dal proprietario il 24 ottobre 2026** («Sì alle proposte del metodo»).
Nessun calcolo è stato fatto: le regole di ogni prova si scrivono prima, in un file loro, con la riga in `REGISTRO.md`.

## 1. L'asticella: battere chi compra e tiene

Una strategia vale solo se fa meglio, **dopo i costi**, che comprare e tenere l'indice (lo SPY, che segue l'S&P 500) e che comprare e
tenere gli stessi titoli che usa. Il motivo: nel 2025 il 79% dei fondi attivi sulle grandi aziende americane ha fatto peggio
dell'S&P 500, e su 15 anni (fino a fine 2024) l'89,5% [1]. Sono professionisti con molti mezzi: battere l'indice è difficile, e se non
ci riusciamo la risposta onesta è «compra l'indice».

Accanto all'asticella dell'indice resta quella delle crypto: lo Sharpe corretto per i tentativi, con il conto di tutte le prove (anche le
bocciate) in `REGISTRO.md` (`LEZIONI_DALLE_CRYPTO.md`, punto 2).

## 2. I titoli **(approvato)**

* **Per il paper e il conto vero:** le 10 azioni americane più scambiate, come chiesto. Sono anche le più economiche da comprare e
  vendere (lo scarto fra acquisto e vendita è il più piccolo del mercato).
* **Per le prove sul passato: le 10 più scambiate *di allora*, non quelle di oggi.** Le 10 più grandi di oggi sono le vincitrici degli
  ultimi dieci anni: provarle sul passato vuol dire sapere già chi ha vinto. È l'errore dei «titoli sopravvissuti» delle crypto
  (`LEZIONI_DALLE_CRYPTO.md`). In ogni mese si prendono le 10 con più dollari scambiati nei tre mesi prima (prezzo per volume: serve solo
  il dato che abbiamo già). Il serbatoio da cui sceglierle sono le aziende che sono state nell'S&P 500 in quel momento (l'elenco storico
  pubblico è da verificare: per esempio https://github.com/fja05680/sp500).
* **In più, gli indici: SPY (S&P 500) e QQQ (Nasdaq 100).** Hanno più storia, costi bassissimi e nessun rischio del singolo titolo;
  molte delle idee studiate (sezione 6) sono nate proprio sull'indice.

## 3. I dati

* **Barre al minuto e al giorno dal 2016**, tutte le borse americane, da Alpaca: il piano gratuito dà la storia dal 2016, con il solo
  limite degli ultimi 15 minuti [2]. Serve una chiave gratuita di Alpaca, che **non entra mai nel repository**: va messa nelle
  impostazioni dell'ambiente della sessione.
* Verificato il 24 ottobre da questa sessione: Alpaca risponde ma chiede la chiave (codice 401); Yahoo rifiuta per troppe richieste
  (429); Stooq non è raggiungibile; GitHub sì.
* Ogni prezzo va corretto per frazionamenti e dividendi; il dato di un giorno si usa solo dopo che è stato pubblicato.
* **I prezzi scaricati non entrano nel repository**: sono grandi, e di regola la licenza dei dati di borsa non permette di
  ripubblicarli (il repository è pubblico; i termini di Alpaca sono da verificare). Ogni sessione li scarica e li tiene in locale; nel
  repository vanno solo il programma che li scarica, i controlli e i risultati.
* Le chiavi le legge solo una sessione aperta **dopo** che sono state messe nell'ambiente: il 24 ottobre questa sessione (aperta prima)
  non le vedeva, e Alpaca rispondeva 401.
* **Verificato il 24 ottobre (sessione nuova, con le chiavi):** Alpaca risponde 200 per le barre al giorno e al minuto dal 2016, le
  quotazioni, i frazionamenti e i dividendi, il calendario della borsa. Gli ultimi 15 minuti non si possono chiedere (risposta 403
  «subscription does not permit querying recent SIP data»): il programma tira indietro la fine di 16 minuti.
* **I dividendi di Alpaca non sono completi.** Sullo SPY, fra il 2016 e il 2024, l'elenco dei dividendi ne ha 33 su 36: mancano lo
  stacco del 18 marzo 2016, del 15 giugno 2018 e del 20 dicembre 2024; i primi due mancano anche nei prezzi rettificati di Alpaca
  (`stock/dati/ESITO_CONTROLLI.md`). Vuol dire che il comprare e tenere lo SPY, cioè l'asticella, con i dati di Alpaca rende un po'
  meno del vero (fra lo 0,3 e lo 0,6% per ogni dividendo mancante: è la misura dei 34 trovati nei prezzi rettificati): un'asticella più bassa del giusto. Prima di qualsiasi confronto con
  l'indice i dividendi mancanti vanno presi da una seconda fonte (per lo SPY, lo storico delle distribuzioni pubblicato
  dall'emittente) e scritti a mano, con la fonte.

## 4. I periodi **(approvato)**

* **Ricerca: gennaio 2016 → dicembre 2024**, con le finestre che avanzano come sulle crypto: le regole si scelgono su 12 mesi e si
  provano sui 3 dopo, poi si avanza di 3 mesi.
* **Periodo chiuso: gennaio 2025 → settembre 2026.** Nessuno lo guarda finché una strategia non ha passato la ricerca e il revisore; si
  apre una volta sola, e se la strategia lì non regge è bocciata.

## 5. I costi

* Commissioni del broker scelto (da verificare sul suo listino quando sarà scelto).
* Scarto fra acquisto e vendita: **misurato** sulle quotazioni dello stesso minuto, non inventato.
* Ordini limite: eseguiti solo se il prezzo **passa oltre** il livello, non se lo tocca appena (lezione delle crypto).
* Ogni risultato si mostra anche con i costi raddoppiati: se regge solo con i costi bassi, non regge.

## 6. Le idee da cui partire

Non si parte dagli indicatori in sé (sulle crypto le regole con gli indicatori tecnici, da sole, hanno perso dopo i costi in decine di
prove: `LEZIONI_DALLE_CRYPTO.md`), ma da **effetti studiati con una ragione economica**; gli indicatori servono a misurarli. La coda,
con l'ordine e il motivo, è in `REGISTRO.md`, sezione 2.

## 7. Dal passato al demo, dal demo ai soldi veri **(approvato)**

Le condizioni si scrivono **adesso**, prima di vedere qualsiasi risultato:

1. **Al demo** va una strategia che ha passato la ricerca, il revisore separato e il periodo chiuso, battendo l'indice dopo i costi.
2. **Ai soldi veri** solo dopo almeno 3 mesi di demo in cui i risultati stanno dentro quello che il passato prevedeva (lo stesso numero
   di operazioni, lo stesso costo misurato, un risultato non peggiore del 5% più sfortunato delle simulazioni), **e** dopo la richiesta
   esplicita, ripetuta e consapevole del proprietario (regola del progetto, `CLAUDE.md`).
3. **Prima dei soldi veri, le tasse svizzere.** Chi vende titoli tenuti meno di sei mesi, o compra e vende in un anno più di cinque
   volte il proprio patrimonio, o guadagna in borsa più della metà del proprio reddito, rischia di essere considerato «commerciante
   professionale di titoli»: i guadagni diventano reddito tassato (e le perdite si deducono) [3]. Comprare e vendere in giornata
   rientra nel primo criterio. Va chiesto a un consulente fiscale prima del passaggio ai soldi veri; per il demo non conta.

## 8. Come è fatto il programma

Tutto in `stock/`, separato dalle crypto:

| Parte | Cosa fa |
|---|---|
| `stock/dati/` | scarica e controlla i prezzi (frazionamenti, buchi, orari), li salva fuori dal repository se sono grandi |
| `stock/strategie/` | una strategia = una funzione che dai prezzi fino a *ora* dice cosa fare; **la stessa funzione** serve alle prove sul passato e al demo |
| `stock/simulatore/` | prova sul passato con i costi della sezione 5 e le finestre della sezione 4 |
| `stock/esecutore/` | manda gli ordini al conto demo del broker scelto; **rifiuta ogni conto che non sia demo** (come `DRY_RUN` per le crypto) |
| `stock/registro/` | tiene ogni ordine, ogni esecuzione e il confronto con quello che il passato prevedeva |
| `dashboard/app/components/stock/` | la scheda delle azioni nella dashboard |

## Fonti

1. S&P Dow Jones Indices, SPIVA U.S. Year-End 2025 (79% su un anno) — https://www.spglobal.com/spdji/en/spiva/article/spiva-us-year-end-2025/ ; SPIVA U.S. Year-End 2024 (89,5% su 15 anni) — https://spglobal.com/spdji/en/spiva/article/spiva-us-year-end-2024 (letti tramite i risultati della ricerca)
2. Alpaca, «About Market Data API» — https://docs.alpaca.markets/docs/about-market-data-api (letto tramite i risultati della ricerca)
3. VZ VermögensZentrum, «Wann Privatanleger Kursgewinne versteuern müssen» (aggiornato il 3 gennaio 2026), che riprende la circolare dell'Amministrazione federale delle contribuzioni — https://www.vermoegenszentrum.ch/ratgeber/wissensbeitrage/privatkunden/steuern-sparen/profis-mussen-kursgewinne-versteuern.html (letto direttamente). Il testo ufficiale della circolare non l'ho letto: **da verificare**.
