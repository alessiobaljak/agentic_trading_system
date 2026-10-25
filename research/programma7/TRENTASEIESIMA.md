# Programma 7 — trentaseiesima prova: la deriva del Bitcoin dopo il dato dell'inflazione americana (G23)

Scritto il 25 ottobre 2026, alle 08:01 UTC, **prima di qualunque calcolo sui prezzi**. La seconda parte dell'idea 66 della coda di
`research/REGISTRO.md` (la prima, le riunioni della Fed, è la prova 96: +0,61% a operazione, p 0,021, in calo dal 2025). Le date vengono
dall'archivio pubblico delle pubblicazioni del BLS (`bls.gov/bls/news-release/cpi.htm`, letto il 25 ottobre 2026): il dato esce alle
**8:30 di New York**. Stessa struttura della prova 96, cambiano solo l'evento e l'ora: nessun parametro nuovo.

## 1. Perché, e il dubbio

Il dato dell'inflazione è l'evento macro a calendario che muove di più i tassi attesi, dodici volte l'anno (contro otto della Fed): se il
Bitcoin digerisce le notizie macro con una deriva nella prima ora (come la prova 96 ha mostrato per il 2022-2024), qui gli eventi sono
quasi il doppio e il potere statistico cresce. **Il dubbio scritto prima**: la prova 96 ha mostrato una deriva in calo (negativa nel
2025-2026) e concentrata in un'ora; la candela delle 8:00 contiene mezz'ora prima del dato (il segnale è un po' sporco); 69 eventi restano
pochi per la soglia di tutte le prove a eventi. Probabilità bassa.

## 2. La regola (valori fissati qui)

* **Eventi**: le 69 pubblicazioni dal 10 febbraio 2021 al 14 ottobre 2026 (il dato di ottobre 2025 non è uscito per la sospensione del
  bilancio federale): 2021-02-10, 03-10, 04-13, 05-12, 06-10, 07-13, 08-11, 09-14, 10-13, 11-10, 12-10; 2022-01-12, 02-10, 03-10, 04-12,
  05-11, 06-10, 07-13, 08-10, 09-13, 10-13, 11-10, 12-13; 2023-01-12, 02-14, 03-14, 04-12, 05-10, 06-13, 07-12, 08-10, 09-13, 10-12, 11-14,
  12-12; 2024-01-11, 02-13, 03-12, 04-10, 05-15, 06-12, 07-11, 08-14, 09-11, 10-10, 11-13, 12-11; 2025-01-15, 02-12, 03-12, 04-10, 05-13,
  06-11, 07-15, 08-12, 09-11, 10-24, 12-18; 2026-01-13, 02-13, 03-11, 04-10, 05-12, 06-10, 07-14, 08-12, 09-11, 10-14. Le pubblicazioni
  dopo il 5 ottobre 2026 (fine dei dati) restano fuori.
* **Ora**: 8:30 di New York; la candela oraria che contiene il dato è quella che apre alle 8:00 di New York (12:00 UTC d'estate, 13:00
  d'inverno). **Segnale**: il segno di quella candela. **Operazione**: nella direzione del segno, entrata all'apertura dell'ora dopo (9:00 di
  New York), uscita all'apertura **6 ore dopo** (15:00); costi del Bitcoin a mercato in entrata e in uscita; niente funding.
* **Controllo**: la stessa regola nei giorni feriali senza pubblicazione alla stessa ora di New York, 2.000 estrazioni di 69 giorni a caso
  (seme 2026). **Descrittivo**: la forma oraria da 3 ore prima a 12 dopo, e la versione contraria.
* Una prova a eventi: nel conto **168**, le prove a eventi **27**.

## 3. L'esame

Come la prova 96: media sopra zero con p ≤ 0,01 e positiva nelle due metà (2021-2023, 2024-2026); contando le 27 prove a eventi la soglia è
0,00037. Si riporta la quota di gruppi di giorni a caso che fanno almeno come le pubblicazioni.
