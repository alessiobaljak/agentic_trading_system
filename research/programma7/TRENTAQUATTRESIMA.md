# Programma 7 — trentaquattresima prova: la deriva del Bitcoin dopo le riunioni della Fed (G22)

Scritto il 25 ottobre 2026, alle 07:52 UTC, **prima di qualunque calcolo sui prezzi**. Idea 66 della coda di `research/REGISTRO.md`
(la parte sulle riunioni della Fed; i dati dell'inflazione restano in coda finché non si hanno le date ufficiali). Le date vengono dal
calendario pubblico della Fed (`federalreserve.gov/monetarypolicy/fomccalendars.htm`, letto il 25 ottobre 2026): il comunicato esce
alle **14:00 di New York** del secondo giorno di riunione.

## 1. Perché, e il dubbio

Nelle azioni è documentata una deriva nelle ore dopo il comunicato della Fed: il mercato digerisce la decisione lentamente e la prima
reazione tende a continuare. Il Bitcoin dal 2021 si muove con la liquidità americana (gli ETF, i tassi) e nessuna prova ha mai guardato un
evento macro a calendario; è un'informazione pubblica, fissata mesi prima, che si mette insieme con i prezzi a ore. **Il dubbio scritto
prima**: sono 46 eventi (poco potere statistico: un p sotto 0,01 richiede un effetto enorme), e lo scalping sulle fiammate (prove 75-78)
ha perso. Probabilità bassa.

## 2. La regola (valori fissati qui)

* **Eventi**: le 46 riunioni programmate dal 27 gennaio 2021 al 16 settembre 2026 (otto l'anno: 2021-01-27, 03-17, 04-28, 06-16, 07-28,
  09-22, 11-03, 12-15; 2022-01-26, 03-16, 05-04, 06-15, 07-27, 09-21, 11-02, 12-14; 2023-02-01, 03-22, 05-03, 06-14, 07-26, 09-20, 11-01,
  12-13; 2024-01-31, 03-20, 05-01, 06-12, 07-31, 09-18, 11-07, 12-18; 2025-01-29, 03-19, 05-07, 06-18, 07-30, 09-17, 10-29, 12-10;
  2026-01-28, 03-18, 04-29, 06-17, 07-29, 09-16). Il voto per notazione del 22 agosto 2025 non è una riunione programmata e resta fuori;
  le riunioni dopo il 5 ottobre 2026 (fine dei dati) restano fuori.
* **Ora del comunicato**: 14:00 di New York convertite in UTC con l'ora legale americana (18:00 UTC d'estate, 19:00 d'inverno).
* **Segnale**: il segno della candela oraria del Bitcoin (`BTCUSDT`, perpetuo) che contiene il comunicato (apertura all'ora del comunicato,
  chiusura un'ora dopo). **Operazione**: nella direzione del segno, entrata all'apertura dell'ora dopo (15:00 di New York), uscita
  all'apertura **6 ore dopo** (21:00 di New York); costi del Bitcoin (`seconda.costi_moneta`) a mercato in entrata e in uscita; niente
  funding (si attraversa al massimo un regolamento). Nessun'altra variante.
* **Controllo**: la stessa regola su tutti i giorni feriali senza riunione dal 2021 al 5 ottobre 2026 alla stessa ora di New York (la
  distribuzione del rendimento medio di 46 giorni presi a caso, 2.000 estrazioni, seme 2026): quanto spesso il caso fa come le riunioni.
* **Descrittivo, non nel conto**: il rendimento medio ora per ora da 3 ore prima a 12 ore dopo il comunicato (per capire la forma della
  reazione), e la versione contraria (sfavorire la prima ora), solo per leggere.
* Una prova a eventi: nel conto **166**, le prove a eventi **26**.

## 3. L'esame

Media sopra zero con **p ≤ 0,01** (bootstrap sulle 46 operazioni) e positiva nelle due metà (2021-2023, 2024-2026); contando le 26 prove a
eventi la soglia è 0,00038. Si riporta anche la quota di giorni a caso che fanno almeno come le riunioni.
