# Prova 37 — anticipare il ribilanciamento dei fondi 60/40: SPY contro le obbligazioni del Tesoro

Regole scritte il 16 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i prezzi (idea I39 di `REGISTRO.md`, dalla
ricerca su GitHub chiesta dal proprietario: `IDEE_DA_GITHUB.md`). Si conoscevano le prove 1-36 e l'articolo qui sotto (letti: la
sezione 4, l'appendice B, le figure 2-4 e la tabella 6). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 91 nel
conto.

## Perché dovrebbe funzionare

Harvey, Mazzoleni, Melone, «The Unintended Consequences of Rebalancing», NBER w33554 (2025, rivisto gennaio 2026). I fondi pensione e
i fondi bilanciati tengono una quota fissa di azioni e obbligazioni; quando le azioni salgono più delle obbligazioni devono vendere
azioni e comprare obbligazioni, per calendario (a fine mese) o quando la quota esce da una fascia. Sono miliardi di dollari mossi per
obbligo e in modo prevedibile: il giorno dopo un segnale alto le azioni rendono circa **16-17 punti base** meno delle obbligazioni.
La loro strategia (futures sull'S&P 500 contro futures sul Tesoro a 10 anni, dal 10 settembre 1997 al 17 marzo 2023): **Sharpe 1,11**
prima dei costi, «vicino a 1» dopo i costi, 0,90 togliendo la crisi del 2008-2009 e marzo 2020; asimmetria 5,23 (tabella 6).

**Sospetti scritti prima (forti):**

* **i numeri dell'articolo sono stati scelti sugli stessi anni**: la fascia fino al 2,5%, la scala dell'1,5%, l'ultima settimana del
  mese e il rimbalzo del primo giorno vengono dalle figure 2-4, calcolate sul 1997-2023. Il nostro 2016-2024 è per tre quarti dentro
  quel periodo (fino al 17 marzo 2023) e non è una conferma indipendente; dal 20 marzo 2023 al 31 dicembre 2024 è dopo il loro
  campione, ma sono meno di due anni;
* **pochi giorni enormi** possono fare tutto (asimmetria 5,23; il 2020 nel nostro periodo);
* **fondi quotati invece dei futures**: SPY e IEF (Tesoro 7-10 anni) al posto dei futures; vendere allo scoperto un fondo costa un
  prestito, e la leva è limitata;
* **il segnale usa la chiusura del giorno**: davvero lo si calcola qualche minuto prima e si compra all'asta di chiusura; qui si usa la
  chiusura stessa (una piccola occhiata in avanti). Si stampa accanto la versione con un giorno di ritardo.

## I dati

Le chiusure rettificate per i dividendi di **SPY** e **IEF** (e TLT, solo da leggere) da **Yahoo**, dal 2 gennaio 2014 al 31 dicembre
2024 (i due anni prima del 2016 servono solo a far partire i portafogli simulati); nel repository vanno solo i risultati. Controllo
della seconda fonte: i rendimenti giornalieri di SPY di Yahoo contro quelli di Alpaca (archivio delle prove), correlazione e differenze.

## La regola (dall'articolo, appendice B e sezione 4)

* **Il portafoglio simulato** è 60% SPY e 40% IEF; ogni giorno i pesi si muovono con i rendimenti: w(t) = 0,6·(1+r_SPY) /
  (0,6·(1+r_SPY) + 0,4·(1+r_IEF)) partendo dal peso della sera prima.
* **Il segnale a fascia:** per ogni fascia δ da 0% a 2,5% a passi di 0,1% (26 portafogli), alla chiusura di ogni giorno il segnale è
  w_δ(t) − 60%; se |w_δ(t) − 60%| ≥ δ il portafoglio torna al 60% per il giorno dopo. Il segnale a fascia del giorno è la **media** dei
  26 segnali.
* **Il segnale di calendario:** un portafoglio che torna al 60% alla chiusura dell'ultimo giorno di borsa di ogni mese; il segnale è
  w_C(t) − 60%.
* **Le posizioni:** il segnale a fascia diventa −(segnale a fascia) / 1,5%. Il segnale di calendario diventa: il segno di −(segnale di
  calendario) negli **ultimi 5 giorni di borsa del mese**; nel **primo giorno di borsa del mese** il segno del segnale di calendario di
  4 giorni di borsa prima (il rimbalzo); zero negli altri giorni. Il peso della strategia è la **media** delle due posizioni.
* **Cosa si tiene:** con il peso w deciso alla chiusura del giorno t, per il giorno t+1 si tengono w volte il conto in SPY e −w volte
  il conto in IEF (w negativo: corti su SPY, lunghi su IEF). Il guadagno del giorno è w·(r_SPY − r_IEF).
* **La leva (interpretazione scritta prima, la leva è una decisione del proprietario):** l'esame usa w limitato fra −1 e +1 (al massimo
  una volta il conto per parte, due volte in tutto: il limite di Alpaca per tenere posizioni la notte); accanto si stampa la versione
  dell'articolo, senza limite.
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima)

Ogni giorno si compra e si vende la differenza fra il peso nuovo e quello vecchio, su tutte e due le parti, all'asta di chiusura: metà
dello scarto **SPY 0,185 punti base** (misurato: `stock/dati/ESITO_CONTROLLI.md`) e **IEF 1 punto base** (non misurato: preso largo,
uno scarto tipico di un centesimo su circa 95 dollari è circa 1 punto base intero); **slittamento 1 punto base** per parte; commissioni
Interactive Brokers «fisso» su un conto di 100'000 dollari; **prestito del fondo venduto allo scoperto 0,5% l'anno** sulla parte corta.
Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-36)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): le due parti da sole (solo fascia, solo calendario); la versione dell'articolo senza limite
alla leva; con un giorno di ritardo; con TLT al posto di IEF; prima e dopo il 17 marzo 2023 (la fine del campione dell'articolo); senza
marzo 2020; asimmetria; quota del guadagno dai 10 giorni migliori; peso medio e massimo; anno per anno.

**Famiglia e periodo chiuso (deciso prima):** è una famiglia nuova, «ribilanciamento» (la direzione dipende da come sono andate azioni
e obbligazioni, non dalla sola data; la parte di calendario somiglia al cambio del mese della prova 6, che però comprava sempre). **Se
passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**.
