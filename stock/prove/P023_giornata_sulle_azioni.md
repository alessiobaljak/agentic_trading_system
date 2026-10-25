# Prova 23 — le regole in giornata sulle 10 azioni di allora (ultima mezz'ora, zona di rumore, prima candela 5 e 15 minuti, inversione)

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** su queste azioni, committate prima di lanciare il programma. Richiesta
del proprietario: «chi ti ha detto di eseguirla su SPY o QQQ e non altre stock?» e «rifai anche le altre in giornata sulle azioni».
Le regole in giornata a indicatori (prove 1, 2, 17, 22) erano state provate solo su SPY e QQQ, perché i prezzi al minuto di tutti i 9
anni c'erano solo per loro. Si conoscevano i risultati di quelle prove sugli indici (tutte bocciate) e delle prove 20 e 21 (la prima
candela sulle azioni nei giorni dei bilanci: vantaggio prima dei costi, perso nello scarto dell'apertura).

Contano come **5 prove** (una per regola; le 10 azioni insieme sono un solo conto).

## Perché potrebbe andare diversamente dagli indici

Le azioni singole si muovono più dell'indice, con più giornate in cui una notizia sposta il prezzo in una direzione sola: le regole che
seguono il movimento hanno più strada da fare (Zarattini, Barbon, Aziz, «A Profitable Day Trading Strategy For The U.S. Equity Market»,
2024, sulle azioni «in gioco»). **Sospetto scritto prima:** lo scarto delle azioni all'apertura è più largo di quello misurato nel resto
della giornata (prova 20: 23 punti base nei giorni con notizie); le 10 più scambiate sono le più seguite dai fondi veloci; e su 4 di
queste 5 regole gli indici hanno già detto no.

## I titoli e i giorni

* **Le 10 azioni di allora** (`stock/universo/dieci_di_allora.csv`, regole in `stock/universo/costruisci.py`): in ogni giorno, i 10
  titoli dell'elenco del mese di quel giorno (l'elenco usa solo dati fino al mese prima). FB si legge come META (`cambi_di_nome.csv`).
  33 titoli in tutto; giorni da maggio 2016 al 31 dicembre 2024.
* **Prezzi:** al minuto di Alpaca, non rettificati, solo la seduta. Nessuna regola tiene posizioni di notte.
* **Giorni esclusi per un titolo:** quelli già esclusi dalle prove sugli indici (chiusure anticipate, giorni segnalati dal controllo dei
  minuti, barre mancanti), più il giorno di ogni frazionamento o raggruppamento e i 5 giorni di borsa dopo (le regole usano i prezzi
  dei giorni prima, non rettificati).
* **Quanto:** ogni titolo ha un posto da **10'000 dollari** (un decimo di 100'000), 98% investito, azioni intere, senza leva; il conto
  si rimette a pesi uguali ogni giorno (nessuna posizione passa la notte, quindi senza costi). Il rendimento del giorno è la media dei
  10 posti; un posto senza operazioni quel giorno rende zero.

## Le regole

Identiche alle prove sugli indici, titolo per titolo, **senza cambiare nessun numero**:
1. **L'ultima mezz'ora** (`P001_ultima_mezzora.md`, `stock/strategie/ultima_mezzora.py`).
2. **La zona di rumore** (`P002_zona_di_rumore.md`, `stock/strategie/zona_di_rumore.py`).
3. **La prima candela da 5 minuti** e 4. **da 15 minuti**, obiettivo 10 volte il rischio (`P017_prima_candela.md`,
   `stock/strategie/prima_candela.py`).
5. **L'inversione a 5 passi** (`P022_inversione_apertura.md`, `stock/strategie/inversione.py`).

## I costi

Per ogni titolo, metà della sua mediana dello scarto misurato (`stock/dati/ESITO_CONTROLLI_UNIVERSO.md`) e 0,5 punti base di
slittamento, come la prova 3; commissioni Interactive Brokers «fisso» (sul posto da 10'000 dollari il minimo di 1 dollaro pesa circa 1
punto base a ordine); versione con i costi raddoppiati. Lo scarto misurato è di mezza giornata, non dell'apertura: per questo, se una
regola passa la ricerca o ha lo Sharpe senza costi sopra quello del tenere, **si misura lo scarto vero negli istanti degli ordini** su
un campione e si rifà il conto con quello prima di qualunque passo dopo.

## L'esame

Per ogni regola: (1) Sharpe annuo con i costi più alto del **tenere lo SPY** e del **tenere le stesse 10 azioni** a pesi uguali
(ribilanciate il primo giorno di ogni mese, come la prova 3); (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe
sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri in guadagno. Accanto, da leggere: operazioni, guadagno medio a
operazione e il suo t, i titoli che contano di più. Se passa: revisore separato, poi il demo per le regole che seguono il movimento (il
periodo chiuso di quella famiglia è consumato dalla prova 2) e il periodo chiuso una volta per l'inversione.
