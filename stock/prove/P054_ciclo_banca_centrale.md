# Prova 54 — il ciclo della banca centrale: lo SPY solo nelle settimane pari dopo ogni riunione

Regole scritte il 28 novembre 2026 **prima di qualsiasi calcolo** (idea I67 di `REGISTRO.md`, dall'audit del 27 novembre), committate
prima del programma. Valgono le due regole di metodo scritte lo stesso giorno in `METODO.md` (sezione 4: due campioni, contanti al
tasso dei buoni del Tesoro).

## Perché dovrebbe funzionare

Cieslak, Morse e Vissing-Jorgensen, *Stock Returns over the FOMC Cycle*, Journal of Finance 74 (2019): dal 1994 al 2016 quasi tutto il
premio delle azioni americane arriva nelle settimane **pari** del ciclo della banca centrale (settimane 0, 2, 4 e 6 contate dal
comunicato), non solo nel giorno prima del comunicato. La spiegazione dello studio: le decisioni informali della banca centrale escono
a cadenza di due settimane (riunioni del consiglio, discorsi), e il mercato sale quando escono. Nei nostri dati l'effetto del giorno
prima c'è ancora (prova 7: +0,23% in media nelle 24 ore prima, t 2,9), ma è troppo raro per battere il tenere sempre (prova 14).
Qui si sta nel mercato circa metà dei giorni, e il resto del tempo i contanti rendono i buoni del Tesoro.

**Sospetti scritti prima.**
* L'effetto potrebbe essersi indebolito dopo il 2016 (lo dice chi l'ha riprovato dopo lo studio; da verificare): il periodo di
  ricerca 2016-2024 viene tutto **dopo** il campione dello studio, ed è lui che decide.
* Il 1994-2015 è il campione in cui lo studio ha trovato l'effetto: lì il risultato è già noto. Si calcola e si legge, **non conferma**
  (`METODO.md`, sezione 4).
* La famiglia «banca centrale» (prove 7, 9 e 14) ha già aperto il periodo chiuso 2025-2026: se la prova passa, la conferma viene
  solo dai giorni in avanti dal 1° ottobre 2026, misurati a tavolino (idea I75), non da un altro periodo chiuso.
* Stando fuori metà del tempo, lo Sharpe può salire anche senza effetto vero se i giorni fuori sono più volatili: si legge accanto lo
  Sharpe dei giorni dispari, che dovrebbe essere vicino a zero.

## I dati

* **SPY**, chiusure giornaliere rettificate per dividendi e frazionamenti, da Yahoo (dal 1993; i prezzi restano fuori dal repository).
* **I comunicati delle riunioni programmate** della banca centrale: `stock/dati/fomc.py` per il 2016-2024; per il 1994-2015 dalle pagine
  storiche della Federal Reserve (`https://www.federalreserve.gov/monetarypolicy/fomchistorical{anno}.htm`), riunioni programmate
  soltanto (fuori le straordinarie e le teleconferenze, come in `fomc.py`), aggiunte a `fomc.py` con la fonte prima del calcolo.
* **Il tasso dei buoni del Tesoro a tre mesi**: FRED, serie DTB3, il valore del giorno prima.

## La regola

* **Il giorno 0** è il giorno di borsa del comunicato. Per ogni giorno di borsa *t*, *d* = i giorni di borsa da quello del comunicato
  più recente (0 il giorno del comunicato).
* **Le settimane pari**: *d* da 0 a 3 (settimana 0), da 9 a 13 (settimana 2), da 19 a 23 (settimana 4), da 29 a 33 (settimana 6); più il
  giorno di borsa **prima** di ogni comunicato (la settimana 0 comincia il giorno −1). È la divisione dello studio (settimana *k* = i
  giorni da 5*k*−1 a 5*k*+3); se il testo dello studio la dicesse diversa, vale questa, scritta prima.
* **In mercato** nei giorni delle settimane pari: si tiene lo SPY al 98% del conto, comprato alla chiusura del giorno di borsa prima del
  primo giorno della finestra e venduto alla chiusura dell'ultimo giorno (rendimento da chiusura a chiusura). Due finestre attaccate
  sono una sola (niente vendita e riacquisto).
* **Fuori mercato**: i contanti rendono DTB3/360 per ogni giorno di calendario.
* Nessun numero scelto sui dati: le finestre sono quelle dello studio, il 98% è quello di tutte le prove.

## I costi

Ordini all'asta di chiusura: slittamento di **2 punti base** per lato (come la prova 46), commissioni di Interactive Brokers «fisso».
Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-53, con la soglia di 0,80 dalla prova 54)

**Da sola, sul 2016-2024:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,80
con tutte le serie del conto (le prove che perdono di sicuro fuori dalla varianza, `METODO.md`, sezione 1); (3) Sharpe sopra zero con
i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela:** Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto
0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t
dello Sharpe della parte almeno 1,3, anche senza marzo 2020; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi
di 20 giorni.

**Da leggere accanto (non cambiano l'esito):** il 1994-2015 con lo stesso esame (campione dello studio); lo Sharpe e il rendimento medio
dei giorni delle settimane dispari; la parte dei giorni in mercato; l'anno per anno; i giorni in avanti dal 1° ottobre 2026 fino
all'ultimo disponibile; lo Sharpe con i contanti a zero (come le prove prima della 54), per confronto.

**Se passa uno dei due esami:** revisore separato, poi la misura a tavolino sui giorni in avanti (il periodo chiuso 2025-2026 la famiglia
l'ha già usato). **Nel conto: 1 prova** (SPY, una variante).
