# Prova 10 — la deriva dopo i bilanci (le 10 azioni di allora)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I6 di `REGISTRO.md`, richiesta dal proprietario
il 24 ottobre), committate prima di lanciare il programma. Si conoscevano le prove 1-9 (bocciate). Famiglia nuova (eventi delle
aziende): il periodo chiuso si può riusare.

## Perché dovrebbe funzionare

Dopo un bilancio migliore delle attese il prezzo continua a salire per settimane, perché il mercato incorpora la notizia lentamente:
Ball, Brown (1968); Bernard, Thomas, *Journal of Accounting Research* 27 (1989). Senza le attese degli analisti (non le abbiamo) si usa la
reazione del prezzo come misura della sorpresa: Brandt, Kishore, Santa-Clara, Venkatachalam, «Earnings announcements are full of
surprises» (2008), trovano che la reazione nei giorni del comunicato indica la deriva dopo. **Sospetto scritto prima:** Martineau,
«Rest in peace post-earnings announcement drift», *Critical Finance Review* 11 (2022): sulle grandi aziende la deriva non c'è più dal
2006 circa. Queste sono le aziende più grandi e seguite del mondo.

## I dati

* **Le date** (`stock/dati/bilanci.py`): ogni modulo 8-K con la voce 2.02 depositato alla SEC dalle aziende delle 10 di allora (34
  simboli, 2016-2024), con la data di deposito d; i moduli entro 20 giorni dal precedente della stessa azienda si tolgono (correzioni).
  La voce 2.02 comprende anche annunci che non sono il bilancio (per esempio le consegne trimestrali di Tesla): si tengono tutti, sono
  comunque notizie sui risultati. **L'ora non si usa** (il modulo può arrivare ore dopo il comunicato stampa: vedi il file).
* Prezzi al giorno come la prova 3 (dividendi, frazionamenti, scissioni, cambi di nome).

## La regola

* **Reazione:** per un comunicato con data d (se d non è un giorno di borsa, il primo giorno di borsa dopo), il rendimento del titolo
  dalla chiusura del giorno di borsa prima di d alla chiusura del giorno di borsa dopo d, **meno** il rendimento dello SPY negli stessi
  giorni (tutti e due con i dividendi).
* **Ingresso:** se la reazione è sopra zero e il titolo è fra le 10 di allora del mese dell'ingresso, alla chiusura del giorno dopo d si
  decide e si compra a mercato all'apertura del giorno di borsa successivo, con il 10% del conto (azioni intere), al massimo 10 titoli
  insieme (se i posti non bastano, in ordine alfabetico). Solo acquisti, niente leva.
* **Uscita:** a mercato all'apertura del 21° giorno di borsa dopo l'ingresso (20 sedute, come la prova 8; nessun altro numero provato).
  Se arriva un nuovo comunicato dello stesso titolo mentre lo si tiene, non si fa niente di diverso.
* Periodo: ingressi da maggio 2016 (quando c'è l'elenco delle 10) a fine novembre 2024.

## I costi e l'esame

Costi come la prova 3 (scarto misurato titolo per titolo, 0,5 punti base di slittamento, Interactive Brokers «fisso», costi doppi,
100'000 dollari). Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del
comprare e tenere le 10 di allora (prova 3), sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe
sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri in guadagno. Accanto, da leggere: il guadagno medio per evento rispetto
allo SPY e il suo t. Conta come **1 prova** (19 nel conto).
