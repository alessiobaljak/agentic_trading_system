# Programma 6 — trentaquattresima prova: indicatori tecnici con il contesto del funding (T1, T2)

Scritto il 21 ottobre 2026, mattina, **prima di qualunque calcolo**, dopo il proprietario: «quando dico continua a cercare
vuol dire trovare anche altre strategie [...] non riesco a capire se stiamo facendo trading / scalping oppure comprando e
tenendo per ore e giorni [...] senza usare veramente degli indicatori tecnici» (e il 19 ottobre: «comprare e tenere 12 ore
non è trading [...] partendo dagli indicatori tecnici»).

## 1. Perché

* Gli indicatori da soli non bastano (prove 1, 2B, 3: Sharpe al massimo 0,69): guadagnano troppo poco per operazione rispetto
  ai costi. Quello che regge è il **funding fra monete** (F3, F5): chi paga molto per stare con la leva da una parte, poi
  perde.
* Qui l'indicatore decide **quando** entrare e uscire (una rottura del prezzo, con lo stop e l'uscita che segue il prezzo), e
  il funding decide **da che parte** è giusto stare: long solo dove a pagare sono gli short, short solo dove pagano i long.
  È trading vero, su candele a 4 ore, con tenute da qualche ora a una settimana.
* T1 (senza il filtro) serve per vedere quanto aggiunge il funding.

## 2. La regola (valori fissati qui, non scelti sul passato)

* **Monete**: ogni settimana le 100 più scambiate dell'universo della terza prova (al tempo giusto, dati corretti del 20
  ottobre); 449 monete in tutto, tutte con le candele a 1 ora (`research/data/p6` e `p6h`), riunite in candele a 4 ore
  (00, 04, 08, 12, 16, 20 UTC).
* **Segnale**: alla chiusura di una candela a 4 ore, **rottura di Donchian a 20 candele** (poco più di 3 giorni): chiusura
  sopra il massimo delle 20 candele prima → long; sotto il minimo → short. La moneta deve essere nell'universo della settimana.
* **T2, il filtro del funding**: la somma del funding dei 7 giorni prima del giorno del segnale, in rango fra le monete
  dell'universo: long solo se è nel **40% più basso**, short solo se è nel **40% più alto**. T1: nessun filtro.
* **Entrata**: all'apertura della candela dopo il segnale (ordine a mercato). Una posizione per moneta alla volta.
* **Uscite**: stop iniziale a **2 ATR** (ATR a 14 candele al segnale) dal prezzo d'entrata; uscita che segue il prezzo a **3
  ATR** dalla chiusura migliore dall'entrata (chandelier); si esce al livello toccato (all'apertura se il prezzo l'ha già
  saltato); al massimo **42 candele** (7 giorni), poi all'apertura.
* **Costi**: commissione a mercato 0,05% più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre) all'entrata e all'uscita;
  funding di ogni ora di tenuta (il funding del giorno diviso 24), pagato dai long e incassato dagli short.
* Entrate dal **4 gennaio 2021** al **10 ottobre 2026**.

## 3. L'esame (tutte e due le parti)

* **Per operazione**: media netta sopra zero con **p ≤ 0,005** a una coda (due varianti), bootstrap sulle settimane
  d'entrata; positiva nelle due metà e senza le 5 migliori.
* **Come portafoglio**: ogni operazione il 5% del capitale, al massimo 20 aperte; rendimento della settimana = somma delle
  operazioni chiuse nella settimana; `terza.esame` e `terza.esito` con lo Sharpe corretto sulle prove del programma 6, che
  diventano **58**.
* VALIDA solo se passa tutte e due. Si riportano anche: numero di operazioni, tenuta media, quota vinte, quante volte esce
  per lo stop, per l'uscita mobile e per il tempo.
