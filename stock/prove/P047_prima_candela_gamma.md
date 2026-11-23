# Prova 47 — la prima candela da 15 minuti sullo SPY, solo nei giorni con la copertura delle opzioni sotto zero

Regole scritte il 23 novembre 2026 **prima di qualsiasi calcolo** (idea I55 di `REGISTRO.md`). Si conoscevano la prova 17 (la stessa regola
in tutti i giorni: SPY 15 minuti Sharpe con i costi −0,48, bocciata), la prova 45 e la sua revisione (la copertura delle opzioni sotto
zero separa i giorni in cui l'ultima mezz'ora segue la giornata: +7,58 punti base a operazione contro +0,05 negli altri giorni) e la 45b
(nel periodo chiuso la direzione tiene, ma i casi sono 18). Nessun rendimento della prima candela per i giorni con la copertura sotto zero
è stato guardato. Contano come **2 prove** (la strategia da sola, e la miscela con lei).

## Perché dovrebbe funzionare

Baltussen, Da, Lammers e Martens (Journal of Financial Economics 142, 2021): quando chi vende opzioni ha una copertura negativa, deve
comprare mentre il prezzo sale e vendere mentre scende **per tutta la giornata**, non solo alla fine: il movimento iniziale tende a
continuare. La prova 17 mescolava tutti i giorni (in quelli con la copertura positiva chi vende opzioni fa il contrario e frena il
movimento). Qui la regola resta identica e si guardano **solo i giorni con la copertura sotto zero**. È anche la regola che il demo usa
sulle 10 azioni più scambiate (`avanti/REGOLE.md`): se il filtro funziona sullo SPY, è un candidato per migliorare il demo.

**Sospetti scritti prima:** gli stessi della prova 45 (il dato è una stima privata controllabile solo dal novembre 2021; pochi giorni,
concentrati in tre periodi; marzo 2020 può fare il risultato); in più, nei giorni agitati la candela è larga e lo stop lontano, e la prova
17 sullo SPY a 15 minuti era la peggiore delle quattro.

## La regola, i dati e i costi

**Identici alla prova 17** (`P017_prima_candela.md`), solo SPY e candela da **15 minuti**: direzione della candela dalle 9:30 alle 9:44,
ingresso a mercato alle 9:45 con il 98% del conto, stop all'altro estremo della candela, obiettivo 10 volte il rischio, uscita a mercato
all'ultima barra della seduta; stessi giorni esclusi; stessi costi (metà dello scarto misurato, 0,5 punti base di slittamento,
Interactive Brokers «fisso», costi doppi). **Unica differenza:** si opera solo se la copertura di SqueezeMetrics con la data del giorno
di borsa prima è **sotto zero** (come la prova 45); gli altri giorni sono esclusi. Periodo 2016-2024. Il periodo chiuso di questa
famiglia (regole che seguono il movimento dell'apertura) è già stato usato dalla prova 2: **se passa, la conferma è solo il demo**.

## L'esame (uguale alle prove 28 e 30-46)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela:** Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto
0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t
dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi di 20 giorni. **E, per la
lezione della prova 45, senza marzo 2020 il t della parte resta almeno 1,3** (condizione aggiunta qui, prima del calcolo).

Da leggere accanto: quante operazioni e come escono (stop, obiettivo, chiusura); **la stessa regola nei giorni con la copertura sopra o
uguale a zero**; l'anno per anno.
