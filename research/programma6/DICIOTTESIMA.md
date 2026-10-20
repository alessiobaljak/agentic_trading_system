# Programma 6 — diciottesima prova: le monete appena quotate (N1, N2)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo sui rendimenti** (guardati solo: quante monete nuove per
anno e le date di quotazione di dieci monete note, per controllare i dati). Idea nuova, non in coda: nessuna prova del
programma 5 o 6 l'ha mai guardata, perché tutti gli universi chiedono almeno 200 giorni di storia.

## 1. Perché

* Molte monete nuove sui futures di Binance sono gettoni con poca offerta in giro e molta ancora da sbloccare (fondi,
  squadra, airdrop): nei mesi dopo la quotazione chi li ha avuti a poco vende. È un fatto noto e pubblico (la
  sottoperformance delle ICO nel lungo periodo, Momtaz 2020 e Benedetti-Kostovetsky 2021; nel 2024-2025 il caso «poca
  offerta, valore pieno altissimo» discusso apertamente dagli stessi exchange).
* Quante sono (dal pannello giornaliero, prima data di ogni moneta): 58 nel 2021, 24 nel 2022, 97 nel 2023, 131 nel
  2024, 238 nel 2025, 93 nel 2026 fino al 18 ottobre.
* Contro: chi è short sulle monete nuove spesso paga un funding alto (tanti short), e le monete nuove possono esplodere
  verso l'alto. Per questo nel conto ci sono il funding vero e un tetto al peso di ogni moneta.

## 2. La regola

* **Le giovani**: ogni lunedì, le monete del pannello (esclusi i contratti che non sono una moneta, `seconda.py`) con
  **età** (giorni dalla prima candela giornaliera alla domenica prima) fra **7 e 60** giorni (N1) o fra **7 e 180** giorni
  (N2), con la mediana del volume dei giorni disponibili (al massimo 30) di almeno **2 milioni di dollari**, volume non zero
  la domenica e la candela del lunedì.
* **Le vecchie**: l'universo della terza prova (le 100 più scambiate con almeno 200 giorni di storia), con le correzioni
  del controllo dei dati del 20 ottobre (sezione 4).
* **Portafoglio** (ogni lunedì, per la settimana): short le giovani a pesi uguali, ognuna al massimo il **10%** del
  capitale (se sono meno di 10 il lato short è più piccolo di 1); long le vecchie con lo stesso peso totale del lato short,
  pesi secondo l'inverso della volatilità dei 30 giorni (come F3). Se le giovani sono meno di **3**, nessuna posizione.
* **Costi**: le giovani 0,05% di commissione più **0,10%** di scarto a ogni giro (come le monete 101-200); le vecchie i
  costi della terza prova; funding vero con il segno; pesi che derivano col prezzo durante la settimana (`terza.conto`).
* Due prove (N1, N2): nel conto del programma 6 diventano **42**.

## 3. L'esame

Dal **4 gennaio 2021** (come F3) all'ultima settimana: l'esame della terza prova (`terza.esame`, `terza.esito`: intervallo
della media settimanale sopra zero con il bootstrap a blocchi di 4 settimane, Sharpe corretto ≥ 0,95 con le **42** prove,
almeno 4 anni positivi, l'ultimo anno, costi doppi, almeno 2 trimestri positivi negli anni pieni 2021-2025, qualcosa in più
del Bitcoin). Si riportano anche (senza decidere niente): il lato short da solo, il funding pagato, il numero medio di
giovani, la correlazione con F3 e M1, e il risultato per età (7-30, 30-60, 60-120, 120-180 giorni) e per anno di quotazione.

## 4. Il controllo dei dati che vale anche qui

Le monete tolte dal listino restano nei file con il prezzo fermo e il volume zero; il funding di quei giorni era riempito
con la media dei 90 giorni prima. Da qui in avanti: funding zero nei giorni a volume zero, e fuori dall'universo le monete
con volume zero la domenica (`controllo_zombi.py`).
